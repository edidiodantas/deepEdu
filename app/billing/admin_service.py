from app.billing.repository import count_students_by_status, list_student_phones
from app.integrations.twilio_outbound import send_whatsapp_message


def professor_status_summary() -> str:
    counts = count_students_by_status()
    trial = counts.get("trial", 0)
    active = counts.get("active", 0)
    past_due = counts.get("past_due", 0)
    canceled = counts.get("canceled", 0)
    total = trial + active + past_due + canceled
    return (
        "Resumo de assinaturas:\n"
        f"- total: {total}\n"
        f"- active: {active}\n"
        f"- trial: {trial}\n"
        f"- past_due: {past_due}\n"
        f"- canceled: {canceled}"
    )


def broadcast_to_students(message: str, statuses: list[str] | None = None) -> dict:
    target_statuses = statuses or ["active", "trial"]
    phones = list_student_phones(statuses=target_statuses)
    sent = 0
    failed = 0
    failures = []
    for phone in phones:
        try:
            send_whatsapp_message(phone, message)
            sent += 1
        except Exception as exc:
            failed += 1
            failures.append({"phone": phone, "error": str(exc)})
    return {
        "targeted": len(phones),
        "sent": sent,
        "failed": failed,
        "statuses": target_statuses,
        "failures": failures[:5],
    }
