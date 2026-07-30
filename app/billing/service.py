from datetime import datetime, timezone

from app.billing.repository import (
    School,
    StudentSubscription,
    assign_student_to_school,
    create_or_update_school,
    ensure_billing_tables,
    get_school,
    get_or_create_student,
    get_student_school,
    update_school_status,
    update_subscription_status,
)
from app.core.config import settings


def init_billing() -> None:
    ensure_billing_tables()


def _parse_iso(dt: str | None):
    if not dt:
        return None
    return datetime.fromisoformat(dt)


def has_active_access(phone: str) -> tuple[bool, StudentSubscription]:
    student = get_or_create_student(phone)

    if not settings.BILLING_ENFORCE_SUBSCRIPTION:
        return True, student

    school = get_student_school(phone)
    if school and school.status == "active":
        paid_until_school = _parse_iso(school.paid_until)
        if paid_until_school is None or paid_until_school > datetime.now(timezone.utc):
            return True, student

    if student.status == "active":
        paid_until = _parse_iso(student.paid_until)
        if paid_until is None or paid_until > datetime.now(timezone.utc):
            return True, student
        return False, student

    if student.status == "trial":
        trial_end = _parse_iso(student.trial_ends_at)
        if trial_end and trial_end > datetime.now(timezone.utc):
            return True, student
        return False, student

    return False, student


def payment_instructions_message() -> str:
    return (
        "Sua assinatura do deepEdu nao esta ativa no momento. "
        "Para continuar, solicite seu link de pagamento ao suporte/professor. "
        "Se voce ja pagou, aguarde alguns minutos e tente novamente."
    )


def payment_instructions_with_link(checkout_url: str | None) -> str:
    if checkout_url:
        return (
            "Sua assinatura do deepEdu nao esta ativa no momento.\n"
            "Voce pode pagar por PIX, boleto ou cartao no link abaixo:\n"
            f"{checkout_url}\n"
            "Assim que o pagamento for confirmado, seu acesso sera liberado automaticamente."
        )
    return payment_instructions_message()


def activate_student_subscription(phone: str, paid_until_iso: str | None = None):
    return update_subscription_status(phone=phone, status="active", paid_until=paid_until_iso)


def create_school(school_id: str, name: str) -> School:
    return create_or_update_school(school_id=school_id, name=name)


def add_student_to_school(phone: str, school_id: str) -> None:
    assign_student_to_school(phone=phone, school_id=school_id)


def activate_school_plan(school_id: str, paid_until_iso: str | None = None) -> School:
    return update_school_status(school_id=school_id, status="active", paid_until=paid_until_iso)


def get_school_for_student(phone: str) -> School | None:
    return get_student_school(phone)


def get_school_by_id(school_id: str) -> School | None:
    return get_school(school_id)
