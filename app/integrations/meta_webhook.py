import hashlib
import hmac
import json
import uuid

import httpx
from fastapi import HTTPException, Request
from fastapi.responses import PlainTextResponse

from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.audit.repository import is_message_processed, mark_message_processed
from app.audit.service import AuditLogError, log_event
from app.core.config import settings
from app.integrations.message_flow import build_answer_for_message


def _validate_meta_signature(request: Request, body: bytes) -> bool:
    secret = settings.META_APP_SECRET.strip()
    if not secret:
        return settings.ENV != "production"
    signature = request.headers.get("X-Hub-Signature-256", "")
    if not signature.startswith("sha256="):
        return False
    digest = hmac.new(secret.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(signature, f"sha256={digest}")


async def handle_meta_verification(request: Request):
    params = request.query_params
    if params.get("hub.mode") == "subscribe" and params.get("hub.verify_token") == settings.META_VERIFY_TOKEN:
        return PlainTextResponse(params.get("hub.challenge", ""))
    raise HTTPException(status_code=403, detail="Verificacao Meta invalida")


async def _send_meta_text(to_phone: str, text: str) -> bool:
    if not settings.META_ACCESS_TOKEN or not settings.META_PHONE_NUMBER_ID:
        return False
    url = f"https://graph.facebook.com/v20.0/{settings.META_PHONE_NUMBER_ID}/messages"
    headers = {"Authorization": f"Bearer {settings.META_ACCESS_TOKEN}"}
    payload = {
        "messaging_product": "whatsapp",
        "to": to_phone.replace("whatsapp:", "").replace("+", ""),
        "type": "text",
        "text": {"body": text[:4096]},
    }
    async with httpx.AsyncClient(timeout=20) as client:
        response = await client.post(url, headers=headers, json=payload)
    return response.is_success


async def handle_meta_webhook(request: Request):
    body = await request.body()
    correlation_id = str(uuid.uuid4())
    log_event(
        correlation_id=correlation_id,
        actor_type="webhook",
        actor_id="meta",
        session_id="webhook",
        action="webhook.received",
        resource="whatsapp_meta",
        outcome="success",
    )
    if not _validate_meta_signature(request, body):
        log_event(
            correlation_id=correlation_id,
            actor_type="webhook",
            actor_id="meta",
            session_id="webhook",
            action="webhook.signature_invalid",
            resource="whatsapp_meta",
            outcome="denied",
        )
        raise HTTPException(status_code=403, detail="Assinatura Meta invalida")

    payload = json.loads(body.decode("utf-8"))
    for entry in payload.get("entry", []):
        for change in entry.get("changes", []):
            for message in change.get("value", {}).get("messages", []):
                if message.get("type") not in (None, "text"):
                    continue
                phone = f"+{message.get('from', '')}"
                question = (message.get("text", {}) or {}).get("body", "").strip()
                message_id = message.get("id", "")
                if message_id and is_message_processed(message_id):
                    continue
                hashed = phone_hash(phone)
                session_id = pseudonymize_session_id(phone)
                log_event(
                    correlation_id=correlation_id,
                    actor_type="student",
                    actor_id=hashed,
                    session_id=session_id,
                    action="message.received",
                    resource="whatsapp_meta",
                    outcome="success",
                    metadata={"message_id": message_id},
                    fail_closed=settings.AUDIT_FAIL_CLOSED,
                )
                try:
                    answer = build_answer_for_message(
                        phone=phone,
                        question=question,
                        correlation_id=correlation_id,
                        session_id=session_id,
                    )
                except AuditLogError:
                    answer = (
                        "Servico temporariamente indisponivel por motivos de seguranca.\n"
                        "Tente novamente em alguns minutos."
                    )

                sent = await _send_meta_text(phone, answer)
                if sent:
                    log_event(
                        correlation_id=correlation_id,
                        actor_type="student",
                        actor_id=hashed,
                        session_id=session_id,
                        action="message.sent",
                        resource="whatsapp_meta",
                        outcome="success",
                        metadata={"answer_length": len(answer)},
                        fail_closed=settings.AUDIT_FAIL_CLOSED,
                    )
                    if message_id:
                        mark_message_processed(message_id)
                else:
                    log_event(
                        correlation_id=correlation_id,
                        actor_type="student",
                        actor_id=hashed,
                        session_id=session_id,
                        action="message.send_failed",
                        resource="whatsapp_meta",
                        outcome="failure",
                        metadata={"message_id": message_id or None},
                        fail_closed=False,
                    )
    return {"ok": True}
