import sqlite3
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from pathlib import Path

from app.billing.phone_identity import phone_key, resolve_phone, store_phone
from app.core.config import settings


VALID_STATUSES = {"trial", "active", "past_due", "canceled"}
VALID_SCHOOL_STATUSES = {"active", "past_due", "canceled"}


@dataclass
class StudentSubscription:
    phone: str
    status: str
    trial_ends_at: str | None
    paid_until: str | None
    asaas_customer_id: str | None
    created_at: str
    updated_at: str


@dataclass
class School:
    school_id: str
    name: str
    status: str
    paid_until: str | None
    asaas_customer_id: str | None
    created_at: str
    updated_at: str


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _trial_end_iso(days: int) -> str:
    return (datetime.now(timezone.utc) + timedelta(days=days)).isoformat()


def _connect():
    db_path = Path(settings.BILLING_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(str(db_path))


def ensure_billing_tables() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_subscriptions (
                phone TEXT PRIMARY KEY,
                status TEXT NOT NULL,
                trial_ends_at TEXT,
                paid_until TEXT,
                asaas_customer_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        columns = [row[1] for row in conn.execute("PRAGMA table_info(student_subscriptions)").fetchall()]
        if "asaas_customer_id" not in columns:
            conn.execute("ALTER TABLE student_subscriptions ADD COLUMN asaas_customer_id TEXT")
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS schools (
                school_id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                status TEXT NOT NULL,
                paid_until TEXT,
                asaas_customer_id TEXT,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS school_students (
                school_id TEXT NOT NULL,
                phone TEXT NOT NULL,
                created_at TEXT NOT NULL,
                PRIMARY KEY (school_id, phone),
                FOREIGN KEY (school_id) REFERENCES schools(school_id)
            )
            """
        )
        conn.commit()
    _migrate_legacy_plain_phones()


def _looks_like_plain_phone(value: str) -> bool:
    normalized = value.strip().replace("whatsapp:", "")
    if normalized.startswith("+") or (normalized.isdigit() and len(normalized) >= 8):
        return True
    return len(normalized) != 32


def _migrate_legacy_plain_phones() -> None:
    """Converte telefones em claro (legado) para phone_hash no billing."""
    with _connect() as conn:
        sub_rows = conn.execute("SELECT phone FROM student_subscriptions").fetchall()
        for (legacy_phone,) in sub_rows:
            if not _looks_like_plain_phone(legacy_phone):
                continue
            hashed = store_phone(legacy_phone)
            if hashed == legacy_phone:
                continue
            conn.execute(
                """
                INSERT OR IGNORE INTO student_subscriptions
                (phone, status, trial_ends_at, paid_until, asaas_customer_id, created_at, updated_at)
                SELECT ?, status, trial_ends_at, paid_until, asaas_customer_id, created_at, updated_at
                FROM student_subscriptions WHERE phone = ?
                """,
                (hashed, legacy_phone),
            )
            conn.execute("DELETE FROM student_subscriptions WHERE phone = ?", (legacy_phone,))

        school_rows = conn.execute("SELECT school_id, phone FROM school_students").fetchall()
        for school_id, legacy_phone in school_rows:
            if not _looks_like_plain_phone(legacy_phone):
                continue
            hashed = store_phone(legacy_phone)
            conn.execute("DELETE FROM school_students WHERE school_id = ? AND phone = ?", (school_id, legacy_phone))
            conn.execute(
                """
                INSERT OR IGNORE INTO school_students (school_id, phone, created_at)
                VALUES (?, ?, datetime('now'))
                """,
                (school_id, hashed),
            )
        conn.commit()


def get_or_create_student(phone: str) -> StudentSubscription:
    ensure_billing_tables()
    phone_key = store_phone(phone)
    now = _utcnow_iso()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT phone, status, trial_ends_at, paid_until, asaas_customer_id, created_at, updated_at
            FROM student_subscriptions
            WHERE phone = ?
            """,
            (phone_key,),
        ).fetchone()
        if row:
            return StudentSubscription(*row)

        trial_end = _trial_end_iso(settings.BILLING_TRIAL_DAYS)
        conn.execute(
            """
            INSERT INTO student_subscriptions (phone, status, trial_ends_at, paid_until, asaas_customer_id, created_at, updated_at)
            VALUES (?, 'trial', ?, NULL, NULL, ?, ?)
            """,
            (phone_key, trial_end, now, now),
        )
        conn.commit()
        return StudentSubscription(phone_key, "trial", trial_end, None, None, now, now)


def update_subscription_status(phone: str, status: str, paid_until: str | None = None) -> StudentSubscription:
    if status not in VALID_STATUSES:
        raise ValueError(f"Status invalido: {status}")

    phone_key_val = phone_key(phone)
    ensure_billing_tables()
    current = get_or_create_student(phone)
    now = _utcnow_iso()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE student_subscriptions
            SET status = ?, paid_until = COALESCE(?, paid_until), updated_at = ?
            WHERE phone = ?
            """,
            (status, paid_until, now, phone_key_val),
        )
        conn.commit()
    return StudentSubscription(
        phone=phone_key_val,
        status=status,
        trial_ends_at=current.trial_ends_at,
        paid_until=paid_until or current.paid_until,
        asaas_customer_id=current.asaas_customer_id,
        created_at=current.created_at,
        updated_at=now,
    )


def set_asaas_customer_id(phone: str, asaas_customer_id: str) -> StudentSubscription:
    phone_key_val = phone_key(phone)
    ensure_billing_tables()
    current = get_or_create_student(phone)
    now = _utcnow_iso()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE student_subscriptions
            SET asaas_customer_id = ?, updated_at = ?
            WHERE phone = ?
            """,
            (asaas_customer_id, now, phone_key_val),
        )
        conn.commit()
    return StudentSubscription(
        phone=phone_key_val,
        status=current.status,
        trial_ends_at=current.trial_ends_at,
        paid_until=current.paid_until,
        asaas_customer_id=asaas_customer_id,
        created_at=current.created_at,
        updated_at=now,
    )


def list_student_phones(statuses: list[str] | None = None) -> list[str]:
    ensure_billing_tables()
    with _connect() as conn:
        if statuses:
            placeholders = ",".join("?" for _ in statuses)
            rows = conn.execute(
                f"SELECT phone FROM student_subscriptions WHERE status IN ({placeholders})",
                tuple(statuses),
            ).fetchall()
        else:
            rows = conn.execute("SELECT phone FROM student_subscriptions").fetchall()
    return [resolve_phone(row[0]) or row[0] for row in rows]


def count_students_by_status() -> dict[str, int]:
    ensure_billing_tables()
    with _connect() as conn:
        rows = conn.execute(
            "SELECT status, COUNT(*) FROM student_subscriptions GROUP BY status"
        ).fetchall()
    return {status: count for status, count in rows}


def create_or_update_school(school_id: str, name: str) -> School:
    ensure_billing_tables()
    now = _utcnow_iso()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT school_id, name, status, paid_until, asaas_customer_id, created_at, updated_at
            FROM schools
            WHERE school_id = ?
            """,
            (school_id,),
        ).fetchone()
        if row:
            conn.execute(
                "UPDATE schools SET name = ?, updated_at = ? WHERE school_id = ?",
                (name, now, school_id),
            )
            conn.commit()
            return School(
                school_id=school_id,
                name=name,
                status=row[2],
                paid_until=row[3],
                asaas_customer_id=row[4],
                created_at=row[5],
                updated_at=now,
            )

        conn.execute(
            """
            INSERT INTO schools (school_id, name, status, paid_until, asaas_customer_id, created_at, updated_at)
            VALUES (?, ?, 'past_due', NULL, NULL, ?, ?)
            """,
            (school_id, name, now, now),
        )
        conn.commit()
        return School(school_id, name, "past_due", None, None, now, now)


def get_school(school_id: str) -> School | None:
    ensure_billing_tables()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT school_id, name, status, paid_until, asaas_customer_id, created_at, updated_at
            FROM schools
            WHERE school_id = ?
            """,
            (school_id,),
        ).fetchone()
    if not row:
        return None
    return School(*row)


