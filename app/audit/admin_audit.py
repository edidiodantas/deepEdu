import uuid
from functools import wraps

from app.audit.service import log_event


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
                    metadata={"kwargs": {k: str(v) for k, v in kwargs.items()}},
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
