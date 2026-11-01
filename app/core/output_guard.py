"""Validação da resposta do LLM antes de chegar ao aluno.

Bloqueia três classes de risco, nesta ordem:

1. resposta vazia;
2. vazamento de instruções internas ou de segredos de configuração;
3. conteúdo impróprio para estudantes menores de idade (violência, autolesão,
   conteúdo sexual, drogas, armas, ofensas).

Termos com uso legítimo em Matemática (por exemplo, "sexo" em tabelas estatísticas
ou "crescimento explosivo") ficam fora da lista para evitar bloqueios indevidos.

A detecção usa listas de padrões (expressões regulares). É uma proteção básica e
determinística: cobre termos conhecidos e não substitui um classificador treinado.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

SAFE_REFUSAL = "Não posso atender a esse pedido."
SAFE_REFUSAL_FULL = (
    "Não posso atender a esse pedido. Vamos voltar à Matemática? Envie sua dúvida ou "
    "converse com seu professor."
)

_LEAK = re.compile(
    r"Voc[eê] [eé] um tutor de Matem[aá]tica para estudantes"
    r"|##\s*(?:Regras|Seguran[cç]a|Modo|Contexto BNCC|Formato da resposta)"
    r"|</?\s*(?:context|pergunta_aluno)\s*>"
    r"|\b(?:ADMIN_API_KEY|AUDIT_PHONE_SALT|PHONE_ENCRYPTION_KEY|ASAAS_API_KEY|LANGSMITH_API_KEY)\b"
    r"|\b(?:api[_ -]?key|senha|password|secret)\s*[:=]\s*\S+",
    re.IGNORECASE,
)

_INAPPROPRIATE = re.compile(
    r"\b(?:"
    # Violência e autolesão
    r"suic[ií]d\w*|se\s+matar|automutila\w*|cortar\s+os\s+pulsos|matar\s+(?:algu[eé]m|pessoas)"
    r"|assassin\w*|tortur\w*|espancar|agredir\s+algu[eé]m"
    # Conteúdo sexual
    r"|sexual\w*|pornogra\w*|nudez|nudes|estupr\w*|er[oó]tic\w*"
    # Drogas e armas
    r"|coca[ií]na|maconha|crack|hero[ií]na|metanfetamina|arma\s+de\s+fogo|bomba\s+caseira"
    # Ofensas
    r"|idiota|imbecil|retardad\w*|ot[aá]ri\w*|vagabund\w*|porra|caralho|merda|puta\w*|vadia\w*"
    r")\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class OutputCheck:
    accepted: bool
    text: str
    reason: str


def validate_tutor_output(text: str) -> OutputCheck:
    """Devolve a resposta original, se aprovada, ou a mensagem de recusa."""
    raw = (text or "").strip()
    if not raw:
        return OutputCheck(False, SAFE_REFUSAL_FULL, "empty")
    if _LEAK.search(raw):
        return OutputCheck(False, SAFE_REFUSAL_FULL, "leak")
    if _INAPPROPRIATE.search(raw):
        return OutputCheck(False, SAFE_REFUSAL_FULL, "inappropriate")
    return OutputCheck(True, raw, "ok")
