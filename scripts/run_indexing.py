from app.rag.indexer import build_index


if __name__ == "__main__":
    total = build_index()
    print(f"Indexacao concluida. Chunks criados: {total}")
