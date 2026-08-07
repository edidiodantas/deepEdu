"""Normalização de texto compartilhada (comandos WhatsApp, consentimento)."""

from __future__ import annotations

import unicodedata


def normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text or "")
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower().strip()
