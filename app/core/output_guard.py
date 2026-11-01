"""Validação da saída do modelo antes de exibir ou reutilizar.

A frase do tutor só segue adiante se estiver no formato esperado e sem
vazamento de prompt, cerca ou pedido de ação. O texto rejeitado não sai.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SAFE_REFUSAL = "Não posso atender a esse pedido."

_REFUSAL_BODY = re.compile(
    r"^\s*n[aã]o posso atender a esse pedido\.?\s*$",
    re.IGNORECASE,
)
_LEAK = re.compile(
    r"<<<\s*(?:FIM_)?(?:PERGUNTA_ALUNO|MATERIAL_ACERVO|HISTORICO)\s*>>>"
    r"|##\s*(?:Recusa|Barreira)"
    r"|Você é um tutor de Matemática para estudantes"
    r"|ADMIN_API_KEY|AUDIT_PHONE_SALT|PHONE_ENCRYPTION_KEY|ASAAS_API_KEY"
    r"|\b(?:api[_-]?key|secret|password|token)\s*[:=]\s*\S+"
    r"|\bsk-[A-Za-z0-9]{8,}",
    re.IGNORECASE,
)
_ACTION = re.compile(
    r"\{\s*\"(?:action|tool|command|function)\"\s*:"
    r"|\b(?:os\.system|subprocess\.(?:run|call|Popen)|rm\s+-rf|sudo\s+\S|drop\s+table|delete\s+from)\b",
    re.IGNORECASE,
)
_STEP = re.compile(r"(?m)^\s*\d+[\.\)]\s+\S")
_SOURCE = re.compile(r"(?i)\bFonte\s*:")
_LETTER = re.compile(r"[A-Za-zÀ-ÿ]")
_CONTROL = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


@dataclass(frozen=True)
class OutputCheck:
    accepted: bool
    text: str
    reason: str


def validate_tutor_output(text: str, *, max_chars: int) -> OutputCheck:
    """Devolve só texto seguro. Em falha, a frase de recusa."""
    raw = (text or "").strip()
    if not raw:
        return OutputCheck(False, SAFE_REFUSAL, "empty")
    if len(raw) > max_chars:
        return OutputCheck(False, SAFE_REFUSAL, "too_long")
    if _CONTROL.search(raw):
        return OutputCheck(False, SAFE_REFUSAL, "format")
    if _LEAK.search(raw):
        return OutputCheck(False, SAFE_REFUSAL, "leak")
    if _ACTION.search(raw):
        return OutputCheck(False, SAFE_REFUSAL, "action")
    if _REFUSAL_BODY.match(raw):
        return OutputCheck(True, SAFE_REFUSAL, "refusal")
    if re.search(r"n[aã]o posso atender a esse pedido", raw, re.IGNORECASE):
        return OutputCheck(False, SAFE_REFUSAL, "format")
    if _expected_tutor_shape(raw):
        return OutputCheck(True, raw, "tutor")
    return OutputCheck(False, SAFE_REFUSAL, "format")


def _expected_tutor_shape(text: str) -> bool:
    if not _LETTER.search(text):
        return False
    if _SOURCE.search(text) or _STEP.search(text):
        return True
    # Resposta curta de cálculo, sem os quatro blocos do prompt.
    return len(text) <= 500
