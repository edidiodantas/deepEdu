import base64
import hashlib

from cryptography.fernet import Fernet

from app.core.config import settings


def _fernet() -> Fernet:
    raw = settings.PHONE_ENCRYPTION_KEY.strip()
    if not raw:
        seed = (settings.AUDIT_PHONE_SALT or "deepedu-dev").encode("utf-8")
        raw = base64.urlsafe_b64encode(hashlib.sha256(seed).digest()).decode("ascii")
    return Fernet(raw.encode("ascii") if isinstance(raw, str) else raw)


def encrypt_phone(phone: str) -> str:
    normalized = phone.strip()
    return _fernet().encrypt(normalized.encode("utf-8")).decode("ascii")


def decrypt_phone(token: str) -> str:
    return _fernet().decrypt(token.encode("ascii")).decode("utf-8")


def mask_phone(phone: str) -> str:
    normalized = phone.strip()
    if len(normalized) <= 6:
        return "***"
    return f"{normalized[:4]}****{normalized[-2:]}"