def set_school_asaas_customer_id(school_id: str, asaas_customer_id: str) -> School:
    ensure_billing_tables()
    current = get_school(school_id)
    if not current:
        raise ValueError("Escola nao encontrada")
    now = _utcnow_iso()
    with _connect() as conn:
        conn.execute(
            "UPDATE schools SET asaas_customer_id = ?, updated_at = ? WHERE school_id = ?",
            (asaas_customer_id, now, school_id),
        )
        conn.commit()
    return School(
        school_id=current.school_id,
        name=current.name,
        status=current.status,
        paid_until=current.paid_until,
        asaas_customer_id=asaas_customer_id,
        created_at=current.created_at,
        updated_at=now,
    )


def update_school_status(school_id: str, status: str, paid_until: str | None = None) -> School:
    if status not in VALID_SCHOOL_STATUSES:
        raise ValueError(f"Status de escola invalido: {status}")
    ensure_billing_tables()
    current = get_school(school_id)
    if not current:
        raise ValueError("Escola nao encontrada")
    now = _utcnow_iso()
    with _connect() as conn:
        conn.execute(
            """
            UPDATE schools
            SET status = ?, paid_until = COALESCE(?, paid_until), updated_at = ?
            WHERE school_id = ?
            """,
            (status, paid_until, now, school_id),
        )
        conn.commit()
    return School(
        school_id=current.school_id,
        name=current.name,
        status=status,
        paid_until=paid_until or current.paid_until,
        asaas_customer_id=current.asaas_customer_id,
        created_at=current.created_at,
        updated_at=now,
    )


def assign_student_to_school(phone: str, school_id: str) -> None:
    phone_key = store_phone(phone)
    ensure_billing_tables()
    if not get_school(school_id):
        raise ValueError("Escola nao encontrada")
    now = _utcnow_iso()
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR REPLACE INTO school_students (school_id, phone, created_at)
            VALUES (?, ?, ?)
            """,
            (school_id, phone_key, now),
        )
        conn.commit()


def get_student_school(phone: str) -> School | None:
    phone_key = store_phone(phone)
    ensure_billing_tables()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT s.school_id, s.name, s.status, s.paid_until, s.asaas_customer_id, s.created_at, s.updated_at
            FROM schools s
            JOIN school_students ss ON ss.school_id = s.school_id
            WHERE ss.phone = ?
            LIMIT 1
            """,
            (phone_key,),
        ).fetchone()
    if not row:
        return None
    return School(*row)
