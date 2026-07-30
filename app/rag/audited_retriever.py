from __future__ import annotations

from typing import Any

from pydantic import ConfigDict
from langchain_core.callbacks import CallbackManagerForRetrieverRun
from langchain_core.documents import Document
from langchain_core.retrievers import BaseRetriever

from app.audit.service import log_event
from app.core.config import settings


class AuditedRetriever(BaseRetriever):
    base_retriever: BaseRetriever
    correlation_id: str | None = None
    actor_id: str = "system"
    session_id: str = "system"

    model_config = ConfigDict(arbitrary_types_allowed=True)

    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: CallbackManagerForRetrieverRun | None = None,
    ) -> list[Document]:
        docs = self.base_retriever.invoke(query)
        top_k = min(settings.RETRIEVAL_TOP_K, len(docs))
        docs = docs[:top_k]
        metadata: dict[str, Any] = {
            "top_k": top_k,
            "scores": [doc.metadata.get("score") for doc in docs],
            "chunk_ids": [doc.metadata.get("chunk_id", doc.metadata.get("source")) for doc in docs],
        }
        if self.correlation_id:
            log_event(
                correlation_id=self.correlation_id,
                actor_type="student",
                actor_id=self.actor_id,
                session_id=self.session_id,
                action="retrieval.executed",
                resource="retriever",
                outcome="success",
                metadata=metadata,
            )
        return docs
