from __future__ import annotations

from functools import lru_cache

from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings

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
    )


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

        model = AutoModelForCausalLM.from_pretrained(
            model_id,
            device_map=cache_key[2],
            torch_dtype="auto",
            trust_remote_code=True,
        )
        temperature = float(cache_key[3])
        max_new = int(cache_key[4])
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=max_new,
            temperature=max(temperature, 1e-5),
            do_sample=temperature > 0,
            return_full_text=False,
            pad_token_id=tokenizer.pad_token_id,
        )
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
