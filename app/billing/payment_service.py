from datetime import datetime, timedelta, timezone

from app.billing.asaas_client import AsaasClient
from app.billing.phone_identity import phone_key, store_phone
from app.billing.repository import (
    create_or_update_school,
    get_or_create_student,
    set_school_asaas_customer_id,
    set_asaas_customer_id,
    update_school_status,
    update_subscription_status,
)
from app.core.config import settings

VALID_BILLING_TYPES = {"PIX", "BOLETO", "CREDIT_CARD", "UNDEFINED"}


def _normalize_billing_type(billing_type: str | None) -> str:
    raw = (billing_type or settings.ASAAS_DEFAULT_BILLING_TYPE or "UNDEFINED").strip().upper()
    if raw not in VALID_BILLING_TYPES:
        raise ValueError(
            f"billing_type invalido: {raw}. Use um de {', '.join(sorted(VALID_BILLING_TYPES))}"
        )
    return raw


def create_checkout(
    phone: str,
    name: str,
    cpf_cnpj: str | None = None,
    email: str | None = None,
    billing_type: str | None = None,
):
    student = get_or_create_student(phone)
    client = AsaasClient()
    chosen_billing_type = _normalize_billing_type(billing_type)

    customer_id = student.asaas_customer_id
    if not customer_id:
        customer = client.create_customer(name=name, cpf_cnpj=cpf_cnpj, phone=phone, email=email)
        customer_id = customer["id"]
        set_asaas_customer_id(phone=phone, asaas_customer_id=customer_id)

    charge = client.create_charge(
        customer_id=customer_id,
        value=settings.ASAAS_BILLING_AMOUNT,
        billing_type=chosen_billing_type,
        external_reference=store_phone(phone),
    )

    return {
        "phone": phone,
        "customer_id": customer_id,
        "payment_id": charge.get("id"),
        "invoice_url": charge.get("invoiceUrl"),
        "pix_qr_code": (charge.get("pixTransaction") or {}).get("qrCode", None),
        "value": charge.get("value"),
        "status": charge.get("status"),
        "billing_type": chosen_billing_type,
    }


def create_checkout_for_student_phone(phone: str, billing_type: str | None = None):
    display_name = f"Aluno {phone}"
    return create_checkout(
        phone=phone,
        name=display_name,
        billing_type=billing_type or settings.ASAAS_DEFAULT_BILLING_TYPE,
    )


def _paid_until_iso():
    return (datetime.now(timezone.utc) + timedelta(days=settings.BILLING_PLAN_DAYS)).isoformat()


def _school_paid_until_iso():
    return (datetime.now(timezone.utc) + timedelta(days=settings.SCHOOL_PLAN_DAYS)).isoformat()


def process_asaas_webhook(payload: dict):
    event = payload.get("event", "")
    payment = payload.get("payment", {}) or {}
    reference = payment.get("externalReference")
    if not reference:
        return {"ok": False, "reason": "externalReference ausente"}

    if reference.startswith("school:"):
        school_id = reference.split(":", 1)[1]
        if event in {"PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"}:
            school = update_school_status(school_id=school_id, status="active", paid_until=_school_paid_until_iso())
            return {"ok": True, "school_id": school.school_id, "status": school.status, "event": event}
        if event in {"PAYMENT_OVERDUE", "PAYMENT_DELETED"}:
            school = update_school_status(school_id=school_id, status="past_due")
            return {"ok": True, "school_id": school.school_id, "status": school.status, "event": event}
        if event in {"PAYMENT_REFUNDED", "PAYMENT_CHARGEBACK_REQUESTED"}:
            school = update_school_status(school_id=school_id, status="canceled")
            return {"ok": True, "school_id": school.school_id, "status": school.status, "event": event}
        return {"ok": True, "ignored": True, "event": event, "school_id": school_id}

    phone_ref = phone_key(reference)

    if event in {"PAYMENT_CONFIRMED", "PAYMENT_RECEIVED"}:
        student = update_subscription_status(phone=phone_ref, status="active", paid_until=_paid_until_iso())
        return {"ok": True, "phone": student.phone, "status": student.status, "event": event}

    if event in {"PAYMENT_OVERDUE", "PAYMENT_DELETED"}:
        student = update_subscription_status(phone=phone_ref, status="past_due")
        return {"ok": True, "phone": student.phone, "status": student.status, "event": event}

    if event in {"PAYMENT_REFUNDED", "PAYMENT_CHARGEBACK_REQUESTED"}:
        student = update_subscription_status(phone=phone_ref, status="canceled")
        return {"ok": True, "phone": student.phone, "status": student.status, "event": event}

    return {"ok": True, "ignored": True, "event": event, "phone": phone_ref}


def create_school_checkout(school_id: str, school_name: str, cpf_cnpj: str | None = None, email: str | None = None):
    school = create_or_update_school(school_id=school_id, name=school_name)
    client = AsaasClient()

    customer_id = school.asaas_customer_id
    if not customer_id:
        customer = client.create_customer(name=school_name, cpf_cnpj=cpf_cnpj, phone="", email=email)
        customer_id = customer["id"]
        set_school_asaas_customer_id(school_id=school_id, asaas_customer_id=customer_id)

    charge = client.create_charge(
        customer_id=customer_id,
        value=settings.SCHOOL_PLAN_AMOUNT,
        billing_type="UNDEFINED",
        external_reference=f"school:{school_id}",
    )
    return {
        "school_id": school_id,
        "school_name": school_name,
        "customer_id": customer_id,
        "payment_id": charge.get("id"),
        "invoice_url": charge.get("invoiceUrl"),
        "value": charge.get("value"),
        "status": charge.get("status"),
        "billing_type": "UNDEFINED",
    }
