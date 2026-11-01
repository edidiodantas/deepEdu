"""Métricas consolidadas de qualidade e proteção, calculadas a partir da trilha de auditoria.

Não há coleta adicional de dados: os números vêm dos eventos que o sistema já registra
(rag.started, rag.abstained, output.blocked etc.), o que mantém as métricas auditáveis.
"""

from __future__ import annotations

from collections import Counter

from app.audit.repository import fetch_audit_logs


def _rate(part: int, total: int) -> float:
    return round(part / total, 3) if total else 0.0


def compute_metrics(logs: list[dict]) -> dict:
    """Consolida uma lista de eventos de auditoria (função pura, testável)."""
    actions = Counter(row.get("action") for row in logs)
    questions = actions["rag.started"]
    abstained = actions["rag.abstained"]
    completed = actions["rag.completed"]
    blocked = actions["output.blocked"]
    sympy_ok = actions["sympy.verified"]
    sympy_div = actions["sympy.divergence"]

    scores = [
        float(row["metadata"]["max_retrieval_score"])
        for row in logs
        if row.get("action") == "rag.completed"
        and isinstance(row.get("metadata"), dict)
        and row["metadata"].get("max_retrieval_score") is not None
    ]
    block_reasons = Counter(
        (row.get("metadata") or {}).get("reason", "?") for row in logs if row.get("action") == "output.blocked"
    )
    versions = Counter(
        (row.get("metadata") or {}).get("index_version") or "sem versão"
        for row in logs
        if row.get("action") in {"rag.completed", "rag.abstained"}
    )
    return {
        "perguntas": questions,
        "respondidas": completed,
        "abstencoes": abstained,
        "taxa_abstencao": _rate(abstained, questions),
        "respostas_bloqueadas": blocked,
        "taxa_bloqueio": _rate(blocked, questions),
        "motivos_bloqueio": dict(block_reasons),
        "injecoes_neutralizadas": actions["prompt.injection_neutralized"],
        "pedidos_sem_consentimento": actions["consent.required"],
        "consentimentos_concedidos": actions["consent.granted"],
        "consentimentos_revogados": actions["consent.revoked"],
        "calculos_conferidos": sympy_ok,
        "calculos_divergentes": sympy_div,
        "taxa_acerto_calculos": _rate(sympy_ok, sympy_ok + sympy_div),
        "falhas": actions["rag.failed"],
        "pontuacao_media_recuperacao": round(sum(scores) / len(scores), 3) if scores else None,
        "respostas_por_versao_da_base": dict(versions),
        "reindexacoes": actions["index.rebuilt"],
        "restauracoes_de_versao": actions["index.restored"],
    }


def quality_metrics(date_from: str | None = None, date_to: str | None = None) -> dict:
    logs = fetch_audit_logs(date_from=date_from, date_to=date_to, limit=1_000_000)
    return {"periodo": {"de": date_from, "ate": date_to}, **compute_metrics(logs)}
