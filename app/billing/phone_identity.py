import sqlite3
from pathlib import Path

from app.audit.hashing import phone_hash
from app.core.config import settings
from app.core.phone_vault import decrypt_phone, encrypt_phone


def _connect():
    db_path = Path(settings.BILLING_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))


def ensure_phone_vault_table() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS phone_vault (
                phone_hash TEXT PRIMARY KEY,
                phone_encrypted TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()


def store_phone(phone: str) -> str:
    from app.billing.repository import _utcnow_iso

    ensure_phone_vault_table()
    hashed = phone_hash(phone)
    encrypted = encrypt_phone(phone)
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO phone_vault (phone_hash, phone_encrypted, created_at)
            VALUES (?, ?, ?)
            ON CONFLICT(phone_hash) DO UPDATE SET phone_encrypted = excluded.phone_encrypted
            """,
            (hashed, encrypted, _utcnow_iso()),
        )
        conn.commit()
    return hashed


def resolve_phone(phone_hash_value: str) -> str | None:
    ensure_phone_vault_table()
    with _connect() as conn:
        row = conn.execute(
            "SELECT phone_encrypted FROM phone_vault WHERE phone_hash = ?",
            (phone_hash_value,),
        ).fetchone()
    if not row:
        return None
    return decrypt_phone(row[0])


def phone_key(phone_or_hash: str) -> str:
    raw = phone_or_hash.strip().replace("whatsapp:", "")
    if raw.startswith("+") or raw.isdigit():
        return store_phone(raw)
    return raw
