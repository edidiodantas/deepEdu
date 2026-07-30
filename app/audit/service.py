from app.audit.repository import AuditEvent, append_audit_log


class AuditLogError(RuntimeError):
    """Falha ao gravar log de auditoria (fail-closed)."""


def log_event(
    *,
    correlation_id: str,
    actor_type: str,
    actor_id: str,
    session_id: str,
    action: str,
    resource: str,
    outcome: str,
    metadata: dict | None = None,
    langsmith_run_id: str | None = None,
    fail_closed: bool = False,
) -> str | None:
    try:
        return append_audit_log(
            AuditEvent(
                correlation_id=correlation_id,
                actor_type=actor_type,
                actor_id=actor_id,
                session_id=session_id,
                action=action,
                resource=resource,
                outcome=outcome,
                metadata=metadata,
                langsmith_run_id=langsmith_run_id,
            )
        )
    except Exception as exc:
        if fail_closed:
            raise AuditLogError(str(exc)) from exc
        return None


def require_log(**kwargs) -> str:
    event_id = log_event(**kwargs, fail_closed=True)
    if not event_id:
        raise AuditLogError("Falha ao gravar evento de auditoria")
    return event_id
