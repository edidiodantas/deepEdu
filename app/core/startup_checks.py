from __future__ import annotations

import warnings

from app.core.config import settings


class ProductionConfigError(RuntimeError):
    """Configuração inválida para ambiente de produção."""


def run_startup_checks() -> list[str]:
    """Valida segredos e parâmetros críticos antes de aceitar tráfego."""
    notes: list[str] = []

    if settings.ENV.lower() == "production":
        if not settings.AUDIT_PHONE_SALT or len(settings.AUDIT_PHONE_SALT) < 16:
            raise ProductionConfigError(
                "AUDIT_PHONE_SALT deve ter pelo menos 16 caracteres em produção."
            )
        if not settings.PHONE_ENCRYPTION_KEY or "defina" in settings.PHONE_ENCRYPTION_KEY.lower():
            raise ProductionConfigError(
                "PHONE_ENCRYPTION_KEY (Fernet base64) é obrigatória em produção."
            )
        if not settings.ADMIN_API_KEY or len(settings.ADMIN_API_KEY) < 16:
            raise ProductionConfigError("ADMIN_API_KEY forte é obrigatória em produção.")
        if settings.AUDIT_FAIL_CLOSED is not True:
            raise ProductionConfigError("AUDIT_FAIL_CLOSED deve ser true em produção.")
    else:
        if not settings.AUDIT_PHONE_SALT:
            notes.append("AUDIT_PHONE_SALT ausente — usando fallback de desenvolvimento.")
        if not settings.PHONE_ENCRYPTION_KEY:
            notes.append("PHONE_ENCRYPTION_KEY ausente — chave derivada do salt (somente dev).")

    if settings.LLM_PROVIDER == "ollama":
        notes.append(
            "LLM via Ollama: execute scripts/install_ollama_model.sh antes do primeiro uso."
        )

    for note in notes:
        warnings.warn(note, stacklevel=2)
    return notes
