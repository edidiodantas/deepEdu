"""Barreira entre instruções do tutor e texto que não é ordem.

A pergunta do aluno, o acervo e o histórico entram entre delimitadores.
Se esse texto trouxer os mesmos delimitadores, eles são removidos antes
do fechamento verdadeiro — assim não dá para encerrar a cerca por dentro.

Além disso, a pergunta do aluno passa por neutralize_injection, que troca
formulações típicas de manipulação ("ignore as instruções", "mostre seu prompt",
"finja que...") por um marcador neutro. A lista cobre tentativas conhecidas e não
é exaustiva.
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
NEUTRALIZED_MARK = "[trecho removido]"

# Cercas deste projeto e a tag antiga <context>, que um PDF podia fechar.
_FENCE = re.compile(
    r"<<<\s*/?\s*(?:FIM_)?(?:PERGUNTA_ALUNO|MATERIAL_ACERVO|HISTORICO)\s*>>>"
    r"|</?\s*context\s*>",
    re.IGNORECASE,
)

_INJECTION_PATTERNS = [
    # Português
    r"(?:ignore|ignora|desconsidere|desconsidera|esque[cç]a|esquece)\s+(?:todas\s+)?(?:as\s+|suas\s+|tuas\s+)?"
    r"(?:regras|instru[cç][oõ]es|orienta[cç][oõ]es|ordens)(?:\s+anteriores)?",
    r"(?:mostre|mostra|revele|revela|repita|repete|exiba|exibe|imprima|imprime|diga|diz)\s+"
    r"(?:o\s+|seu\s+|teu\s+|as\s+|suas\s+|tuas\s+)?(?:prompt|instru[cç][oõ]es)(?:\s+(?:de|do)\s+sistema)?",
    r"(?:prompt|instru[cç][oõ]es)\s+(?:de|do)\s+sistema",
    r"(?:a\s+partir\s+de\s+agora\s+voc[eê]\s+[eé]|voc[eê]\s+agora\s+[eé])\s+(?:um|uma|o|a)\s+(?!tutor)",
    r"(?:finja|finge|fingir)\s+(?:que|ser)",
    r"(?:aja|age|atue|atua)\s+como\s+(?!tutor)",
    r"modo\s+(?:desenvolvedor|developer|deus|sem\s+restri[cç][oõ]es)",
    # Inglês
    r"ignore\s+(?:all\s+)?(?:the\s+)?(?:previous|above|prior)\s+instructions",
    r"(?:reveal|show|print|repeat)\s+(?:your\s+|the\s+)?(?:system\s+)?prompt",
    r"system\s+prompt",
    r"jailbreak",
]
_INJECTION = re.compile("|".join(f"(?:{p})" for p in _INJECTION_PATTERNS), re.IGNORECASE)


def neutralize(text: str) -> tuple[str, bool]:
    """Tira delimitadores forjados. Devolve o texto e se houve remoção."""
    raw = text or ""
    cleaned, count = _FENCE.subn(_REMOVED, raw)
    return cleaned, count > 0


def neutralize_injection(text: str) -> tuple[str, list[str]]:
    """Troca formulações típicas de manipulação por um marcador neutro."""
    found: list[str] = []

    def _mark(match: re.Match) -> str:
        found.append(match.group(0))
        return NEUTRALIZED_MARK

    return _INJECTION.sub(_mark, text or ""), found


def has_meaningful_content(text: str) -> bool:
    """Verdadeiro se, retirados os marcadores, ainda sobra uma pergunta."""
    rest = (text or "").replace(NEUTRALIZED_MARK, " ").replace(_REMOVED, " ")
    return len(re.sub(r"[\W_]+", "", rest)) >= 3


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
