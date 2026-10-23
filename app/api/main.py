import uuid

from fastapi import FastAPI, Header, HTTPException, Request
from pydantic import BaseModel, Field

from app.audit import init_audit
from app.api.admin import router as admin_router
from app.billing.payment_service import process_asaas_webhook
from app.billing.service import init_billing
from app.core.config import settings
from app.core.hardware import runtime_status
from app.core.langsmith_setup import configure_langsmith
from app.core.startup_checks import run_startup_checks
from app.services.tutor_service import answer_question

app = FastAPI(title=settings.APP_NAME)
app.include_router(admin_router)


class LocalQuestion(BaseModel):
    question: str = Field(min_length=1)
    student_id: str = "aluno-local"


@app.on_event("startup")
def startup_event():
    configure_langsmith()
    run_startup_checks()
    init_audit()
    init_billing()


@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": settings.APP_NAME,
        "llm_provider": settings.LLM_PROVIDER,
        "llm_model": settings.LLM_MODEL,
        "llm_runtime": runtime_status(),
    }


@app.post("/perguntar")
def perguntar(body: LocalQuestion):
    """Pergunta local. Grava a mesma trilha de auditoria do tutor."""
    question = body.question.strip()
    if not question:
        raise HTTPException(status_code=400, detail="Pergunta vazia")
    student_id = body.student_id.strip() or "aluno-local"
    correlation_id = str(uuid.uuid4())
    answer = answer_question(
        phone=student_id,
        question=question,
        correlation_id=correlation_id,
    )
    return {"correlation_id": correlation_id, "answer": answer}


@app.post("/webhook/asaas")
async def asaas_webhook(request: Request, asaas_access_token: str | None = Header(default=None)):
    token = settings.ASAAS_WEBHOOK_TOKEN.strip()
    if settings.ENV.lower() == "production":
        if not token or asaas_access_token != token:
            raise HTTPException(status_code=403, detail="Webhook token invalido")
    elif token and asaas_access_token != token:
        raise HTTPException(status_code=403, detail="Webhook token invalido")
    payload = await request.json()
    result = process_asaas_webhook(payload)
    return result
