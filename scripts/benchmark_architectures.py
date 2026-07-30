import argparse
import json
import statistics
import subprocess
import sys
import textwrap
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path


DEFAULT_PROMPTS = [
    "Explique de forma simples a diferenca entre mitose e meiose.",
    "Resolva: 2x + 5 = 17, mostrando os passos.",
    "Resuma a Revolucao Francesa em 6 linhas para ensino medio.",
    "Crie 3 questoes de revisao sobre fotossintese com gabarito.",
    "Me ajude a montar um plano de estudo de 7 dias para matematica.",
]


CHILD_CODE = textwrap.dedent(
    """
    import json
    import time
    import traceback

    from app.rag.chain import ask_tutor

    prompt = {prompt}
    phone = {phone}

    try:
        t0 = time.perf_counter()
        answer = ask_tutor(phone=phone, question=prompt)
        elapsed_ms = (time.perf_counter() - t0) * 1000
        print(json.dumps({
            "ok": True,
            "elapsed_ms": elapsed_ms,
            "answer": answer,
        }, ensure_ascii=False))
    except Exception as exc:
        print(json.dumps({
            "ok": False,
            "error": str(exc),
            "traceback": traceback.format_exc(),
        }, ensure_ascii=False))
    """
)


@dataclass
class RunResult:
    ok: bool
    elapsed_ms: float | None
    answer: str | None
    error: str | None
    traceback: str | None


def pick_python(project_path: Path) -> str:
    venv_python = project_path / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    return sys.executable


def run_once(project_path: Path, prompt: str, phone: str) -> RunResult:
    py = pick_python(project_path)
    code = CHILD_CODE.format(prompt=repr(prompt), phone=repr(phone))
    proc = subprocess.run(
        [py, "-c", code],
        cwd=str(project_path),
        capture_output=True,
        text=True,
        check=False,
    )

    raw = (proc.stdout or "").strip()
    if not raw:
        return RunResult(
            ok=False,
            elapsed_ms=None,
            answer=None,
            error=f"Sem saida JSON. stderr={proc.stderr.strip()}",
            traceback=None,
        )

    try:
        payload = json.loads(raw.splitlines()[-1])
    except json.JSONDecodeError:
        return RunResult(
            ok=False,
            elapsed_ms=None,
            answer=None,
            error=f"Saida invalida: {raw[:300]}",
            traceback=proc.stderr.strip() or None,
        )

    return RunResult(
        ok=bool(payload.get("ok")),
        elapsed_ms=payload.get("elapsed_ms"),
        answer=payload.get("answer"),
        error=payload.get("error"),
        traceback=payload.get("traceback"),
    )


def load_prompts(path: Path | None, cli_prompts: list[str]) -> list[str]:
    if cli_prompts:
        return [p.strip() for p in cli_prompts if p.strip()]
    if path and path.exists():
        lines = [ln.strip() for ln in path.read_text(encoding="utf-8").splitlines()]
        prompts = [ln for ln in lines if ln and not ln.startswith("#")]
        if prompts:
            return prompts
    return DEFAULT_PROMPTS


def summarize_elapsed(values: list[float]) -> dict[str, float]:
    return {
        "avg_ms": statistics.mean(values),
        "min_ms": min(values),
        "max_ms": max(values),
        "p50_ms": statistics.median(values),
    }


