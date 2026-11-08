from langchain_core.tracers.context import collect_runs

from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.audit.repository import get_enrollment
from app.audit.service import log_event
from app.memory.history import clear_session_history
from app.core.config import settings
from app.core.output_guard import SAFE_REFUSAL, validate_tutor_output
from app.core.prompt_barrier import has_meaningful_content, neutralize, neutralize_injection
from app.core.token_budget import count_tokens, truncate_to_tokens
from app.rag.abstinence import evaluate_retrieval
from app.rag.chain import build_tutor_chain
from app.rag.index_versions import current_version
from app.rag.sources import source_summary
from app.rag.sympy_tool import verify_numeric_answer


def _content_to_text(content) -> str:
    if content is None:
        return ""
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, str):
                parts.append(item)
            elif isinstance(item, dict) and "text" in item:
                parts.append(str(item["text"]))
            else:
                parts.append(str(item))
        return "\n".join(parts)
    return str(content)


def answer_question(
    phone: str,
    question: str,
    *,
    correlation_id: str,
) -> str:
    return answer_question_detailed(phone, question, correlation_id=correlation_id)["answer"]


def answer_question_detailed(
    phone: str,
    question: str,
    *,
    correlation_id: str,
) -> dict:
    """Responde e devolve também os trechos usados (ou os melhores, se absteve)."""
    hashed = phone_hash(phone)
    session_id = pseudonymize_session_id(phone)
    trimmed_question = truncate_to_tokens(question, settings.USER_MESSAGE_MAX_TOKENS)
    # Versão da base de conhecimento usada nesta resposta (registrada na auditoria).
    index_version = current_version()
    # Barreira de entrada: tira delimitadores forjados e neutraliza tentativas de manipulação.
    shielded_question, delimiter_stripped = neutralize(trimmed_question)
    shielded_question, injected = neutralize_injection(shielded_question)

    log_event(
        correlation_id=correlation_id,
        actor_type="student",
        actor_id=hashed,
        session_id=session_id,
        action="rag.started",
        resource="rag_pipeline",
        outcome="success",
        metadata={
            "question_tokens": count_tokens(shielded_question),
            "input_barrier": "pergunta_aluno",
            "delimiter_stripped": delimiter_stripped,
            "injection_fragments": len(injected),
        },
        fail_closed=True,
    )

    if injected:
        log_event(
            correlation_id=correlation_id,
            actor_type="student",
            actor_id=hashed,
            session_id=session_id,
            action="prompt.injection_neutralized",
            resource="prompt_barrier",
            outcome="success",
            metadata={"fragments": len(injected)},
            fail_closed=True,
        )
        if not has_meaningful_content(shielded_question):
            return {
                "answer": SAFE_REFUSAL,
                "abstained": False,
                "blocked": True,
                "max_score": 0.0,
                "min_score": settings.RETRIEVAL_MIN_SCORE,
                "sources": [],
            }

    gate = evaluate_retrieval(
        shielded_question,
        correlation_id=correlation_id,
        actor_id=hashed,
        session_id=session_id,
    )
    if gate.abstain:
        log_event(
            correlation_id=correlation_id,
            actor_type="student",
            actor_id=hashed,
            session_id=session_id,
            action="rag.abstained",
            resource="rag_pipeline",
            outcome="success",
            metadata={
                "max_score": gate.max_score,
                "min_score": settings.RETRIEVAL_MIN_SCORE,
                "index_version": index_version,
            },
            fail_closed=True,
        )
        return {
            "answer": gate.message,
            "abstained": True,
            "max_score": round(gate.max_score, 3),
            "min_score": settings.RETRIEVAL_MIN_SCORE,
            "index_version": index_version,
            "sources": source_summary(gate.docs),
        }

    chain = build_tutor_chain(
        correlation_id=correlation_id,
        actor_id=hashed,
        session_id=session_id,
        prefetched_docs=gate.docs,
    )

    langsmith_run_id: str | None = None
    try:
        with collect_runs() as runs_cb:
            response = chain.invoke(
                {"question": shielded_question},
                config={
                    "configurable": {"session_id": session_id},
                    "metadata": {
                        "session_id": session_id,
                        "phone_hash": hashed,
                        "channel": "local",
                    },
                    "tags": [settings.LANGCHAIN_PROJECT, "rag", "matematica_em"],
                },
            )
        if runs_cb.traced_runs:
            langsmith_run_id = str(runs_cb.traced_runs[0].id)
        model_text = _content_to_text(getattr(response, "content", response))
        checked = validate_tutor_output(
            model_text,
            max_chars=max(500, settings.LLM_MAX_NEW_TOKENS * 8),
        )
        answer = checked.text

        if not checked.accepted:
            log_event(
                correlation_id=correlation_id,
                actor_type="system",
                actor_id="output_guard",
                session_id=session_id,
                action="output.blocked",
                resource="output_guard",
                outcome="blocked",
                metadata={
                    "reason": checked.reason,
                    "max_retrieval_score": gate.max_score,
                    "index_version": index_version,
                },
                langsmith_run_id=langsmith_run_id,
                fail_closed=True,
            )
            # A resposta bloqueada não pode permanecer na memória da conversa.
            clear_session_history(session_id)

        verification = verify_numeric_answer(shielded_question, model_text if checked.accepted else "")
        if verification.get("verified") is False and verification.get("expected"):
            log_event(
                correlation_id=correlation_id,
                actor_type="system",
                actor_id="sympy",
                session_id=session_id,
                action="sympy.divergence",
                resource="sympy",
                outcome="success",
                metadata=verification,
                langsmith_run_id=langsmith_run_id,
            )

        log_event(
            correlation_id=correlation_id,
            actor_type="student",
            actor_id=hashed,
            session_id=session_id,
            action="llm.invoked",
            resource=settings.LLM_MODEL,
            outcome="success" if checked.accepted else "rejected",
            metadata={
                "answer_length": len(answer),
                "output_accepted": checked.accepted,
                "output_reason": checked.reason,
                "sympy_verified": verification.get("verified"),
                "sympy_reason": verification.get("reason"),
                "max_retrieval_score": gate.max_score,
                "index_version": index_version,
            },
            langsmith_run_id=langsmith_run_id,
            fail_closed=True,
        )

        if (
            checked.accepted
            and verification.get("verified") is False
            and verification.get("expected")
        ):
            answer = (
                f"{answer}\n\n"
                f"(Verificacao: resultado esperado ~ {verification['expected']}. "
                "Revise os calculos.)"
            )
        elif checked.accepted and verification.get("verified") is True:
            log_event(
                correlation_id=correlation_id,
                actor_type="system",
                actor_id="sympy",
                session_id=session_id,
                action="sympy.verified",
                resource="sympy",
                outcome="success",
                metadata=verification,
                langsmith_run_id=langsmith_run_id,
            )

        enrollment = get_enrollment(hashed)
        log_event(
            correlation_id=correlation_id,
            actor_type="student",
            actor_id=hashed,
            session_id=session_id,
            action="rag.completed",
            resource="rag_pipeline",
            outcome="success",
            metadata={
                "answer_length": len(answer),
                "output_accepted": checked.accepted,
                "output_reason": checked.reason,
                "parental_consent_ref": (enrollment or {}).get("parental_consent_ref"),
                "max_retrieval_score": gate.max_score,
                "index_version": index_version,
            },
            langsmith_run_id=langsmith_run_id,
            fail_closed=True,
        )
        return {
            "answer": answer,
            "abstained": False,
            "blocked": not checked.accepted,
            "max_score": round(gate.max_score, 3),
            "min_score": settings.RETRIEVAL_MIN_SCORE,
            "index_version": index_version,
            "sources": source_summary(gate.docs),
        }
    except Exception as exc:
        log_event(
            correlation_id=correlation_id,
            actor_type="student",
            actor_id=hashed,
            session_id=session_id,
            action="rag.failed",
            resource="rag_pipeline",
            outcome="failure",
            metadata={"error": type(exc).__name__},
            langsmith_run_id=langsmith_run_id,
            fail_closed=False,
        )
        raise
