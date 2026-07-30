from fastapi import FastAPI, Form, Header, HTTPException, Request

from app.audit import init_audit
from app.api.admin import router as admin_router
from app.billing.payment_service import process_asaas_webhook
from app.billing.service import init_billing
from app.core.config import settings
from app.core.langsmith_setup import configure_langsmith
from app.core.startup_checks import run_startup_checks
from app.integrations.meta_webhook import handle_meta_verification, handle_meta_webhook
from app.integrations.twilio_webhook import handle_incoming_whatsapp

app = FastAPI(title=settings.APP_NAME)
app.include_router(admin_router)


@app.on_event("startup")
def startup_event():
    configure_langsmith()
    run_startup_checks()
    init_audit()
    init_billing()


@app.get("/health")
def health():
    return {"status": "ok", "service": settings.APP_NAME}


@app.post("/webhook/whatsapp")
async def whatsapp_webhook(
    request: Request,
    From: str = Form(...),
    Body: str = Form(...),
    MessageSid: str = Form(default=""),
):
    return await handle_incoming_whatsapp(
        request=request, From=From, Body=Body, MessageSid=MessageSid
    )


@app.get("/webhook/meta")
async def meta_webhook_verify(request: Request):
    return await handle_meta_verification(request)


@app.post("/webhook/meta")
async def meta_webhook(request: Request):
    return await handle_meta_webhook(request)


@app.post("/webhook/asaas")
async def asaas_webhook(request: Request, asaas_access_token: str | None = Header(default=None)):
    if settings.ASAAS_WEBHOOK_TOKEN and asaas_access_token != settings.ASAAS_WEBHOOK_TOKEN:
        raise HTTPException(status_code=403, detail="Webhook token invalido")
    payload = await request.json()
    result = process_asaas_webhook(payload)
    return result
