from __future__ import annotations

from functools import lru_cache

from langchain_core.documents import Document

from app.core.config import settings


@lru_cache(maxsize=1)
def _cross_encoder():
    from sentence_transformers import CrossEncoder

    return CrossEncoder(settings.RERANK_MODEL)


def rerank_documents(query: str, docs: list[Document], top_k: int | None = None) -> list[Document]:
    """Re-ranking cross-encoder pós-recuperação (RF26)."""
    if not docs:
        return []
    limit = top_k or settings.RETRIEVAL_TOP_K
    if not settings.RERANK_ENABLED:
        return docs[:limit]

    try:
        model = _cross_encoder()
        pairs = [(query, doc.page_content) for doc in docs]
        scores = model.predict(pairs)
        ranked = sorted(zip(docs, scores), key=lambda item: float(item[1]), reverse=True)
        result: list[Document] = []
        for doc, score in ranked[:limit]:
            doc.metadata["rerank_score"] = float(score)
            doc.metadata["score"] = float(score)
            result.append(doc)
        return result
    except Exception:
        return docs[:limit]
