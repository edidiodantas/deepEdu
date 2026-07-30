from fastapi import APIRouter, Depends
from fastapi.responses import PlainTextResponse

from app.audit.admin_audit import audited_admin_action
from app.audit.enrollment import admin_enroll_student
from app.audit.hashing import phone_hash
from app.audit.repository import append_incident, fetch_audit_logs, fetch_consent_logs
from app.billing.phone_identity import store_phone
from app.billing.payment_service import (
    VALID_BILLING_TYPES,
    create_checkout,
    create_school_checkout,
)
from app.billing.repository import VALID_STATUSES
from app.billing.service import (
    activate_school_plan,
    activate_student_subscription,
    add_student_to_school,
    create_school,
    get_school_for_student,
)
from app.core.security import require_admin_api_key

router = APIRouter(prefix="/admin", tags=["admin"], dependencies=[Depends(require_admin_api_key)])


@router.post("/billing/activate")
@audited_admin_action("admin.billing.activate", "billing")
def activate_subscription(phone: str, paid_until_iso: str | None = None):
    student = activate_student_subscription(phone=phone, paid_until_iso=paid_until_iso)
    return {"ok": True, "phone": student.phone, "status": student.status, "paid_until": student.paid_until}


@router.get("/billing/statuses")
def list_statuses():
    return {"allowed_statuses": sorted(list(VALID_STATUSES))}


@router.post("/billing/checkout")
@audited_admin_action("admin.billing.checkout", "billing")
def create_checkout_link(
    phone: str,
    name: str,
    cpf_cnpj: str | None = None,
    email: str | None = None,
    billing_type: str | None = None,
):
    data = create_checkout(
        phone=phone,
        name=name,
        cpf_cnpj=cpf_cnpj,
        email=email,
        billing_type=billing_type,
    )
    return {"ok": True, **data}


@router.get("/billing/payment-methods")
def list_payment_methods():
    return {"methods": sorted(list(VALID_BILLING_TYPES))}


@router.post("/schools")
@audited_admin_action("admin.school.create", "school")
def create_school_record(school_id: str, name: str):
    school = create_school(school_id=school_id, name=name)
    return {"ok": True, "school_id": school.school_id, "name": school.name, "status": school.status}


@router.post("/schools/assign-student")
@audited_admin_action("admin.school.assign_student", "school")
def assign_student(phone: str, school_id: str):
    add_student_to_school(phone=phone, school_id=school_id)
    school = get_school_for_student(phone=phone)
    return {"ok": True, "phone": phone, "school_id": school.school_id if school else None}


@router.post("/schools/activate")
@audited_admin_action("admin.school.activate", "school")
def activate_school_subscription(school_id: str, paid_until_iso: str | None = None):
    school = activate_school_plan(school_id=school_id, paid_until_iso=paid_until_iso)
    return {"ok": True, "school_id": school.school_id, "status": school.status, "paid_until": school.paid_until}


@router.post("/schools/checkout")
@audited_admin_action("admin.school.checkout", "school")
def school_checkout(
    school_id: str,
    school_name: str,
    cpf_cnpj: str | None = None,
    email: str | None = None,
):
    data = create_school_checkout(
        school_id=school_id,
        school_name=school_name,
        cpf_cnpj=cpf_cnpj,
        email=email,
    )
    return {"ok": True, **data}


@router.get("/audit/export")
def export_audit_csv(
    date_from: str | None = None,
    date_to: str | None = None,
    include_consent: bool = True,
):
    import csv
    import io

    audit_rows = fetch_audit_logs(date_from=date_from, date_to=date_to)
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(
        [
            "event_id",
            "timestamp",
            "correlation_id",
            "actor_type",
            "actor_id",
            "session_id",
            "action",
            "resource",
            "outcome",
            "metadata",
            "langsmith_run_id",
        ]
    )
    for row in audit_rows:
        writer.writerow(
            [
                row["event_id"],
                row["timestamp"],
                row["correlation_id"],
                row["actor_type"],
                row["actor_id"],
                row["session_id"],
                row["action"],
                row["resource"],
                row["outcome"],
                str(row["metadata"]),
                row.get("langsmith_run_id") or "",
            ]
        )
    if include_consent:
        writer.writerow([])
        writer.writerow(["phone_hash", "status", "terms_version", "created_at"])
        for row in fetch_consent_logs(date_from=date_from, date_to=date_to):
            writer.writerow([row["phone_hash"], row["status"], row["terms_version"], row["created_at"]])
    return PlainTextResponse(output.getvalue(), media_type="text/csv")


@router.get("/audit/logs")
def list_audit_logs(limit: int = 200, action: str | None = None):
    return {"items": fetch_audit_logs(action=action, limit=limit)}


@router.post("/students/enroll")
@audited_admin_action("admin.enrollment.create", "enrollment")
def enroll_student(
    phone: str,
    school_id: str,
    student_code: str,
    parental_consent_ref: str,
):
    store_phone(phone)
    admin_enroll_student(
        phone=phone,
        school_id=school_id,
        student_code=student_code,
        parental_consent_ref=parental_consent_ref,
    )
    return {"ok": True, "phone_hash": phone_hash(phone)}


@router.post("/incidents")
@audited_admin_action("admin.incident.report", "incident")
def report_incident(severity: str, description: str, action_taken: str = ""):
    incident_id = append_incident(
        severity=severity,
        description=description,
        action_taken=action_taken,
        reported_by="admin",
    )
    return {"ok": True, "incident_id": incident_id}
