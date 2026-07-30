from langchain.retrievers import EnsembleRetriever
from langchain_chroma import Chroma
from langchain_community.retrievers import BM25Retriever
from langchain_huggingface import HuggingFaceEmbeddings

from app.core.config import settings
from app.rag.loader import load_materials


def build_hybrid_retriever():
    embeddings = HuggingFaceEmbeddings(model_name=settings.EMBEDDING_MODEL)
    vectordb = Chroma(
        collection_name="deepedu_materials",
        persist_directory=settings.CHROMA_DIR,
        embedding_function=embeddings,
    )
    vector_retriever = vectordb.as_retriever(search_kwargs={"k": settings.RETRIEVAL_TOP_K})

    raw_docs = load_materials(settings.MATERIALS_DIR)
    if not raw_docs:
        raise ValueError(
            "Nenhum material carregado em data/materials. "
            "Adicione arquivos e execute scripts/run_indexing.py."
        )
    bm25 = BM25Retriever.from_documents(raw_docs)
    bm25.k = settings.RETRIEVAL_TOP_K

    return EnsembleRetriever(
        retrievers=[bm25, vector_retriever],
        weights=[0.35, 0.65],
    )
