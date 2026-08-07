from langchain.retrievers import EnsembleRetriever
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings
from app.rag.constants import COLLECTION_NAME
from app.rag.indexer import load_indexed_documents
from app.rag.loader import load_materials


def build_hybrid_retriever():
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vectordb = Chroma(
        collection_name=COLLECTION_NAME,
        persist_directory=settings.CHROMA_DIR,
        embedding_function=embeddings,
    )
    vector_retriever = vectordb.as_retriever(search_kwargs={"k": max(settings.RETRIEVAL_TOP_K, 10)})

    # BM25 nos mesmos chunks do Chroma (evita granularidade documento inteiro vs chunk).
    chunk_docs = load_indexed_documents()
    if not chunk_docs:
        chunk_docs = load_materials(settings.MATERIALS_DIR)
    if not chunk_docs:
        raise ValueError(
            "Nenhum material indexado. Adicione arquivos em data/materials "
            "e execute scripts/run_indexing.py."
        )
    bm25 = BM25Retriever.from_documents(chunk_docs)
    bm25.k = max(settings.RETRIEVAL_TOP_K, 10)

    return EnsembleRetriever(
        retrievers=[bm25, vector_retriever],
        weights=[0.35, 0.65],
    )
