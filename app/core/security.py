import uuid

from fastapi import Header, HTTPException

from app.audit.service import log_event
from app.core.config import settings


def require_admin_api_key(x_admin_api_key: str | None = Header(default=None)):
    expected = settings.ADMIN_API_KEY.strip()
    correlation_id = str(uuid.uuid4())
    if not expected:
        raise HTTPException(status_code=500, detail="ADMIN_API_KEY nao configurada")
    if x_admin_api_key != expected:
        log_event(
            correlation_id=correlation_id,
            actor_type="admin",
            actor_id="unknown",
            session_id="admin",
            action="admin.action_denied",
            resource="admin_api",
            outcome="denied",
            metadata={"reason": "invalid_api_key"},
        )
        raise HTTPException(status_code=403, detail="Acesso administrativo negado")
