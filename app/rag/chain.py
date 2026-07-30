from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.runnables import RunnableLambda, RunnablePassthrough
from langchain_core.runnables.history import RunnableWithMessageHistory

from app.core.config import settings
from app.core.langsmith_setup import configure_langsmith
from app.core.llm_factory import build_chat_model
from app.core.prompt_loader import load_system_prompt
from app.core.token_budget import format_rag_context, truncate_to_tokens
from app.memory.history import get_history
from app.memory.summarizer import compact_chat_history
from app.rag.audited_retriever import AuditedRetriever
from app.rag.retriever import build_hybrid_retriever


def _retrieve_with_budget(inputs: dict) -> str:
    docs = inputs.get("prefetched_docs")
    if docs is None:
        retriever = inputs["retriever"]
        question = inputs["question"]
        docs = retriever.invoke(question)
    return format_rag_context(docs, settings.RAG_CONTEXT_MAX_TOKENS)


def build_tutor_chain(
    *,
    correlation_id: str | None = None,
    actor_id: str = "system",
    session_id: str = "system",
    prefetched_docs: list | None = None,
):
    configure_langsmith()
    retriever = None
    if prefetched_docs is None:
        base = build_hybrid_retriever()
        retriever = AuditedRetriever(
            base_retriever=base,
            correlation_id=correlation_id,
            actor_id=actor_id,
            session_id=session_id,
        )

    llm = build_chat_model()
    system_template = load_system_prompt()
    if "{context}" not in system_template:
        system_template = f"{system_template}\n\n<context>\n{{context}}\n</context>"

    system_template = truncate_to_tokens(system_template, settings.PROMPT_MAX_TOKENS)
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", system_template),
            MessagesPlaceholder(variable_name="history"),
            ("human", "{question}"),
        ]
    )

    def _trim_history(history):
        return compact_chat_history(history)

    base_chain = (
        RunnablePassthrough.assign(
            context=RunnableLambda(
                lambda x: _retrieve_with_budget(
                    {
                        "retriever": retriever,
                        "question": x["question"],
                        "prefetched_docs": prefetched_docs,
                    }
                )
            ),
            history=RunnableLambda(lambda x: _trim_history(x.get("history", []))),
        )
        | prompt
        | llm
    )

    return RunnableWithMessageHistory(
        base_chain,
        get_session_history=lambda session_id: get_history(session_id),
        input_messages_key="question",
        history_messages_key="history",
    )
