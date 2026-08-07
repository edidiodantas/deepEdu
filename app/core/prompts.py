"""Compatibilidade: o prompt oficial vive em prompts/*.md via prompt_loader."""

from app.core.prompt_loader import load_system_prompt


def get_system_prompt() -> str:
    return load_system_prompt()


# Evita segunda cópia hardcoded da persona do tutor.
SYSTEM_PROMPT = None
