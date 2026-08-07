import uuid
from functools import wraps

from app.audit.service import log_event

_REDACT_KEYS = {"phone", "cpf_cnpj", "email", "parental_consent_ref", "asaas_api_key"}


def _safe_kwargs(kwargs: dict) -> dict:
    safe = {}
    for key, value in kwargs.items():
        if key.lower() in _REDACT_KEYS or "phone" in key.lower() or "token" in key.lower():
            safe[key] = "[redacted]"
        else:
            safe[key] = str(value)
    return safe


def audited_admin_action(action: str, resource: str):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            correlation_id = str(uuid.uuid4())
            try:
                result = func(*args, **kwargs)
                log_event(
                    correlation_id=correlation_id,
                    actor_type="admin",
                    actor_id="admin",
                    session_id="admin",
                    action=action,
                    resource=resource,
                    outcome="success",
                    metadata={"kwargs": _safe_kwargs(kwargs)},
                )
                return result
            except Exception as exc:
                log_event(
                    correlation_id=correlation_id,
                    actor_type="admin",
                    actor_id="admin",
                    session_id="admin",
                    action=action,
                    resource=resource,
                    outcome="failure",
                    metadata={"error": type(exc).__name__},
                )
                raise

        return wrapper

    return decorator
