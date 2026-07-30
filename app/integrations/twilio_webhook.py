import unicodedata
import uuid

from fastapi import Form, HTTPException, Request
from fastapi.responses import PlainTextResponse
from twilio.request_validator import RequestValidator
from twilio.twiml.messaging_response import MessagingResponse

from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.audit.repository import is_message_processed, mark_message_processed
from app.audit.service import AuditLogError, log_event
from app.billing.admin_service import broadcast_to_students, professor_status_summary
from app.billing.payment_service import create_checkout_for_student_phone
from app.billing.service import has_active_access, payment_instructions_with_link
from app.core.config import settings
from app.integrations.message_flow import build_answer_for_message


def validate_twilio_signature(request: Request, form_data: dict) -> bool:
    if not settings.TWILIO_VALIDATE_SIGNATURE:
        return True
    signature = request.headers.get("X-Twilio-Signature", "")
    validator = RequestValidator(settings.TWILIO_AUTH_TOKEN)
    return validator.validate(str(request.url), form_data, signature)


def _normalize_text(text: str) -> str:
    normalized = unicodedata.normalize("NFKD", text)
    without_accents = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    return without_accents.lower().strip()


def _extract_billing_type_from_text(text: str) -> str | None:
    normalized = _normalize_text(text)
    if "pix" in normalized:
        return "PIX"
    if "boleto" in normalized:
        return "BOLETO"
    if "cartao" in normalized or "credito" in normalized:
        return "CREDIT_CARD"
    return None


def _is_payment_command(text: str) -> bool:
    normalized = _normalize_text(text)
    return any(
        token in normalized
        for token in ["pagar", "pagamento", "assinar", "assinatura", "plano", "comprar"]
    )


def _is_status_command(text: str) -> bool:
    normalized = _normalize_text(text)
    return any(token in normalized for token in ["status", "acesso", "assinatura", "plano"])


def _help_message() -> str:
    return (
        "Bem-vindo ao deepEdu.\n"
        "Comandos rapidos:\n"
        "- ajuda (mostra este menu)\n"
        "- pagar (gera link com opcoes)\n"
        "- pagar pix\n"
        "- pagar boleto\n"
        "- pagar cartao\n"
        "- status\n"
        "- SAIR (revoga consentimento e apaga historico)\n"
        "Ou envie sua duvida da materia normalmente."
    )


def _build_checkout_message(phone: str, requested_method: str | None = None) -> str:
    checkout_data = create_checkout_for_student_phone(phone=phone, billing_type=requested_method)
    checkout_url = checkout_data.get("invoice_url")
    billing_type = checkout_data.get("billing_type", "UNDEFINED")
    if billing_type == "UNDEFINED":
        method_desc = "PIX, boleto ou cartao"
    elif billing_type == "CREDIT_CARD":
        method_desc = "cartao de credito"
    elif billing_type == "BOLETO":
        method_desc = "boleto"
    else:
        method_desc = "PIX"

    return (
        f"Aqui esta seu link de pagamento ({method_desc}):\n"
        f"{checkout_url}\n"
        "Apos a confirmacao, seu acesso sera liberado automaticamente."
    )


def _is_help_command(text: str) -> bool:
    normalized = _normalize_text(text)
    return any(token in normalized for token in ["ajuda", "menu", "comandos", "help"])


def _is_professor_number(phone: str) -> bool:
    raw = settings.PROFESSOR_WHATSAPP_NUMBERS.strip()
    if not raw:
        return False
    allowed = {item.strip() for item in raw.split(",") if item.strip()}
    return phone in allowed


def _is_professor_command(text: str) -> bool:
    normalized = _normalize_text(text)
    return normalized.startswith("professor")


def _professor_help_message() -> str:
    return (
        "Menu professor:\n"
        "- professor ajuda\n"
        "- professor status\n"
        "- professor aviso <mensagem>\n"
        "Exemplo: professor aviso Prova de matematica amanha as 10h."
    )


def _handle_professor_command(phone: str, question: str) -> str:
    normalized = _normalize_text(question)
    if not _is_professor_number(phone):
        return "Este comando e exclusivo para numeros de professores autorizados."

    parts = normalized.split(maxsplit=2)
    if len(parts) == 1 or parts[1] in {"ajuda", "menu"}:
        return _professor_help_message()

    command = parts[1]
    if command == "status":
        return professor_status_summary()

    if command == "aviso":
        original_parts = question.split(maxsplit=2)
        if len(original_parts) < 3 or not original_parts[2].strip():
            return "Use: professor aviso <mensagem>"
        message = f"[Aviso do Professor]\n{original_parts[2].strip()}"
        report = broadcast_to_students(message=message, statuses=["active", "trial"])
        return (
            "Aviso enviado.\n"
            f"Alvos: {report['targeted']} | Enviados: {report['sent']} | Falhas: {report['failed']}"
        )

    return _professor_help_message()


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


async def handle_incoming_whatsapp(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(default=""),
):
    correlation_id = str(uuid.uuid4())
    form_data = {"From": From, "Body": Body, "MessageSid": MessageSid}

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
