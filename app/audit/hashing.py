import hashlib

from app.core.config import settings


def phone_hash(phone: str) -> str:
    normalized = phone.strip()
    salt = settings.AUDIT_PHONE_SALT.strip() or "deepedu-dev-salt"
    digest = hashlib.sha256(f"{salt}:{normalized}".encode("utf-8")).hexdigest()
    return digest[:32]


def pseudonymize_session_id(phone: str) -> str:
    return f"sess_{phone_hash(phone)[:16]}"
