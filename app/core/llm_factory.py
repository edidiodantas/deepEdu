from langchain_core.language_models.chat_models import BaseChatModel

from app.core.config import settings


def build_chat_model() -> BaseChatModel:
    provider = settings.LLM_PROVIDER.strip().lower()

    if provider == "ollama":
        from langchain_ollama import ChatOllama

        return ChatOllama(
            model=settings.LLM_MODEL,
            temperature=settings.LLM_TEMPERATURE,
            num_predict=settings.LLM_MAX_NEW_TOKENS,
            base_url=settings.OLLAMA_BASE_URL,
        )

    if provider == "huggingface":
        from langchain_huggingface import ChatHuggingFace, HuggingFacePipeline
        from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline

        tokenizer = AutoTokenizer.from_pretrained(settings.LLM_MODEL)
        model = AutoModelForCausalLM.from_pretrained(
            settings.LLM_MODEL,
            device_map=settings.LLM_DEVICE_MAP,
            torch_dtype="auto",
        )
        pipe = pipeline(
            "text-generation",
            model=model,
            tokenizer=tokenizer,
            max_new_tokens=settings.LLM_MAX_NEW_TOKENS,
            temperature=settings.LLM_TEMPERATURE,
        )
        return ChatHuggingFace(llm=HuggingFacePipeline(pipeline=pipe))

    if provider == "openai_compatible":
        from langchain_openai import ChatOpenAI

        return ChatOpenAI(
            model=settings.LLM_MODEL or settings.DEEPSEEK_MODEL,
            api_key=settings.LLM_API_KEY or settings.DEEPSEEK_API_KEY,
            base_url=settings.LLM_BASE_URL or settings.DEEPSEEK_BASE_URL,
            temperature=settings.LLM_TEMPERATURE,
            max_tokens=settings.LLM_MAX_NEW_TOKENS,
        )

    raise ValueError(f"LLM_PROVIDER invalido: {provider}")
