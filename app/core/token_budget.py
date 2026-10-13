from __future__ import annotations

from functools import lru_cache

from app.core.config import settings


# Tags Ollama (legado) → ids HuggingFace do tokenizer.
_OLLAMA_TO_HF_TOKENIZER = {
    "qwen2.5-math:1.5b-instruct": "Qwen/Qwen2.5-Math-1.5B-Instruct",
    "qwen2.5-math:7b-instruct": "Qwen/Qwen2.5-Math-7B-Instruct",
    "qwen2.5:1.5b": "Qwen/Qwen2.5-1.5B",
    "qwen2.5:3b": "Qwen/Qwen2.5-3B",
    "qwen2.5:7b": "Qwen/Qwen2.5-7B",
}

_DEFAULT_AMADEUS = "amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct"


def _tokenizer_model_id() -> str:
    explicit = (settings.LLM_TOKENIZER_ID or "").strip()
    if explicit:
        return explicit
    model = (settings.LLM_MODEL or _DEFAULT_AMADEUS).strip()
    return _OLLAMA_TO_HF_TOKENIZER.get(model, model)


@lru_cache(maxsize=1)
def _tokenizer():
    try:
        from transformers import AutoTokenizer

        return AutoTokenizer.from_pretrained(_tokenizer_model_id(), trust_remote_code=True)
    except Exception:
        return None


def count_tokens(text: str) -> int:
    tokenizer = _tokenizer()
    if tokenizer is None:
        return max(1, len(text) // 4)
    return len(tokenizer.encode(text, add_special_tokens=False))


def truncate_to_tokens(text: str, max_tokens: int) -> str:
    if max_tokens <= 0:
        return ""
    tokenizer = _tokenizer()
    if tokenizer is None:
        return text[: max_tokens * 4]
    tokens = tokenizer.encode(text, add_special_tokens=False)
    if len(tokens) <= max_tokens:
        return text
    return tokenizer.decode(tokens[:max_tokens], skip_special_tokens=True)


def trim_context_chunks(chunks: list[str], max_tokens: int) -> list[str]:
    if not chunks:
        return []
    per_chunk = max(80, max_tokens // max(1, len(chunks)))
    trimmed = [truncate_to_tokens(chunk, per_chunk) for chunk in chunks]
    total = sum(count_tokens(c) for c in trimmed)
    while total > max_tokens and len(trimmed) > 1:
        trimmed.pop()
        total = sum(count_tokens(c) for c in trimmed)
    return trimmed


def format_rag_context(docs: list, max_tokens: int | None = None) -> str:
    limit = max_tokens or settings.RAG_CONTEXT_MAX_TOKENS
    top_k = min(settings.RETRIEVAL_TOP_K, len(docs))
    parts: list[str] = []
    for doc in docs[:top_k]:
        meta = getattr(doc, "metadata", {}) or {}
        source = meta.get("source_file") or meta.get("source") or "acervo"
        page = meta.get("page")
        header = f"Fonte: {source}" + (f", p.{page}" if page not in (None, "") else "")
        parts.append(f"{header}\n{doc.page_content}")
    parts = trim_context_chunks(parts, limit)
    return "\n\n---\n\n".join(parts)
