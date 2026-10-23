import json
import sqlite3
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from app.core.config import settings


@dataclass
class AuditEvent:
    correlation_id: str
    actor_type: str
    actor_id: str
    session_id: str
    action: str
    resource: str
    outcome: str
    metadata: dict[str, Any] | None = None
    langsmith_run_id: str | None = None


@dataclass
class ConsentRecord:
    phone_hash: str
    status: str
    terms_version: str
    created_at: str


def _utcnow_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def _connect() -> sqlite3.Connection:
    db_path = Path(settings.AUDIT_DB_PATH)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(str(db_path))
    conn.execute("PRAGMA journal_mode=WAL")
    return conn


def ensure_audit_tables() -> None:
    with _connect() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS audit_log (
                event_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                correlation_id TEXT NOT NULL,
                actor_type TEXT NOT NULL,
                actor_id TEXT NOT NULL,
                session_id TEXT NOT NULL,
                action TEXT NOT NULL,
                resource TEXT NOT NULL,
                outcome TEXT NOT NULL,
                metadata TEXT,
                langsmith_run_id TEXT
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp
            ON audit_log(timestamp)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_log_correlation
            ON audit_log(correlation_id)
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_audit_log_action
            ON audit_log(action)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS consent_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                phone_hash TEXT NOT NULL,
                status TEXT NOT NULL,
                terms_version TEXT NOT NULL,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE INDEX IF NOT EXISTS idx_consent_log_phone
            ON consent_log(phone_hash, created_at)
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS message_dedup (
                message_id TEXT PRIMARY KEY,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incident_log (
                incident_id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                severity TEXT NOT NULL,
                description TEXT NOT NULL,
                action_taken TEXT,
                reported_by TEXT NOT NULL
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS student_enrollment (
                phone_hash TEXT PRIMARY KEY,
                school_id TEXT NOT NULL,
                student_code TEXT NOT NULL,
                parental_consent_ref TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TEXT NOT NULL,
                updated_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
        cleanup_message_dedup(conn)


def cleanup_message_dedup(conn: sqlite3.Connection | None = None) -> int:
    cutoff = datetime.now(timezone.utc).timestamp() - (settings.MESSAGE_DEDUP_TTL_HOURS * 3600)
    cutoff_iso = datetime.fromtimestamp(cutoff, tz=timezone.utc).isoformat()
    if conn is None:
        with _connect() as local:
            cur = local.execute("DELETE FROM message_dedup WHERE created_at < ?", (cutoff_iso,))
            local.commit()
            return cur.rowcount
    cur = conn.execute("DELETE FROM message_dedup WHERE created_at < ?", (cutoff_iso,))
    return cur.rowcount


def ensure_enrollment_tables() -> None:
    ensure_audit_tables()


def upsert_enrollment(
    *,
    phone_hash: str,
    school_id: str,
    student_code: str,
    parental_consent_ref: str,
    status: str,
) -> None:
    ensure_enrollment_tables()
    now = _utcnow_iso()
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO student_enrollment (
                phone_hash, school_id, student_code, parental_consent_ref, status, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(phone_hash) DO UPDATE SET
                school_id = excluded.school_id,
                student_code = excluded.student_code,
                parental_consent_ref = excluded.parental_consent_ref,
                status = excluded.status,
                updated_at = excluded.updated_at
            """,
            (phone_hash, school_id, student_code, parental_consent_ref, status, now, now),
        )
        conn.commit()


def get_enrollment(phone_hash: str) -> dict[str, Any] | None:
    ensure_enrollment_tables()
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT phone_hash, school_id, student_code, parental_consent_ref, status, created_at, updated_at
            FROM student_enrollment
            WHERE phone_hash = ?
            """,
            (phone_hash,),
        ).fetchone()
    if not row:
        return None
    return {
        "phone_hash": row[0],
        "school_id": row[1],
        "student_code": row[2],
        "parental_consent_ref": row[3],
        "status": row[4],
        "created_at": row[5],
        "updated_at": row[6],
    }


def append_incident(severity: str, description: str, action_taken: str, reported_by: str) -> str:
    ensure_audit_tables()
    incident_id = str(uuid.uuid4())
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO incident_log (incident_id, timestamp, severity, description, action_taken, reported_by)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (incident_id, _utcnow_iso(), severity, description, action_taken, reported_by),
        )
        conn.commit()
    return incident_id


def append_audit_log(event: AuditEvent) -> str:
    event_id = str(uuid.uuid4())
    metadata_json = json.dumps(event.metadata or {}, ensure_ascii=False)
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO audit_log (
                event_id, timestamp, correlation_id, actor_type, actor_id,
                session_id, action, resource, outcome, metadata, langsmith_run_id
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                event_id,
                _utcnow_iso(),
                event.correlation_id,
                event.actor_type,
                event.actor_id,
                event.session_id,
                event.action,
                event.resource,
                event.outcome,
                metadata_json,
                event.langsmith_run_id,
            ),
        )
        conn.commit()
    return event_id


def append_consent_log(phone_hash: str, status: str, terms_version: str) -> None:
    with _connect() as conn:
        conn.execute(
            """
            INSERT INTO consent_log (phone_hash, status, terms_version, created_at)
            VALUES (?, ?, ?, ?)
            """,
            (phone_hash, status, terms_version, _utcnow_iso()),
        )
        conn.commit()


def get_latest_consent(phone_hash: str) -> ConsentRecord | None:
    with _connect() as conn:
        row = conn.execute(
            """
            SELECT phone_hash, status, terms_version, created_at
            FROM consent_log
            WHERE phone_hash = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (phone_hash,),
        ).fetchone()
    if not row:
        return None
    return ConsentRecord(
        phone_hash=row[0],
        status=row[1],
        terms_version=row[2],
        created_at=row[3],
    )


def is_message_processed(message_id: str) -> bool:
    if not message_id:
        return False
    with _connect() as conn:
        row = conn.execute(
            "SELECT 1 FROM message_dedup WHERE message_id = ?",
            (message_id,),
        ).fetchone()
    return row is not None


def mark_message_processed(message_id: str) -> None:
    if not message_id:
        return
    with _connect() as conn:
        conn.execute(
            """
            INSERT OR IGNORE INTO message_dedup (message_id, created_at)
            VALUES (?, ?)
            """,
            (message_id, _utcnow_iso()),
        )
        conn.commit()


def fetch_audit_logs(
    date_from: str | None = None,
    date_to: str | None = None,
    action: str | None = None,
    limit: int = 10_000,
    correlation_id: str | None = None,
    newest_first: bool = False,
) -> list[dict[str, Any]]:
    query = "SELECT event_id, timestamp, correlation_id, actor_type, actor_id, session_id, action, resource, outcome, metadata, langsmith_run_id FROM audit_log WHERE 1=1"
    params: list[Any] = []
    if date_from:
        query += " AND timestamp >= ?"
        params.append(date_from)
    if date_to:
        query += " AND timestamp <= ?"
        params.append(date_to)
    if action:
        query += " AND action = ?"
        params.append(action)
    if correlation_id:
        query += " AND correlation_id = ?"
        params.append(correlation_id)
    # newest_first: LIMIT pega os N mais recentes (painel); senão, ordem cronológica.
    query += f" ORDER BY timestamp {'DESC' if newest_first else 'ASC'} LIMIT ?"
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()

    results: list[dict[str, Any]] = []
    for row in rows:
        results.append(
            {
                "event_id": row[0],
                "timestamp": row[1],
                "correlation_id": row[2],
                "actor_type": row[3],
                "actor_id": row[4],
                "session_id": row[5],
                "action": row[6],
                "resource": row[7],
                "outcome": row[8],
                "metadata": json.loads(row[9] or "{}"),
                "langsmith_run_id": row[10],
            }
        )
    return results


def fetch_consent_logs(
    date_from: str | None = None,
    date_to: str | None = None,
    limit: int = 10_000,
) -> list[dict[str, Any]]:
    query = "SELECT phone_hash, status, terms_version, created_at FROM consent_log WHERE 1=1"
    params: list[Any] = []
    if date_from:
        query += " AND created_at >= ?"
        params.append(date_from)
    if date_to:
        query += " AND created_at <= ?"
        params.append(date_to)
    query += " ORDER BY created_at ASC LIMIT ?"
    params.append(limit)

    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()

    return [
        {
            "phone_hash": row[0],
            "status": row[1],
            "terms_version": row[2],
            "created_at": row[3],
        }
        for row in rows
    ]
