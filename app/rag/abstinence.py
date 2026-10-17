from __future__ import annotations

import math
from dataclasses import dataclass

from langchain_core.documents import Document

from app.audit.service import log_event
from app.core.config import settings
from app.rag.constants import COLLECTION_NAME

ABSTINENCE_MESSAGE = (
    "Não encontrei material suficiente no acervo para responder com segurança. "
    "Tente reformular a pergunta (seja mais específica sobre o tema de Matemática) "
    "ou consulte seu professor."
)


@dataclass
class RetrievalGateResult:
    abstain: bool
    max_score: float
    docs: list[Document]
    message: str = ABSTINENCE_MESSAGE


def should_abstain(*, max_score: float, doc_count: int, min_score: float | None = None) -> bool:
    threshold = min_score if min_score is not None else settings.RETRIEVAL_MIN_SCORE
    return doc_count == 0 or max_score < threshold


def _sigmoid(value: float) -> float:
    # Estável numericamente para logits do cross-encoder.
    if value >= 0:
        z = math.exp(-value)
        return 1.0 / (1.0 + z)
    z = math.exp(value)
    return z / (1.0 + z)


def _distance_to_similarity(distance: float) -> float:
    """Converte distância Chroma (cosine/L2) para similaridade em [0, 1]."""
    d = float(distance)
    if d < 0:
        return 1.0
    # Cosine distance no Chroma costuma ser 1 - cos_sim ∈ [0, 2].
    if d <= 2.0:
        return max(0.0, min(1.0, 1.0 - d))
    # L2 / outras métricas: mapeamento monotônico para (0, 1].
    return 1.0 / (1.0 + d)


def _normalize_doc_score(doc: Document) -> float:
    if "rerank_score" in doc.metadata:
        return _sigmoid(float(doc.metadata["rerank_score"]))
    if "vector_score" in doc.metadata:
        return float(doc.metadata["vector_score"])
    if "score" in doc.metadata:
        raw = float(doc.metadata["score"])
        # Scores já em [0, 1] mantêm; logits (|x| > 1 tipicamente) passam por sigmoid.
        if 0.0 <= raw <= 1.0:
            return raw
        return _sigmoid(raw)
    return 0.0


def _vector_max_score(query: str) -> float:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=settings.CHROMA_DIR,
        embedding_function=embeddings,
    )
    try:
        count = vectordb._collection.count()
    except Exception:
        count = 0
    if count == 0:
        return 0.0
    results = vectordb.similarity_search_with_score(query, k=1)
    if not results:
        return 0.0
    _, distance = results[0]
    return _distance_to_similarity(distance)


def evaluate_retrieval(
    query: str,
    *,
    correlation_id: str | None = None,
    actor_id: str = "system",
    session_id: str = "system",
) -> RetrievalGateResult:
    from app.rag.retriever import build_hybrid_retriever
    from app.rag.reranker import rerank_documents

    retriever = build_hybrid_retriever()
    docs = retriever.invoke(query)
    docs = rerank_documents(query, docs, top_k=settings.RETRIEVAL_TOP_K)
    top_k = min(settings.RETRIEVAL_TOP_K, len(docs))
    docs = docs[:top_k]

    scores = [_normalize_doc_score(doc) for doc in docs]
    max_score = max(scores) if scores else 0.0
    if max_score == 0.0 and docs:
        max_score = _vector_max_score(query)

    for doc, score in zip(docs, scores):
        doc.metadata["score"] = score if score > 0 else max_score
        doc.metadata["gate_score"] = doc.metadata["score"]

    abstain = should_abstain(max_score=max_score, doc_count=len(docs))
    if correlation_id:
        log_event(
            correlation_id=correlation_id,
            actor_type="student",
            actor_id=actor_id,
            session_id=session_id,
            action="retrieval.executed",
            resource="retriever",
            outcome="abstained" if abstain else "success",
            metadata={
                "top_k": top_k,
                "max_score": max_score,
                "min_score": settings.RETRIEVAL_MIN_SCORE,
                "abstained": abstain,
                "rerank_model": settings.RERANK_MODEL if settings.RERANK_ENABLED else "",
                "chunk_ids": [
                    doc.metadata.get("chunk_id", doc.metadata.get("source")) for doc in docs
                ],
            },
        )
    return RetrievalGateResult(abstain=abstain, max_score=max_score, docs=docs)
