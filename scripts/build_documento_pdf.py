#!/usr/bin/env python3
"""
Gera o Documento Final consolidado em HTML e PDF para impressão.

Uso:
    python scripts/build_documento_pdf.py

Saída:
    docs/output/DOCUMENTO_FINAL.html
    docs/output/DOCUMENTO_FINAL.pdf
"""

from __future__ import annotations

import re
import subprocess
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / "docs"
OUTPUT = DOCS / "output"
PRINT_CSS = DOCS / "print" / "print.css"

PARTS = [
    ("REQUISITOS.md", "Parte I — Especificação de Requisitos"),
    ("TOKEN_BUDGET.md", "Parte II — Orçamento de Tokens (Qwen2.5-Math 4K)"),
    ("AUDITORIA_ECA.md", "Parte III — Auditoria Integral (ECA Digital)"),
    ("REVISAO_IMPLEMENTACAO.md", "Parte IV — Revisão v3.0 (implementação completa)"),
    ("CASOS_DE_USO.md", "Parte V — Casos de Uso (RF e RNF)"),
    ("ECA_DIGITAL_CHECKLIST.md", "Parte VI — Checklist ECA Digital"),
    ("RBAC.md", "Parte VII — Controle de Acesso (RBAC)"),
    ("ROPA.md", "Parte VIII — Registro de Operações (ROPA)"),
    ("DPIA.md", "Parte IX — DPIA (Avaliação de Impacto)"),
    ("SEGURANCA_DADOS.md", "Parte X — Segurança de Dados em Repouso"),
    ("eval/README.md", "Parte XI — Avaliação RAG"),
]


def read_md(rel_path: str) -> str:
    path = DOCS / rel_path
    if not path.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {path}")
    return path.read_text(encoding="utf-8")


def strip_leading_h1(content: str) -> str:
    """Remove H1 duplicado das partes (capa já tem título principal)."""
    lines = content.splitlines()
    if lines and lines[0].startswith("# "):
        lines = lines[1:]
        while lines and not lines[0].strip():
            lines = lines[1:]
    return "\n".join(lines)


def build_cover() -> str:
    today = date.today().strftime("%d/%m/%Y")
    return f"""<div class="cover-page">
  <h1>DeepEdu</h1>
  <p class="subtitle">Tutor RAG de Matemática — Ensino Médio</p>
  <p class="subtitle"><strong>Documento Final de Requisitos e Conformidade</strong></p>
  <dl class="meta">
    <dt>Projeto</dt><dd>DeepEdu — Sistema RAG modular</dd>
    <dt>Versão</dt><dd>1.0</dd>
    <dt>Data</dt><dd>{today}</dd>
    <dt>Status</dt><dd>Aprovado para desenvolvimento</dd>
    <dt>Público-alvo</dt><dd>Estudantes do Ensino Médio (15–17 anos)</dd>
    <dt>Canal principal</dt><dd>WhatsApp Business Cloud API</dd>
    <dt>Plataforma</dt><dd>Ubuntu Server · Docker · LangChain/LangGraph</dd>
    <dt>Conteúdo</dt><dd>Requisitos · Tokens · Auditoria ECA · Revisão · Checklists · ROPA</dd>
    <dt>Versão PDF</dt><dd>3.0 — implementação completa + casos de uso RF/RNF</dd>
  </dl>
</div>
"""


def build_toc() -> str:
    items = [
        ("parte-i", "Parte I — Especificação de Requisitos (RF/RNF)"),
        ("parte-ii", "Parte II — Orçamento de Tokens (Qwen2.5-Math 4K)"),
        ("parte-iii", "Parte III — Auditoria Integral (ECA Digital)"),
        ("parte-iv", "Parte IV — Revisão de Implementação v3.0"),
        ("parte-v", "Parte V — Casos de Uso (RF e RNF)"),
        ("parte-vi", "Parte VI — Checklist ECA Digital"),
        ("parte-vii", "Parte VII — Controle de Acesso (RBAC)"),
        ("parte-viii", "Parte VIII — Registro de Operações (ROPA)"),
        ("parte-ix", "Parte IX — DPIA"),
        ("parte-x", "Parte X — Segurança de Dados em Repouso"),
        ("parte-xi", "Parte XI — Avaliação RAG"),
        ("anexo-a", "Anexo A — Dataset de avaliação (50 perguntas)"),
        ("anexo-b", "Anexo B — Prompts do sistema"),
    ]
    lis = "\n".join(f'    <li><a href="#{aid}">{label}</a></li>' for aid, label in items)
    return f"""<div class="toc">
  <h2>Sumário</h2>
  <ol>
{lis}
  </ol>
</div>
"""


