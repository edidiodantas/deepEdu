from app.audit.repository import ensure_audit_tables


def init_audit() -> None:
    ensure_audit_tables()
