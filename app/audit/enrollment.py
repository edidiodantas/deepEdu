from __future__ import annotations

import uuid

from app.audit.hashing import phone_hash
from app.audit.repository import (
    ensure_enrollment_tables,
    get_enrollment,
    upsert_enrollment,
)
from app.audit.service import log_event


def enrollment_prompt() -> str:
    return (
        "Para usar o tutor, sua matricula precisa estar vinculada.\n"
        "Envie: VINCULAR <seu codigo de matricula>\n"
        "O codigo foi fornecido pela escola aos responsaveis.\n"
        "Duvidas: secretaria da escola."
    )


def is_enrollment_command(text: str) -> bool:
    return text.strip().upper().startswith("VINCULAR")


def parse_enrollment_code(text: str) -> str | None:
    parts = text.strip().split(maxsplit=1)
    if len(parts) != 2:
        return None
    return parts[1].strip().upper()


def has_active_enrollment(phone: str) -> bool:
    record = get_enrollment(phone_hash(phone))
    return record is not None and record.get("status") == "verified"


def verify_enrollment(
    *,
    phone: str,
    student_code: str,
    correlation_id: str,
    session_id: str,
) -> tuple[bool, str]:
    hashed = phone_hash(phone)
    record = get_enrollment(hashed)
    if not record:
        return False, "Matricula nao encontrada. Peca a escola para cadastrar seu codigo."
    if record["student_code"].upper() != student_code.upper():
        return False, "Codigo de matricula invalido. Tente novamente ou fale com a secretaria."
    upsert_enrollment(
        phone_hash=hashed,
        school_id=record["school_id"],
        student_code=student_code.upper(),
        parental_consent_ref=record.get("parental_consent_ref"),
        status="verified",
    )
    log_event(
        correlation_id=correlation_id,
        actor_type="student",
        actor_id=hashed,
        session_id=session_id,
        action="enrollment.verified",
        resource=f"school:{record['school_id']}",
        outcome="success",
        metadata={"student_code": student_code.upper()},
        fail_closed=True,
    )
    return True, (
        "Matricula vinculada com sucesso.\n"
        "Agora responda ACEITO para confirmar o uso do tutor conforme a politica da escola."
    )


def admin_enroll_student(
    *,
    phone: str,
    school_id: str,
    student_code: str,
    parental_consent_ref: str,
    correlation_id: str | None = None,
) -> None:
    ensure_enrollment_tables()
    hashed = phone_hash(phone)
    upsert_enrollment(
        phone_hash=hashed,
        school_id=school_id,
        student_code=student_code.upper(),
        parental_consent_ref=parental_consent_ref,
        status="pending",
    )
    log_event(
        correlation_id=correlation_id or str(uuid.uuid4()),
        actor_type="admin",
        actor_id="admin",
        session_id="admin",
        action="enrollment.created",
        resource=f"student:{hashed}",
        outcome="success",
        metadata={
            "school_id": school_id,
            "student_code": student_code.upper(),
            "parental_consent_ref": parental_consent_ref,
        },
    )
