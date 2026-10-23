"""Resumo dos trechos do material usados numa resposta (mostrado ao administrador)."""

import os


def source_summary(docs) -> list[dict]:
    """Trechos usados na resposta, para o administrador conferir de onde ela veio."""
    sources = []
    for doc in docs:
        meta = doc.metadata or {}
        path = meta.get("source_file") or meta.get("source") or "?"
        page = meta.get("page")
        snippet = " ".join((doc.page_content or "").split())
        sources.append(
            {
                "file": os.path.basename(str(path)),
                # PyMuPDF/PyPDF numeram a partir de 0; a pessoa lê a partir de 1.
                "page": int(page) + 1 if isinstance(page, (int, float)) else None,
                "score": round(float(meta.get("gate_score", meta.get("score", 0.0)) or 0.0), 3),
                "chunk_id": meta.get("chunk_id"),
                "snippet": snippet[:280] + ("…" if len(snippet) > 280 else ""),
            }
        )
    return sources
