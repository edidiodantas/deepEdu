from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.audit.repository import get_enrollment
from app.audit.repository import append_consent_log, get_latest_consent
from app.audit.service import log_event
from app.core.config import settings
from app.core.text_normalize import normalize_text
from app.memory.history import clear_session_history


def _normalize(text: str) -> str:
    return normalize_text(text)


def consent_prompt() -> str:
    school = settings.CONSENT_SCHOOL_NAME.strip() or "sua escola"
    return (
        f"Ola! Sou o tutor de Matematica da {school}.\n"
        "Para te ajudar, registro nossas conversas de forma segura, conforme a "
        "politica de privacidade da escola e a lei de protecao de menores no ambiente digital.\n"
        "Seus pais ou responsaveis autorizaram este uso.\n"
        "Responda ACEITO para continuar ou SAIR para encerrar.\n"
        "Duvidas sobre privacidade: fale com a secretaria da escola."
    )


def consent_denied_message() -> str:
    return (
        "Nao posso processar sua mensagem sem consentimento registrado.\n"
        "Responda ACEITO para usar o tutor ou SAIR para encerrar."
    )


def optout_confirmation() -> str:
    return (
        "Seu consentimento foi revogado e o historico desta conversa foi removido.\n"
        "Para voltar a usar o tutor, responda ACEITO."
    )


def has_active_consent(phone: str) -> bool:
    latest = get_latest_consent(phone_hash(phone))
    if latest is None or latest.status != "granted":
        return False
    # Nova versão dos termos exige novo ACEITO.
    return (latest.terms_version or "") == settings.CONSENT_TERMS_VERSION


def is_consent_accept_command(text: str) -> bool:
    normalized = _normalize(text)
    return normalized in {"aceito", "sim", "concordo", "ok", "aceitar"}


def is_optout_command(text: str) -> bool:
    normalized = _normalize(text)
    return normalized in {"sair", "parar", "cancelar", "excluir", "stop"}


def grant_consent(
    *,
    phone: str,
    correlation_id: str,
    session_id: str,
) -> None:
    hashed = phone_hash(phone)
    version = settings.CONSENT_TERMS_VERSION
    append_consent_log(hashed, "granted", version)
    enrollment = get_enrollment(hashed)
    log_event(
        correlation_id=correlation_id,
        actor_type="student",
        actor_id=hashed,
        session_id=session_id,
        action="consent.granted",
        resource="consent",
        outcome="success",
        metadata={
            "terms_version": version,
            "parental_consent_ref": (enrollment or {}).get("parental_consent_ref"),
        },
        fail_closed=True,
    )


def revoke_consent(
    *,
    phone: str,
    correlation_id: str,
    session_id: str,
) -> None:
    hashed = phone_hash(phone)
    version = settings.CONSENT_TERMS_VERSION
    append_consent_log(hashed, "revoked", version)
    clear_session_history(pseudonymize_session_id(phone))
    log_event(
        correlation_id=correlation_id,
        actor_type="student",
        actor_id=hashed,
        session_id=session_id,
        action="consent.revoked",
        resource="consent",
        outcome="success",
        metadata={"terms_version": version},
        fail_closed=True,
    )
    log_event(
        correlation_id=correlation_id,
        actor_type="student",
        actor_id=hashed,
        session_id=session_id,
        action="optout.requested",
        resource="session",
        outcome="success",
        fail_closed=True,
    )
    log_event(
        correlation_id=correlation_id,
        actor_type="system",
        actor_id="system",
        session_id=session_id,
        action="session.deleted",
        resource=f"session:{session_id}",
        outcome="success",
        fail_closed=True,
    )
