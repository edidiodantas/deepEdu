from __future__ import annotations

import warnings
from functools import lru_cache

from langchain_core.documents import Document

from app.core.config import settings

_MONO_T5_MARKERS = ("monoptt5", "monot5", "ptt5")
_BATCH = 2
_MAX_TOKENS = 512


def _is_mono_t5(model_id: str) -> bool:
    name = model_id.lower()
    return any(marker in name for marker in _MONO_T5_MARKERS)


def _token_id(tokenizer, *names: str) -> int:
    vocab = tokenizer.get_vocab()
    for name in names:
        if name in vocab:
            return int(vocab[name])
    encoded = tokenizer.encode(names[-1], add_special_tokens=False)
    if len(encoded) == 1:
        return int(encoded[0])
    raise RuntimeError(f"Tokenizer sem token de relevancia: {names}")


@lru_cache(maxsize=1)
def _cross_encoder():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(settings.RERANK_MODEL)


@lru_cache(maxsize=1)
def _mono_t5():
    import torch
    from transformers import AutoModelForSeq2SeqLM, AutoTokenizer

    model_id = settings.RERANK_MODEL
    tokenizer = AutoTokenizer.from_pretrained(model_id)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.bfloat16
    model = AutoModelForSeq2SeqLM.from_pretrained(model_id, torch_dtype=dtype)
    model.to(device)
    model.eval()
    true_id = _token_id(tokenizer, "▁true", "true")
    false_id = _token_id(tokenizer, "▁false", "false")
    return tokenizer, model, true_id, false_id, device


def _mono_t5_log_odds(query: str, docs: list[Document]) -> list[float]:
    """Diferença true−false. O sigmoid disso é a probabilidade de 'relevante'."""
    import torch

    tokenizer, model, true_id, false_id, device = _mono_t5()
    scores: list[float] = []
    start = model.config.decoder_start_token_id
    for offset in range(0, len(docs), _BATCH):
        chunk = docs[offset : offset + _BATCH]
        texts = [
            f"Query: {query} Document: {doc.page_content} Relevant:" for doc in chunk
        ]
        encoded = tokenizer(
            texts,
            return_tensors="pt",
            padding=True,
            truncation=True,
            max_length=_MAX_TOKENS,
        )
        encoded = {key: value.to(device) for key, value in encoded.items()}
        decoder_input_ids = torch.full(
            (len(chunk), 1),
            start,
            dtype=torch.long,
            device=device,
        )
        with torch.inference_mode():
            logits = model(
                input_ids=encoded["input_ids"],
                attention_mask=encoded["attention_mask"],
                decoder_input_ids=decoder_input_ids,
            ).logits[:, 0, :]
        log_odds = logits[:, true_id] - logits[:, false_id]
        scores.extend(float(value) for value in log_odds.detach().cpu())
    return scores


def rerank_documents(query: str, docs: list[Document], top_k: int | None = None) -> list[Document]:
    """Reordena os trechos recuperados. Padrão: monoPTT5 (português)."""
    if not docs:
        return []
    limit = top_k or settings.RETRIEVAL_TOP_K
    if not settings.RERANK_ENABLED:
        return docs[:limit]

    try:
        if _is_mono_t5(settings.RERANK_MODEL):
            scores = _mono_t5_log_odds(query, docs)
        else:
            model = _cross_encoder()
            pairs = [(query, doc.page_content) for doc in docs]
            scores = [float(score) for score in model.predict(pairs)]
        ranked = sorted(zip(docs, scores), key=lambda item: item[1], reverse=True)
        result: list[Document] = []
        for doc, score in ranked[:limit]:
            doc.metadata["rerank_score"] = float(score)
            doc.metadata["rerank_model"] = settings.RERANK_MODEL
            doc.metadata["score"] = float(score)
            result.append(doc)
        return result
    except Exception as exc:
        warnings.warn(
            f"Reranker indisponivel ({settings.RERANK_MODEL}): {exc}",
            stacklevel=2,
        )
        return docs[:limit]
