"""Verificação de consentimento antes do atendimento (Lei 15.211/2025, art. 12, § 2º).

Toda mensagem recebida pelo tutor passa por aqui antes de chegar ao pipeline RAG:

- "SAIR" (ou equivalente) revoga o consentimento e apaga o histórico da conversa;
- sem consentimento ativo, "ACEITO" (ou equivalente) registra o consentimento;
- sem consentimento ativo, qualquer outra mensagem recebe o pedido de consentimento
  e não é processada.

Se o consentimento estiver ativo, a função devolve None e a pergunta segue normalmente.
"""

from __future__ import annotations

from app.audit.consent import (
    consent_prompt,
    grant_consent,
    has_active_consent,
    is_consent_accept_command,
    is_optout_command,
    optout_confirmation,
    revoke_consent,
)
from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.audit.service import log_event

CONSENT_GRANTED_MESSAGE = (
    "Consentimento registrado. Agora você pode enviar sua pergunta de Matemática."
)


def _gate_response(answer: str, *, consent_active: bool) -> dict:
    return {
        "answer": answer,
        "abstained": False,
        "consent_active": consent_active,
        "sources": [],
    }


def consent_gate(phone: str, message: str, *, correlation_id: str) -> dict | None:
    """Devolve a resposta do fluxo de consentimento, ou None se a pergunta pode seguir."""
    session_id = pseudonymize_session_id(phone)

    if is_optout_command(message):
        revoke_consent(phone=phone, correlation_id=correlation_id, session_id=session_id)
        return _gate_response(optout_confirmation(), consent_active=False)

    if has_active_consent(phone):
        return None

    if is_consent_accept_command(message):
        grant_consent(phone=phone, correlation_id=correlation_id, session_id=session_id)
        return _gate_response(CONSENT_GRANTED_MESSAGE, consent_active=True)

    log_event(
        correlation_id=correlation_id,
        actor_type="student",
        actor_id=phone_hash(phone),
        session_id=session_id,
        action="consent.required",
        resource="consent",
        outcome="blocked",
        fail_closed=True,
    )
    return _gate_response(consent_prompt(), consent_active=False)
