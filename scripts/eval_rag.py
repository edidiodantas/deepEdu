#!/usr/bin/env python3
"""Avaliação RAG offline — RF38 / RNF15.

Roda as perguntas de docs/eval/dataset_rag_matematica_em.csv contra a base indexada
e gera dois relatórios em reports/: um JSON com todos os resultados e um Markdown
com o resumo, pronto para ser citado na dissertação.

Uso (no computador onde o DeepEdu está instalado e os materiais estão indexados):

    python scripts/eval_rag.py               # só recuperação (rápido)
    python scripts/eval_rag.py --com-llm     # recuperação + resposta completa do tutor

Métricas:
- taxa de abstenção: perguntas em que o sistema se recusou a responder;
- acerto da fonte: o documento esperado está entre os trechos recuperados;
- consistência da política: a decisão de abstenção segue o limiar configurado;
- (com --com-llm) acerto dos cálculos conferido pelo SymPy, respostas bloqueadas
  pela validação de saída e tempo médio de resposta.
"""

from __future__ import annotations

import argparse
import csv
import json
import os
import sys
import time
from datetime import datetime, timezone
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


def _flag(row: dict, key: str) -> bool:
    return (row.get(key) or "").strip().lower() == "true"


def source_hit(expected_document: str, docs) -> bool | None:
    """Verdadeiro se o documento esperado está entre os trechos recuperados."""
    expected = os.path.basename((expected_document or "").strip()).lower()
    if not expected:
        return None
    found = {
        os.path.basename(str((d.metadata or {}).get("source_file") or (d.metadata or {}).get("source") or "")).lower()
        for d in docs
    }
    return expected in found


def evaluate_row(row: dict, *, with_llm: bool = False) -> dict:
    from app.rag.abstinence import evaluate_retrieval, should_abstain

    question = row["pergunta"]
    gate = evaluate_retrieval(question)
    abstained = gate.abstain
    result = {
        "id": row["id"],
        "abstained": abstained,
        "max_score": round(gate.max_score, 3),
        "chunks": len(gate.docs),
        "source_hit": source_hit(row.get("documento_esperado", ""), gate.docs),
        "calc_expected": _flag(row, "requer_calculo"),
        "policy_ok": should_abstain(max_score=gate.max_score, doc_count=len(gate.docs)) == abstained,
    }
    if with_llm:
        from app.rag.sympy_tool import verify_numeric_answer
        from app.services.tutor_service import answer_question_detailed

        start = time.perf_counter()
        answer = answer_question_detailed("avaliacao-automatica", question, correlation_id=f"eval-{row['id']}")
        result["latency_s"] = round(time.perf_counter() - start, 2)
        result["blocked"] = bool(answer.get("blocked"))
        result["answer_abstained"] = bool(answer.get("abstained"))
        if result["calc_expected"] and not result["blocked"] and not result["answer_abstained"]:
            result["calc_ok"] = verify_numeric_answer(question, answer.get("answer", "")).get("verified") is True
        else:
            result["calc_ok"] = None
    return result


def _ratio(hits: int, total: int) -> float | None:
    return round(hits / total, 3) if total else None


def summarize(results: list[dict]) -> dict:
    n = len(results)
    with_source = [r for r in results if r.get("source_hit") is not None]
    summary = {
        "total": n,
        "abstention_rate": _ratio(sum(1 for r in results if r["abstained"]), n),
        "source_accuracy": _ratio(sum(1 for r in with_source if r["source_hit"]), len(with_source)),
        "source_evaluated": len(with_source),
        "policy_consistency": _ratio(sum(1 for r in results if r["policy_ok"]), n),
        "mean_max_score": round(sum(r["max_score"] for r in results) / n, 3) if n else None,
    }
    if any("latency_s" in r for r in results):
        calc = [r for r in results if r.get("calc_ok") is not None]
        latencies = [r["latency_s"] for r in results if "latency_s" in r]
        summary.update(
            {
                "calc_accuracy": _ratio(sum(1 for r in calc if r["calc_ok"]), len(calc)),
                "calc_evaluated": len(calc),
                "blocked_rate": _ratio(sum(1 for r in results if r.get("blocked")), n),
                "mean_latency_s": round(sum(latencies) / len(latencies), 2) if latencies else None,
            }
        )
    return summary


def _pct(value) -> str:
    return "—" if value is None else f"{value * 100:.1f}%".replace(".", ",")


def render_markdown(summary: dict, meta: dict) -> str:
    lines = [
        "# Relatório de avaliação do DeepEdu",
        "",
        f"- Data: {meta.get('date')}",
        f"- Versão da base de conhecimento: {meta.get('index_version') or 'não versionada'}",
        f"- Modelo de linguagem: {meta.get('llm_model')}",
        f"- Limiar de abstenção: {meta.get('min_score')}",
        f"- Perguntas avaliadas: {summary['total']}",
        "",
        "| Métrica | Resultado |",
        "|---|---|",
        f"| Taxa de abstenção | {_pct(summary['abstention_rate'])} |",
        f"| Acerto da fonte ({summary['source_evaluated']} perguntas com documento esperado) | {_pct(summary['source_accuracy'])} |",
        f"| Consistência da política de abstenção | {_pct(summary['policy_consistency'])} |",
        f"| Pontuação média da recuperação | {summary['mean_max_score']} |",
    ]
    if "calc_accuracy" in summary:
        lines += [
            f"| Acerto dos cálculos conferidos pelo SymPy ({summary['calc_evaluated']} perguntas) | {_pct(summary['calc_accuracy'])} |",
            f"| Respostas bloqueadas pela validação de saída | {_pct(summary['blocked_rate'])} |",
            f"| Tempo médio de resposta | {summary['mean_latency_s']} s |",
        ]
    else:
        lines += ["", "Avaliação só da recuperação. Rode com --com-llm para incluir as respostas completas."]
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Avaliação RAG DeepEdu")
    parser.add_argument("--dataset", default=str(ROOT / "docs/eval/dataset_rag_matematica_em.csv"))
    parser.add_argument("--output-dir", default=str(ROOT / "reports"))
    parser.add_argument("--com-llm", action="store_true", help="gera também a resposta completa do tutor")
    args = parser.parse_args()

    rows = load_dataset(Path(args.dataset))
    if not rows:
        print("Nenhuma pergunta ativa no dataset.", file=sys.stderr)
        return 1

    from app.core.config import settings
    from app.rag.index_versions import current_version

    results = []
    for i, row in enumerate(rows, 1):
        print(f"[{i}/{len(rows)}] {row['id']}", file=sys.stderr)
        results.append(evaluate_row(row, with_llm=args.com_llm))
    summary = summarize(results)
    meta = {
        "date": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "index_version": current_version(),
        "llm_model": settings.LLM_MODEL,
        "min_score": settings.RETRIEVAL_MIN_SCORE,
        "with_llm": args.com_llm,
    }

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    json_path = out_dir / f"eval_{stamp}.json"
    md_path = out_dir / f"eval_{stamp}.md"
    json_path.write_text(
        json.dumps({"meta": meta, "summary": summary, "results": results}, indent=2, ensure_ascii=False),
        encoding="utf-8",
    )
    md_path.write_text(render_markdown(summary, meta), encoding="utf-8")
    print(render_markdown(summary, meta))
    print(f"→ {json_path}\n→ {md_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
