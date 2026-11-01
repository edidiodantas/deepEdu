"""Barreira entre instruções do tutor e texto que não é ordem.

A pergunta do aluno, o acervo e o histórico entram entre delimitadores.
Se esse texto trouxer os mesmos delimitadores, eles são removidos antes
do fechamento verdadeiro — assim não dá para encerrar a cerca por dentro.
"""

from __future__ import annotations

import re
from typing import Any

QUESTION_OPEN = "<<<PERGUNTA_ALUNO>>>"
QUESTION_CLOSE = "<<<FIM_PERGUNTA_ALUNO>>>"
MATERIAL_OPEN = "<<<MATERIAL_ACERVO>>>"
MATERIAL_CLOSE = "<<<FIM_MATERIAL_ACERVO>>>"
HISTORY_OPEN = "<<<HISTORICO>>>"
HISTORY_CLOSE = "<<<FIM_HISTORICO>>>"

_REMOVED = "[delimitador removido]"

# Cercas deste projeto e a tag antiga <context>, que um PDF podia fechar.
_FENCE = re.compile(
    r"<<<\s*/?\s*(?:FIM_)?(?:PERGUNTA_ALUNO|MATERIAL_ACERVO|HISTORICO)\s*>>>"
    r"|</?\s*context\s*>",
    re.IGNORECASE,
)


def neutralize(text: str) -> tuple[str, bool]:
    """Tira delimitadores forjados. Devolve o texto e se houve remoção."""
    raw = text or ""
    cleaned, count = _FENCE.subn(_REMOVED, raw)
    return cleaned, count > 0


def wrap_question(text: str) -> str:
    cleaned, _ = neutralize(text)
    return f"{QUESTION_OPEN}\n{cleaned}\n{QUESTION_CLOSE}"


def wrap_material(text: str) -> str:
    cleaned, _ = neutralize(text)
    return f"{MATERIAL_OPEN}\n{cleaned}\n{MATERIAL_CLOSE}"


def shield_history(messages: list[Any]) -> list[Any]:
    """Recoloca o histórico como dado, sem regravar a conversa guardada."""
    from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

    shielded: list[Any] = []
    for message in messages:
        content = getattr(message, "content", "")
        text = content if isinstance(content, str) else str(content)
        cleaned, _ = neutralize(text)
        if isinstance(message, HumanMessage):
            shielded.append(HumanMessage(content=wrap_question(cleaned)))
        elif isinstance(message, SystemMessage):
            shielded.append(
                SystemMessage(content=f"{HISTORY_OPEN}\n{cleaned}\n{HISTORY_CLOSE}")
            )
        elif isinstance(message, AIMessage):
            shielded.append(AIMessage(content=cleaned))
        else:
            shielded.append(message.__class__(content=cleaned))
    return shielded
