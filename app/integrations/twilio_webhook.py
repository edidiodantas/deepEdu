import uuid

from fastapi import HTTPException, Request
from fastapi.responses import PlainTextResponse
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.audit.repository import is_message_processed, mark_message_processed
from app.audit.service import AuditLogError, log_event
from app.core.config import settings
from app.integrations.message_flow import build_answer_for_message


def validate_twilio_signature(request: Request, form_data: dict) -> bool:
    if not settings.TWILIO_VALIDATE_SIGNATURE:
        return True
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    return validator.validate(str(request.url), form_data, signature)


def _audit_fail_response() -> PlainTextResponse:
    twiml = MessagingResponse()
    twiml.message(
        "Servico temporariamente indisponivel por motivos de seguranca.\n"
        "Tente novamente em alguns minutos ou fale com a escola."
    )
    return PlainTextResponse(str(twiml), media_type="application/xml")


def _respond(answer: str) -> PlainTextResponse:
    twiml = MessagingResponse()
    twiml.message(answer)
    return PlainTextResponse(str(twiml), media_type="application/xml")


async def handle_incoming_whatsapp(request: Request):
    correlation_id = str(uuid.uuid4())
    form = await request.form()
    form_data = {str(key): str(value) for key, value in form.items()}
    From = form_data.get("From", "")
    Body = form_data.get("Body", "")
    MessageSid = form_data.get("MessageSid", "")

    log_event(
        correlation_id=correlation_id,
        actor_type="webhook",
        actor_id="twilio",
        session_id="webhook",
        action="webhook.received",
        resource="whatsapp",
        outcome="success",
        metadata={"has_message_sid": bool(MessageSid)},
        fail_closed=settings.AUDIT_FAIL_CLOSED,
    )

    if not validate_twilio_signature(request, form_data):
        log_event(
            correlation_id=correlation_id,
            actor_type="webhook",
            actor_id="twilio",
            session_id="webhook",
            action="webhook.signature_invalid",
            resource="whatsapp",
            outcome="denied",
        )
        raise HTTPException(status_code=403, detail="Assinatura Twilio invalida")

    if MessageSid and is_message_processed(MessageSid):
        log_event(
            correlation_id=correlation_id,
            actor_type="webhook",
            actor_id="twilio",
            session_id="webhook",
            action="message.duplicate_skipped",
            resource=f"message:{MessageSid}",
            outcome="success",
        )
        return _respond("")

    phone = From.replace("whatsapp:", "").strip()
    question = Body.strip()
    hashed = phone_hash(phone)
    session_id = pseudonymize_session_id(phone)

    log_event(
        correlation_id=correlation_id,
        actor_type="student",
        actor_id=hashed,
        session_id=session_id,
        action="message.received",
        resource="whatsapp",
        outcome="success",
        metadata={"body_length": len(question), "message_sid": MessageSid or None},
        fail_closed=settings.AUDIT_FAIL_CLOSED,
    )

    try:
        answer = build_answer_for_message(
            phone=phone,
            question=question,
            correlation_id=correlation_id,
            session_id=session_id,
        )

        log_event(
            correlation_id=correlation_id,
            actor_type="student",
            actor_id=hashed,
            session_id=session_id,
            action="message.sent",
            resource="whatsapp",
            outcome="success",
            metadata={"answer_length": len(answer)},
            fail_closed=settings.AUDIT_FAIL_CLOSED,
        )
    except AuditLogError:
        return _audit_fail_response()

    if MessageSid:
        mark_message_processed(MessageSid)

    return _respond(answer)
