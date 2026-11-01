#!/usr/bin/env python3
"""Conjunto de referência da tese: formato, recusa, vazamento e cálculo.

Não usa outro modelo como juiz. A saída candidata é a do próprio caso
(ou a resposta de referência do gabarito de matemática).
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.core.output_guard import validate_tutor_output  # noqa: E402
from app.core.prompt_barrier import neutralize  # noqa: E402


def _flag(value: str) -> bool:
    return (value or "").strip().lower() == "true"


def load_rows(path: Path) -> list[dict]:
    with path.open(encoding="utf-8") as fh:
        return [row for row in csv.DictReader(fh) if _flag(row.get("ativo", ""))]


def math_reference_rows(path: Path) -> list[dict]:
    """Gabarito de matemática no formato que o tutor deve exibir."""
    rows = []
    for row in load_rows(path):
        answer = (row.get("resposta_esperada") or "").strip()
        source = (row.get("fonte_esperada") or "").strip()
        if not answer or not source:
            continue
        rows.append(
            {
                "id": row["id"],
                "tipo": "gabarito",
                "pergunta": row.get("pergunta", ""),
                "saida_modelo": f"1. {answer}\nFonte: {source}",
                "motivo_esperado": "tutor",
                "delimitador_removido": "false",
                "proibido_na_exibicao": "",
                "requer_calculo": "false",
                "ativo": "true",
            }
        )
    return rows


def _sympy_ok(question: str, shown: str) -> tuple[bool | None, str]:
    try:
        from app.rag.sympy_tool import verify_numeric_answer
    except ImportError:
        return None, "sympy_ausente"
    result = verify_numeric_answer(question, shown)
    if result.get("verified") is True:
        return True, "ok"
    return False, str(result.get("reason") or "divergente")


def score_row(row: dict) -> dict:
    question = row.get("pergunta") or ""
    raw_output = row.get("saida_modelo") or ""
    _, stripped = neutralize(question)
    checked = validate_tutor_output(raw_output, max_chars=4000)
    expected_reason = (row.get("motivo_esperado") or "").strip()
    expected_strip = (row.get("delimitador_removido") or "").strip().lower()
    forbidden = (row.get("proibido_na_exibicao") or "").strip()

    checks: list[tuple[str, bool]] = [
        ("motivo", checked.reason == expected_reason),
    ]
    if expected_strip in {"true", "false"}:
        checks.append(("delimitador", stripped is (expected_strip == "true")))
    if forbidden:
        checks.append(("proibido_oculto", forbidden.lower() not in checked.text.lower()))
    calculo = None
    calculo_nota = ""
    if _flag(row.get("requer_calculo", "")) and checked.accepted:
        calculo, calculo_nota = _sympy_ok(question, checked.text)
        if calculo is not None:
            checks.append(("calculo", calculo))

    passed = all(ok for _, ok in checks)
    return {
        "id": row.get("id", ""),
        "tipo": row.get("tipo", ""),
        "passed": passed,
        "reason": checked.reason,
        "delimiter_stripped": stripped,
        "calculo": calculo,
        "calculo_nota": calculo_nota,
        "checks": {name: ok for name, ok in checks},
    }


def summarize(results: list[dict]) -> dict:
    total = len(results)
    passed = sum(1 for item in results if item["passed"])
    skipped = sum(1 for item in results if item["calculo"] is None and item["calculo_nota"] == "sympy_ausente")
    return {
        "total": total,
        "passed": passed,
        "failed": total - passed,
        "calculo_adiado_sem_sympy": skipped,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Avalia o conjunto de referência deepEdu")
    parser.add_argument(
        "--seguranca",
        default=str(ROOT / "docs/eval/golden_seguranca.csv"),
    )
    parser.add_argument(
        "--matematica",
        default=str(ROOT / "docs/eval/dataset_rag_matematica_em.csv"),
    )
    parser.add_argument("--output", default=str(ROOT / "reports/golden_latest.json"))
    args = parser.parse_args()

    rows = load_rows(Path(args.seguranca)) + math_reference_rows(Path(args.matematica))
    if not rows:
        print("Conjunto de referência vazio.", file=sys.stderr)
        return 1

    results = [score_row(row) for row in rows]
    summary = summarize(results)
    payload = {"summary": summary, "results": results}
    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps(summary, indent=2, ensure_ascii=False))
    failed = [item["id"] for item in results if not item["passed"]]
    if failed:
        print("Falhas:", ", ".join(failed))
        print(f"→ {out}")
        return 1
    print(f"→ {out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
