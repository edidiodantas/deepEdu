from pathlib import Path

from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from app.audit.service import log_event
from app.core.config import settings
from app.rag.loader import load_materials
from app.rag.constants import COLLECTION_NAME


def _clear_collection(persist_directory: str, collection_name: str) -> None:
    """Remove a coleção existente para evitar chunks duplicados na reindexação."""
    Path(persist_directory).mkdir(parents=True, exist_ok=True)
    try:
        import chromadb

        client = chromadb.PersistentClient(path=persist_directory)
        client.delete_collection(collection_name)
    except Exception:
        # Coleção inexistente ou API antiga — segue com from_documents.
        pass


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

    # CHUNK_CHILD_TOKENS ≈ tokens; splitter usa caracteres (~4 chars/token).
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=settings.CHUNK_CHILD_TOKENS * 4,
        chunk_overlap=80,
        separators=["\n\n", "\n", ". ", " ", ""],
    )
    chunks = splitter.split_documents(docs)
    for i, chunk in enumerate(chunks):
        source = chunk.metadata.get("source_file") or chunk.metadata.get("source") or "unknown"
        page = chunk.metadata.get("page", "")
        chunk.metadata["chunk_id"] = f"{source}:{page}:{i}"

    Path(settings.CHROMA_DIR).mkdir(parents=True, exist_ok=True)
    _clear_collection(settings.CHROMA_DIR, COLLECTION_NAME)

    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vectordb = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=settings.CHROMA_DIR,
        collection_name=COLLECTION_NAME,
        collection_metadata={"hnsw:space": "cosine"},
    )
    try:
        vectordb.persist()
    except Exception:
        pass

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


def load_indexed_documents() -> list[Document]:
    """Carrega chunks já indexados (para BM25 alinhado ao Chroma)."""
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=settings.CHROMA_DIR,
        embedding_function=embeddings,
    )
    raw = vectordb.get(include=["documents", "metadatas"])
    documents = raw.get("documents") or []
    metadatas = raw.get("metadatas") or []
    docs: list[Document] = []
    for content, meta in zip(documents, metadatas):
        if not content:
            continue
        docs.append(Document(page_content=content, metadata=meta or {}))
    return docs
