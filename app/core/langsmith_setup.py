import os

from app.core.config import settings


def configure_langsmith() -> None:
    if not settings.LANGCHAIN_TRACING_V2:
        return
    os.environ.setdefault("LANGCHAIN_TRACING_V2", "true")
    if settings.LANGSMITH_API_KEY:
        os.environ.setdefault("LANGCHAIN_API_KEY", settings.LANGSMITH_API_KEY)
    if settings.LANGCHAIN_PROJECT:
        os.environ.setdefault("LANGCHAIN_PROJECT", settings.LANGCHAIN_PROJECT)
