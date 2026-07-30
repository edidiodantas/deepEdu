from app.audit.consent import (
    consent_denied_message,
    consent_prompt,
    grant_consent,
    has_active_consent,
    is_consent_accept_command,
    is_optout_command,
    optout_confirmation,
    revoke_consent,
)
from app.audit.enrollment import (
    enrollment_prompt,
    has_active_enrollment,
    is_enrollment_command,
    parse_enrollment_code,
    verify_enrollment,
)
from app.billing.service import has_active_access, payment_instructions_with_link
from app.services.tutor_service import answer_question
from app.integrations.twilio_webhook import (
    _build_checkout_message,
    _extract_billing_type_from_text,
    _handle_professor_command,
    _help_message,
    _is_help_command,
    _is_payment_command,
    _is_professor_command,
    _is_status_command,
)


def build_answer_for_message(
    *,
    phone: str,
    question: str,
    correlation_id: str,
    session_id: str,
) -> str:
    if is_optout_command(question):
        revoke_consent(phone=phone, correlation_id=correlation_id, session_id=session_id)
        return optout_confirmation()
    if _is_professor_command(question):
        return _handle_professor_command(phone=phone, question=question)
    if is_enrollment_command(question):
        code = parse_enrollment_code(question)
        if not code:
            return "Use: VINCULAR <seu codigo de matricula>"
        _, msg = verify_enrollment(
            phone=phone,
            student_code=code,
            correlation_id=correlation_id,
            session_id=session_id,
        )
        return msg
    if not has_active_enrollment(phone):
        return enrollment_prompt()
    if is_consent_accept_command(question):
        grant_consent(phone=phone, correlation_id=correlation_id, session_id=session_id)
        return (
            "Consentimento registrado. Obrigado!\n"
            "Agora pode enviar sua duvida de Matematica que eu te ajudo."
        )
    if not has_active_consent(phone):
        return consent_prompt() if question else consent_denied_message()
    if not question:
        return _help_message()
    if _is_help_command(question):
        return _help_message()

    has_access, _ = has_active_access(phone)
    requested_method = _extract_billing_type_from_text(question)
    if _is_payment_command(question):
        try:
            return _build_checkout_message(phone=phone, requested_method=requested_method)
        except Exception:
            return payment_instructions_with_link(checkout_url=None)
    if _is_status_command(question) and not has_access:
        try:
            return _build_checkout_message(phone=phone, requested_method=None)
        except Exception:
            return payment_instructions_with_link(checkout_url=None)
    if _is_status_command(question) and has_access:
        return "Seu acesso esta ativo.\nPode enviar sua pergunta da materia que eu te ajudo agora."
    if not has_access:
        try:
            return _build_checkout_message(phone=phone, requested_method=None)
        except Exception:
            return payment_instructions_with_link(checkout_url=None)
    return answer_question(phone=phone, question=question, correlation_id=correlation_id)
