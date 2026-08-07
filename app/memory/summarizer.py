from __future__ import annotations

from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage

from app.core.config import settings
from app.core.token_budget import count_tokens, truncate_to_tokens


def _message_text(message: BaseMessage) -> str:
    content = getattr(message, "content", "")
    if isinstance(content, str):
        return content
    return str(content)


def _role_label(message: BaseMessage) -> str:
    if isinstance(message, HumanMessage):
        return "Aluno"
    if isinstance(message, SystemMessage):
        return "Sistema"
    return "Tutor"


def compact_chat_history(messages: list[BaseMessage]) -> list[BaseMessage]:
    """Buffer + resumo quando histórico excede gatilho (RF08)."""
    if not messages:
        return []

    total = sum(count_tokens(_message_text(msg)) for msg in messages)
    if total <= settings.HISTORY_SUMMARY_TRIGGER:
        return messages

    keep_tail = 4
    if len(messages) <= keep_tail:
        trimmed: list[BaseMessage] = []
        budget = settings.HISTORY_MAX_TOKENS
        for msg in reversed(messages):
            tokens = count_tokens(_message_text(msg))
            if tokens > budget:
                break
            trimmed.insert(0, msg)
            budget -= tokens
        return trimmed

    older = messages[:-keep_tail]
    summary_parts: list[str] = []
    for msg in older:
        role = _role_label(msg)
        excerpt = truncate_to_tokens(_message_text(msg), 80)
        summary_parts.append(f"- {role}: {excerpt}")

    summary = truncate_to_tokens(
        "Resumo da conversa anterior:\n" + "\n".join(summary_parts),
        settings.HISTORY_MAX_TOKENS // 3,
    )
    compacted: list[BaseMessage] = [SystemMessage(content=summary), *messages[-keep_tail:]]

    budget = settings.HISTORY_MAX_TOKENS
    result: list[BaseMessage] = []
    for msg in reversed(compacted):
        tokens = count_tokens(_message_text(msg))
        if tokens > budget:
            break
        result.insert(0, msg)
        budget -= tokens
    return result
