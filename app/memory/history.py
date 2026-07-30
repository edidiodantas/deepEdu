from pathlib import Path

from langchain_community.chat_message_histories import SQLChatMessageHistory

from app.core.config import settings


def get_history(session_id: str) -> SQLChatMessageHistory:
    Path(settings.CHAT_DB_PATH).parent.mkdir(parents=True, exist_ok=True)
    return SQLChatMessageHistory(
        session_id=session_id,
        connection=f"sqlite:///{settings.CHAT_DB_PATH}",
    )


def clear_session_history(session_id: str) -> None:
    history = get_history(session_id)
    history.clear()

