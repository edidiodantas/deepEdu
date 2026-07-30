#!/usr/bin/env python3
"""Avaliação RAG offline — RF38 / RNF15."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def load_dataset(path: Path) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        for row in reader:
            if row.get("ativo", "").lower() != "true":
                continue
            if not row.get("pergunta", "").strip():
                continue
            rows.append(row)
    return rows


def evaluate_row(row: dict) -> dict:
    from app.rag.abstinence import evaluate_retrieval, should_abstain

    question = row["pergunta"]
    gate = evaluate_retrieval(question)
    abstained = gate.abstain
    has_docs = len(gate.docs) > 0
    citation_ok = has_docs and not abstained
    return {
        "id": row["id"],
        "abstained": abstained,
        "max_score": gate.max_score,
        "chunks": len(gate.docs),
        "citation_expected": row.get("requer_citacao", "").lower() == "true",
        "citation_ok": citation_ok if row.get("requer_citacao", "").lower() == "true" else None,
        "calc_expected": row.get("requer_calculo", "").lower() == "true",
        "policy_ok": should_abstain(max_score=gate.max_score, doc_count=len(gate.docs)) == abstained,
    }


def summarize(results: list[dict]) -> dict:
    n = len(results) or 1
    abstentions = sum(1 for r in results if r["abstained"])
    citations = [r for r in results if r["citation_ok"] is not None]
    citation_hits = sum(1 for r in citations if r["citation_ok"])
    return {
        "total": len(results),
        "abstention_rate": round(abstentions / n, 3),
        "citation_accuracy": round(citation_hits / (len(citations) or 1), 3),
        "policy_consistency": round(sum(1 for r in results if r["policy_ok"]) / n, 3),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Avaliação RAG deepEdu")
    parser.add_argument(
        "--dataset",
        default=str(ROOT / "docs/eval/dataset_rag_matematica_em.csv"),
    )
    parser.add_argument("--output", default=str(ROOT / "reports/eval_latest.json"))
    args = parser.parse_args()

    dataset_path = Path(args.dataset)
    rows = load_dataset(dataset_path)
    if not rows:
        print("Nenhuma pergunta ativa no dataset.", file=sys.stderr)
        return 1

    results = [evaluate_row(row) for row in rows]
    summary = summarize(results)
    payload = {"summary": summary, "results": results}

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"→ {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
