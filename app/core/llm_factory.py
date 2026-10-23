from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings
from app.core.hardware import (
    _llm_dtype,  # noqa: F401  (reexportado para testes/uso externo)
    cpu_placement,
    plan_llm_placement,
    record_runtime,
)

# Modelo oficial DeepEdu: Amadeus-Verbo 0,5B (PT-BR, família Qwen2.5).
DEFAULT_HF_MODEL = "amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct"


def _cache_key() -> tuple:
    """Chave estável para não recarregar o modelo a cada pergunta."""
    return (
        settings.LLM_PROVIDER.strip().lower(),
        (settings.LLM_MODEL or DEFAULT_HF_MODEL).strip(),
        settings.LLM_DEVICE_MAP,
        settings.LLM_TEMPERATURE,
        settings.LLM_MAX_NEW_TOKENS,
        settings.OLLAMA_BASE_URL,
        settings.LLM_API_KEY or settings.DEEPSEEK_API_KEY,
        settings.LLM_BASE_URL or settings.DEEPSEEK_BASE_URL,
        settings.LLM_DTYPE,
    )


def _smoke_test(pipe) -> None:
    pipe("Olá", max_new_tokens=1, do_sample=False)


def _free_gpu_memory() -> None:
    import gc

    import torch

    gc.collect()
    if torch.cuda.is_available():
        torch.cuda.empty_cache()


@lru_cache(maxsize=4)
def _build_chat_model_cached(cache_key: tuple) -> BaseChatModel:
    provider = cache_key[0]

    if provider == "huggingface":
        from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        model_id = cache_key[1]
        tokenizer = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
        if tokenizer.pad_token is None:
            tokenizer.pad_token = tokenizer.eos_token

        temperature = float(cache_key[3])
        max_new = int(cache_key[4])

        def _load(placement):
            import torch

            model = AutoModelForCausalLM.from_pretrained(
                model_id,
                device_map=placement.device_map,
                torch_dtype=getattr(torch, placement.dtype_name),
                trust_remote_code=True,
            )
            return pipeline(
                "text-generation",
                model=model,
                tokenizer=tokenizer,
                max_new_tokens=max_new,
                temperature=max(temperature, 1e-5),
                do_sample=temperature > 0,
                return_full_text=False,
                pad_token_id=tokenizer.pad_token_id,
            )

        placement = plan_llm_placement(cache_key[2], cache_key[8])
        pipe = _load(placement)
        if placement.device_map != "cpu":
            # Gera 1 token já no carregamento: erros de GPU (tipo numérico não
            # suportado, falta de memória, driver) aparecem aqui, não na pergunta.
            try:
                _smoke_test(pipe)
            except Exception as exc:
                reason = f"{placement.device_label} falhou no teste ({type(exc).__name__}: {str(exc)[:160]})"
                del pipe
                _free_gpu_memory()
                placement = cpu_placement(reason, cache_key[8])
                pipe = _load(placement)
        record_runtime(placement)

        # Sem model_id/tokenizer explícitos o ChatHuggingFace cai no padrão "gpt2"
        # e aplica o chat template errado (ou falha) em vez do Amadeus/Qwen2.5.
        return ChatHuggingFace(
            llm=HuggingFacePipeline(pipeline=pipe, model_id=model_id),
            model_id=model_id,
            tokenizer=tokenizer,
        )

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=cache_key[1],
            temperature=float(cache_key[3]),
            num_predict=int(cache_key[4]),
            base_url=cache_key[5],
        )

    if provider == "openai_compatible":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=cache_key[1] or settings.DEEPSEEK_MODEL,
            api_key=cache_key[6] or settings.DEEPSEEK_API_KEY,
            base_url=cache_key[7] or settings.DEEPSEEK_BASE_URL,
            temperature=float(cache_key[3]),
            max_tokens=int(cache_key[4]),
        )

    raise ValueError(f"LLM_PROVIDER invalido: {provider}")


def build_chat_model() -> BaseChatModel:
    """Retorna o LLM (cacheado — Amadeus HF não é recarregado a cada pergunta)."""
    return _build_chat_model_cached(_cache_key())


def clear_chat_model_cache() -> None:
    """Útil em testes ou após mudar o .env em runtime."""
    _build_chat_model_cached.cache_clear()
