from pathlib import Path

from app.core.config import settings


def load_system_prompt() -> str:
    path = Path(settings.PROMPT_FILE)
    if path.exists():
        text = path.read_text(encoding="utf-8").strip()
        lines = [line for line in text.splitlines() if not line.startswith("#")]
        return "\n".join(lines).strip()
    # Fallback mínimo se arquivo ausente
    return (
        "Voce e um tutor de Matematica para o Ensino Medio brasileiro. "
        "Responda em portugues, em passos, usando apenas o contexto em {context}. "
        "Cite a fonte ao final."
    )
