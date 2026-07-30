#!/usr/bin/env python3
"""Gera docs/CASOS_DE_USO.md a partir de docs/REQUISITOS.md."""

from __future__ import annotations

import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REQ = ROOT / "docs" / "REQUISITOS.md"
OUT = ROOT / "docs" / "CASOS_DE_USO.md"

ACTORS = {
    "RF": "Estudante EM, Sistema deepEdu",
    "RNF": "Sistema deepEdu, Operador, DPO",
}

PRE = {
    "RF": "Matrícula ECA ativa (`VINCULAR`), consentimento `ACEITO`, acesso liberado.",
    "RNF": "Ambiente configurado conforme `.env.example` e documentação de deploy.",
}

POST = {
    "RF": "Evento registrado em `audit_log`; resposta entregue via WhatsApp ou painel.",
    "RNF": "Critério de aceitação do requisito verificado em teste ou checklist.",
}


def parse_requirements(text: str) -> list[tuple[str, str, str, str]]:
    pattern = re.compile(r"^### (RF\d+|RNF\d+) — (.+)$", re.MULTILINE)
    matches = list(pattern.finditer(text))
    items: list[tuple[str, str, str, str]] = []
    for i, match in enumerate(matches):
        rid, title = match.group(1), match.group(2)
        start = match.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        block = text[start:end]
        mod = re.search(r"\*\*Módulos:\*\* (.+)", block)
        modules = mod.group(1).strip() if mod else "—"
        items.append((rid, title, modules, block.strip().split("\n\n")[0][:300]))
    return items


def flow_for(rid: str, title: str) -> str:
    kind = "RNF" if rid.startswith("RNF") else "RF"
    actor = ACTORS[kind]
    if kind == "RF":
        steps = [
            f"1. {actor.split(',')[0]} envia ação relacionada a «{title}».",
            "2. Sistema valida matrícula, consentimento e auditoria (fail-closed).",
            f"3. Sistema executa pipeline necessário para {rid}.",
            "4. Sistema registra eventos (`audit_log` / LangSmith).",
            "5. Sistema retorna resultado ao ator ou operador.",
        ]
    else:
        steps = [
            f"1. Operador/DPO inicia verificação de {rid} — {title}.",
            "2. Sistema aplica configuração, limites ou política correspondente.",
            "3. Métricas, logs ou testes automatizados confirmam conformidade.",
            "4. Evidência arquivada (relatório eval, backup, CI).",
        ]
    return "\n".join(steps)


def build_md(items: list[tuple[str, str, str, str]]) -> str:
    lines = [
        "# Casos de Uso — deepEdu (derivados de RF e RNF)",
        "",
        "| Campo | Valor |",
        "|-------|-------|",
        "| **Versão** | 1.0 |",
        "| **Projeto** | deepEdu — Tutor RAG Matemática EM |",
        "| **Base** | `docs/REQUISITOS.md` v1.2 |",
        "| **Formato** | Um caso de uso por RF/RNF |",
        "",
        "---",
        "",
        "## 1. Visão geral",
        "",
        "Cada caso de uso (UC) rastreia diretamente um requisito funcional (RF) ou não funcional (RNF).",
        "Atores principais: **Estudante EM**, **Administrador/DPO**, **Operador**, **Sistema deepEdu**.",
        "",
        "### Diagrama de contexto",
        "",
        "```",
        "Estudante ──WhatsApp──► deepEdu API ──► RAG (retrieval + Qwen + SymPy)",
        "                              │",
        "Administrador ──painel/API──►├─► audit_log / LangSmith",
        "DPO ──export────────────────┘",
        "```",
        "",
        "---",
        "",
        "## 2. Casos de uso funcionais (RF)",
        "",
    ]

    for rid, title, modules, desc in items:
        if not rid.startswith("RF"):
            continue
        uc = rid.replace("RF", "UC-RF")
        lines.extend(
            [
                f"### {uc} — {title}",
                "",
                f"| Campo | Valor |",
                f"|-------|-------|",
                f"| **Requisito** | {rid} |",
                f"| **Módulos** | {modules} |",
                f"| **Atores** | {ACTORS['RF']} |",
                f"| **Pré-condições** | {PRE['RF']} |",
                f"| **Descrição** | {desc.replace(chr(10), ' ')[:250]} |",
                "",
                "**Fluxo principal:**",
                "",
                flow_for(rid, title),
                "",
                f"| **Pós-condições** | {POST['RF']} |",
                "",
                "---",
                "",
            ]
        )

    lines.extend(["## 3. Casos de uso não funcionais (RNF)", ""])
    for rid, title, modules, desc in items:
        if not rid.startswith("RNF"):
            continue
        uc = rid.replace("RNF", "UC-RNF")
        lines.extend(
            [
                f"### {uc} — {title}",
                "",
                f"| Campo | Valor |",
                f"|-------|-------|",
                f"| **Requisito** | {rid} |",
                f"| **Módulos** | {modules} |",
                f"| **Atores** | {ACTORS['RNF']} |",
                f"| **Pré-condições** | {PRE['RNF']} |",
                f"| **Descrição** | {desc.replace(chr(10), ' ')[:250]} |",
                "",
                "**Fluxo de verificação:**",
                "",
                flow_for(rid, title),
                "",
                f"| **Pós-condições** | {POST['RNF']} |",
                "",
                "---",
                "",
            ]
        )

    lines.extend(
        [
            "## 4. Matriz de rastreabilidade UC → RF/RNF",
            "",
            "| UC | Requisito | Tipo |",
            "|----|-----------|------|",
        ]
    )
    for rid, title, _, _ in items:
        prefix = "UC-RNF" if rid.startswith("RNF") else "UC-RF"
        num = rid[3:]
        lines.append(f"| {prefix}{num} | {rid} | {'RNF' if rid.startswith('RNF') else 'RF'} |")

    lines.append("")
    return "\n".join(lines)


def main() -> None:
    text = REQ.read_text(encoding="utf-8")
    items = parse_requirements(text)
    OUT.write_text(build_md(items), encoding="utf-8")
    print(f"Gerado: {OUT} ({len(items)} casos de uso)")


if __name__ == "__main__":
    main()
