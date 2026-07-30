from pathlib import Path

from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.audit.service import log_event
from app.core.config import settings
from app.rag.loader import load_materials


def build_index(correlation_id: str = "index-job"):
    docs = load_materials(settings.MATERIALS_DIR)
    if not docs:
        raise ValueError("Nenhum material encontrado em data/materials")

    for doc in docs:
        source = doc.metadata.get("source", "unknown")
        log_event(
            correlation_id=correlation_id,
            actor_type="system",
            actor_id="indexer",
            session_id="indexer",
            action="corpus.document_added",
            resource=str(source),
            outcome="success",
            metadata={"chars": len(doc.page_content)},
        )

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_CHILD_TOKENS * 4,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)

    Path(settings.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.CHROMA_DIR,
        collection_name="deepedu_materials",
    )
    vectordb.persist()

    log_event(
        correlation_id=correlation_id,
        actor_type="system",
        actor_id="indexer",
        session_id="indexer",
        action="index.rebuilt",
        resource=settings.CHROMA_DIR,
        outcome="success",
        metadata={"chunks": len(chunks), "documents": len(docs)},
    )
    return len(chunks)
