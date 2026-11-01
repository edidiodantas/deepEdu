"""Barreira contra injeção de instruções (prompt injection) no texto do aluno.

Duas camadas:

1. Delimitação: a pergunta entra no prompt entre QUESTION_OPEN e QUESTION_CLOSE,
   e o prompt do tutor instrui o modelo a tratá-la como dado, nunca como ordem.
2. Neutralização: antes de chegar ao modelo, trechos típicos de manipulação
   ("ignore as regras", "mostre seu prompt", "finja ser...") e qualquer cópia dos
   delimitadores internos são substituídos por um marcador neutro.

A lista de padrões cobre tentativas conhecidas; não é exaustiva.
"""

from __future__ import annotations

import re

QUESTION_OPEN = "<pergunta_aluno>"
QUESTION_CLOSE = "</pergunta_aluno>"
NEUTRALIZED_MARK = "[trecho removido]"

# Delimitadores internos que o aluno não pode reproduzir para "sair" do bloco de dados.
_DELIMITERS = re.compile(r"</?\s*(?:pergunta_aluno|context)\s*>", re.IGNORECASE)

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


def neutralize(text: str) -> tuple[str, list[str]]:
    """Devolve (texto neutralizado, lista de trechos removidos)."""
    original = text or ""
    found: list[str] = []

    def _mark(match: re.Match) -> str:
        found.append(match.group(0))
        return NEUTRALIZED_MARK

    cleaned = _DELIMITERS.sub(_mark, original)
    cleaned = _INJECTION.sub(_mark, cleaned)
    return cleaned, found


def has_meaningful_content(text: str) -> bool:
    """Verdadeiro se, retirados os marcadores, ainda sobra uma pergunta."""
    rest = (text or "").replace(NEUTRALIZED_MARK, " ")
    return len(re.sub(r"[\W_]+", "", rest)) >= 3
