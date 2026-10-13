from app.billing.repository import count_students_by_status


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