def main():
    parser = argparse.ArgumentParser(
        description="Benchmark DeepSeek vs Phi usando os mesmos prompts."
    )
    parser.add_argument("--deepseek-project", default=".", help="Projeto DeepSeek")
    parser.add_argument(
        "--phi-project", default="./deepedu_phi_compare", help="Projeto Phi"
    )
    parser.add_argument("--prompts-file", default="", help="Arquivo .txt de prompts")
    parser.add_argument(
        "--prompt", action="append", default=[], help="Prompt avulso (pode repetir)"
    )
    parser.add_argument("--runs", type=int, default=2, help="Repeticoes por prompt")
    parser.add_argument(
        "--warmup", type=int, default=1, help="Rodadas de aquecimento (sem salvar)"
    )
    parser.add_argument(
        "--phone", default="+5511999999999", help="Telefone de sessao para memoria"
    )
    parser.add_argument(
        "--output-dir",
        default="./data/benchmarks",
        help="Pasta de saida para relatorios",
    )
    args = parser.parse_args()

    deepseek_path = Path(args.deepseek_project).resolve()
    phi_path = Path(args.phi_project).resolve()
    output_dir = Path(args.output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    prompts_path = Path(args.prompts_file).resolve() if args.prompts_file else None
    prompts = load_prompts(prompts_path, args.prompt)

    if not deepseek_path.exists() or not phi_path.exists():
        raise SystemExit("Projeto DeepSeek ou Phi nao encontrado.")

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    results = {
        "meta": {
            "timestamp": timestamp,
            "deepseek_project": str(deepseek_path),
            "phi_project": str(phi_path),
            "runs": args.runs,
            "warmup": args.warmup,
            "prompts_count": len(prompts),
        },
        "rows": [],
    }

    systems = {
        "deepseek": deepseek_path,
        "phi": phi_path,
    }
    elapsed_by_system: dict[str, list[float]] = {"deepseek": [], "phi": []}

    for system_name, project_path in systems.items():
        for prompt_idx, prompt in enumerate(prompts, start=1):
            for _ in range(args.warmup):
                run_once(project_path, prompt, args.phone)
            for run_idx in range(1, args.runs + 1):
                rr = run_once(project_path, prompt, args.phone)
                row = {
                    "system": system_name,
                    "prompt_index": prompt_idx,
                    "run_index": run_idx,
                    "prompt": prompt,
                    "ok": rr.ok,
                    "elapsed_ms": rr.elapsed_ms,
                    "error": rr.error,
                    "answer_preview": (rr.answer or "")[:220],
                }
                results["rows"].append(row)
                if rr.ok and rr.elapsed_ms is not None:
                    elapsed_by_system[system_name].append(rr.elapsed_ms)

    summary = {}
    for name, values in elapsed_by_system.items():
        summary[name] = summarize_elapsed(values) if values else {}
        summary[name]["success_count"] = len(values)

    if summary.get("deepseek", {}).get("avg_ms") and summary.get("phi", {}).get("avg_ms"):
        deep_avg = summary["deepseek"]["avg_ms"]
        phi_avg = summary["phi"]["avg_ms"]
        summary["comparison"] = {
            "faster_system": "phi" if phi_avg < deep_avg else "deepseek",
            "avg_delta_ms": abs(deep_avg - phi_avg),
            "phi_speedup_percent_vs_deepseek": ((deep_avg - phi_avg) / deep_avg) * 100,
        }
    else:
        summary["comparison"] = {"note": "Sem dados suficientes para comparar medias."}

    results["summary"] = summary

    json_path = output_dir / f"benchmark_{timestamp}.json"
    md_path = output_dir / f"benchmark_{timestamp}.md"
    json_path.write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = [
        f"# Benchmark DeepSeek vs Phi ({timestamp})",
        "",
        f"- DeepSeek project: `{deepseek_path}`",
        f"- Phi project: `{phi_path}`",
        f"- Prompts: `{len(prompts)}`",
        f"- Runs por prompt: `{args.runs}` (warmup `{args.warmup}`)",
        "",
        "## Resumo de latencia",
    ]

    for name in ("deepseek", "phi"):
        data = summary.get(name, {})
        if not data or "avg_ms" not in data:
            lines.append(f"- {name}: sem dados validos")
            continue
        lines.append(
            f"- {name}: avg={data['avg_ms']:.1f} ms | p50={data['p50_ms']:.1f} ms | "
            f"min={data['min_ms']:.1f} ms | max={data['max_ms']:.1f} ms | "
            f"sucessos={data['success_count']}"
        )

    cmp_data = summary.get("comparison", {})
    if "faster_system" in cmp_data:
        lines.extend(
            [
                "",
                "## Comparacao",
                f"- Mais rapido (media): `{cmp_data['faster_system']}`",
                f"- Diferenca media: `{cmp_data['avg_delta_ms']:.1f} ms`",
                f"- Speedup Phi vs DeepSeek: `{cmp_data['phi_speedup_percent_vs_deepseek']:.2f}%`",
            ]
        )
    else:
        lines.extend(["", "## Comparacao", f"- {cmp_data.get('note', 'Sem comparacao.')}"])

    md_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(f"Benchmark concluido.\nJSON: {json_path}\nMD: {md_path}")


if __name__ == "__main__":
    main()
