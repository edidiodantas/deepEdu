from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader
from langchain_core.documents import Document


def _load_pdf(file: Path) -> list[Document]:
    """Prefere PyMuPDF (fórmulas/layout); cai para PyPDF se o pacote faltar."""
    try:
        from langchain_community.document_loaders import PyMuPDFLoader

        return PyMuPDFLoader(str(file)).load()
    except ImportError:
        return PyPDFLoader(str(file)).load()


def load_materials(materials_dir: str):
    docs = []
    path = Path(materials_dir)
    path.mkdir(parents=True, exist_ok=True)

    for file in path.rglob("*"):
        suffix = file.suffix.lower()
        if suffix == ".pdf":
            docs.extend(_load_pdf(file))
        elif suffix in {".txt", ".md"}:
            docs.extend(TextLoader(str(file), encoding="utf-8").load())

    for doc in docs:
        doc.metadata["source_file"] = doc.metadata.get("source", "unknown")
    return docs
