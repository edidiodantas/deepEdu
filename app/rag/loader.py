from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader, TextLoader


def load_materials(materials_dir: str):
    docs = []
    path = Path(materials_dir)
    path.mkdir(parents=True, exist_ok=True)

    for file in path.rglob("*"):
        suffix = file.suffix.lower()
        if suffix == ".pdf":
            docs.extend(PyPDFLoader(str(file)).load())
        elif suffix in {".txt", ".md"}:
            docs.extend(TextLoader(str(file), encoding="utf-8").load())

    for doc in docs:
        doc.metadata["source_file"] = doc.metadata.get("source", "unknown")
    return docs
