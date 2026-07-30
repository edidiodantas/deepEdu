from __future__ import annotations

from dataclasses import dataclass

from langchain_core.documents import Document

from app.audit.service import log_event
from app.core.config import settings

ABSTINENCE_MESSAGE = (
    "Nao encontrei material suficiente no acervo para responder com seguranca. "
    "Tente reformular a pergunta (seja mais especifica sobre o tema de Matematica) "
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


def _vector_max_score(query: str) -> float:
    from langchain_chroma import Chroma
    from langchain_huggingface import HuggingFaceEmbeddings

    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vectordb = Chroma(
        collection_name="deepedu_materials",
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
    return max(0.0, 1.0 - float(distance))


def evaluate_retrieval(
    query: str,
    *,
    correlation_id: str | None = None,
    actor_id: str = "system",
    session_id: str = "system",
) -> RetrievalGateResult:
    from app.rag.retriever import build_hybrid_retriever

    retriever = build_hybrid_retriever()
    docs = retriever.invoke(query)
    from app.rag.reranker import rerank_documents

    docs = rerank_documents(query, docs, top_k=settings.RETRIEVAL_TOP_K)
    top_k = min(settings.RETRIEVAL_TOP_K, len(docs))
    docs = docs[:top_k]
    max_score = max((float(doc.metadata.get("rerank_score", doc.metadata.get("score", 0))) for doc in docs), default=0.0)
    if max_score == 0.0:
        max_score = _vector_max_score(query)
    for doc in docs:
        doc.metadata.setdefault("score", max_score)

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
                "chunk_ids": [
                    doc.metadata.get("chunk_id", doc.metadata.get("source")) for doc in docs
                ],
            },
        )
    return RetrievalGateResult(abstain=abstain, max_score=max_score, docs=docs)