def slugify(text: str) -> str:
    s = text.lower()
    s = re.sub(r"parte\s+[ivxlc]+", lambda m: m.group(0).replace(" ", "-"), s)
    s = re.sub(r"[^a-z0-9\-]+", "-", s)
    return s.strip("-")


def build_annex_prompts() -> str:
    prompts_dir = ROOT / "prompts"
    if not prompts_dir.exists():
        return ""
    blocks = []
    for path in sorted(prompts_dir.glob("*.md")):
        content = path.read_text(encoding="utf-8")
        blocks.append(f"<h3>{path.name}</h3>\n<pre>{content}</pre>")
    body = "\n".join(blocks)
    return f"""
<div id="anexo-b" class="section-break">
  <h1>Anexo B — Prompts do sistema</h1>
  <p>Arquivos em <code>prompts/</code>. Orçamento: sistema ≤ 400 tokens (Qwen2.5-Math).</p>
  {body}
</div>
"""


def build_annex_dataset() -> str:
  csv_path = DOCS / "eval" / "dataset_rag_matematica_em.csv"
  if not csv_path.exists():
      return ""
  lines = csv_path.read_text(encoding="utf-8").strip().splitlines()
  header = lines[0].split(",")
  rows = [line.split(",") for line in lines[1:11]]  # 10 primeiras linhas de dados

  thead = "".join(f"<th>{h}</th>" for h in header[:8])
  tbody_rows = []
  for row in rows:
      cells = row + [""] * (8 - len(row))
      tbody_rows.append("".join(f"<td>{c}</td>" for c in cells[:8]))

  tbody = "\n".join(f"    <tr>{r}</tr>" for r in tbody_rows)
  return f"""
<div id="anexo-a" class="section-break">
  <h1>Anexo A — Dataset de avaliação RAG (50 perguntas ativas)</h1>
  <p>Arquivo completo: <code>docs/eval/dataset_rag_matematica_em.csv</code> (EM-001 a EM-050).</p>
  <table>
    <thead><tr>{thead}</tr></thead>
    <tbody>
{tbody}
    </tbody>
  </table>
</div>
"""


def markdown_to_html_fragment(md: str) -> str:
    result = subprocess.run(
        ["pandoc", "-f", "markdown", "-t", "html", "--wrap=none"],
        input=md,
        capture_output=True,
        text=True,
        check=True,
    )
    return result.stdout


def build_body() -> str:
    sections: list[str] = []
    part_ids = [
        "parte-i", "parte-ii", "parte-iii", "parte-iv", "parte-v", "parte-vi",
        "parte-vii", "parte-viii", "parte-ix", "parte-x", "parte-xi",
    ]

    for i, (rel_path, title) in enumerate(PARTS):
        part_id = part_ids[i]
        content = strip_leading_h1(read_md(rel_path))
        html = markdown_to_html_fragment(content)
        sections.append(
            f'<div id="{part_id}" class="section-break">\n'
            f'  <div class="part-title">{title}</div>\n'
            f"  {html}\n"
            f"</div>"
        )

    sections.append(build_annex_dataset())
    sections.append(build_annex_prompts())
    return "\n".join(sections)


def build_signatures() -> str:
    return """
<div class="signature-block section-break">
  <h2>Termo de aprovação</h2>
  <p>Declaro ter revisado o presente documento e aprovo seu uso como base para o desenvolvimento do sistema DeepEdu.</p>
  <div class="signature-line">Product Owner — Nome / Data</div>
  <div class="signature-line">Tech Lead — Nome / Data</div>
  <div class="signature-line">Responsável pedagógico — Nome / Data</div>
  <div class="signature-line">DPO / Encarregado de dados — Nome / Data</div>
</div>
"""


def build_html() -> str:
    css = PRINT_CSS.read_text(encoding="utf-8")
    return f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="utf-8"/>
  <title>DeepEdu — Documento Final de Requisitos</title>
  <style>{css}</style>
</head>
<body>
{build_cover()}
{build_toc()}
{build_body()}
{build_signatures()}
</body>
</html>
"""


def html_to_pdf(html_path: Path, pdf_path: Path) -> None:
    from weasyprint import HTML

    HTML(filename=str(html_path)).write_pdf(str(pdf_path))


def main() -> int:
    OUTPUT.mkdir(parents=True, exist_ok=True)
    html_path = OUTPUT / "DOCUMENTO_FINAL.html"
    pdf_path = OUTPUT / "DOCUMENTO_FINAL.pdf"

    print("Gerando HTML consolidado...")
    html = build_html()
    html_path.write_text(html, encoding="utf-8")
    print(f"  → {html_path}")

    print("Gerando PDF para impressão...")
    html_to_pdf(html_path, pdf_path)
    size_kb = pdf_path.stat().st_size // 1024
    print(f"  → {pdf_path} ({size_kb} KB)")

    return 0


if __name__ == "__main__":
    sys.exit(main())
