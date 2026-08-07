"""Comandos WhatsApp / billing — módulo neutro (evita import circular)."""

from __future__ import annotations

import re

from app.core.config import settings
from app.core.text_normalize import normalize_text

_WORD = re.compile(r"[a-z0-9]+")


def extract_billing_type_from_text(text: str) -> str | None:
    normalized = normalize_text(text)
    words = set(_WORD.findall(normalized))
    if "pix" in words:
        return "PIX"
    if "boleto" in words:
        return "BOLETO"
    if "cartao" in words or "credito" in words:
        return "CREDIT_CARD"
    return None


def is_payment_command(text: str) -> bool:
    """Comando de pagamento por palavra inteira / frase curta (não substring)."""
    normalized = normalize_text(text)
    if not normalized:
        return False
    if normalized in {"assinatura", "plano", "pagar", "pagamento", "assinar", "comprar"}:
        return True
    first = _WORD.findall(normalized)[:1]
    return bool(first) and first[0] in {"pagar", "pagamento", "assinar", "comprar"}


def is_status_command(text: str) -> bool:
    normalized = normalize_text(text)
    if not normalized:
        return False
    if normalized in {"status", "acesso", "assinatura", "plano", "meu plano", "meu acesso", "meu status"}:
        return True
    words = _WORD.findall(normalized)
    return len(words) == 1 and words[0] in {"status", "acesso"}


def help_message() -> str:
    return (
        "Bem-vindo ao deepEdu.\n"
        "Comandos rapidos:\n"
        "- ajuda (mostra este menu)\n"
        "- pagar (gera link com opcoes)\n"
        "- pagar pix\n"
        "- pagar boleto\n"
        "- pagar cartao\n"
        "- status\n"
        "- SAIR (revoga consentimento e apaga historico)\n"
        "Ou envie sua duvida da materia normalmente."
    )


def build_checkout_message(phone: str, requested_method: str | None = None) -> str:
    from app.billing.payment_service import create_checkout_for_student_phone

    checkout_data = create_checkout_for_student_phone(phone=phone, billing_type=requested_method)
    checkout_url = checkout_data.get("invoice_url")
    billing_type = checkout_data.get("billing_type", "UNDEFINED")
    if billing_type == "UNDEFINED":
        method_desc = "PIX, boleto ou cartao"
    elif billing_type == "CREDIT_CARD":
        method_desc = "cartao de credito"
    elif billing_type == "BOLETO":
        method_desc = "boleto"
    else:
        method_desc = "PIX"

    return (
        f"Aqui esta seu link de pagamento ({method_desc}):\n"
        f"{checkout_url}\n"
        "Apos a confirmacao, seu acesso sera liberado automaticamente."
    )


def is_help_command(text: str) -> bool:
    normalized = normalize_text(text)
    if normalized in {"ajuda", "menu", "comandos", "help"}:
        return True
    words = _WORD.findall(normalized)
    return len(words) == 1 and words[0] in {"ajuda", "menu", "comandos", "help"}


def is_professor_number(phone: str) -> bool:
    raw = settings.PROFESSOR_WHATSAPP_NUMBERS.strip()
    if not raw:
        return False
    allowed = {item.strip() for item in raw.split(",") if item.strip()}
    return phone in allowed


def is_professor_command(text: str) -> bool:
    return normalize_text(text).startswith("professor")


def professor_help_message() -> str:
    return (
        "Menu professor:\n"
        "- professor ajuda\n"
        "- professor status\n"
        "- professor aviso <mensagem>\n"
        "Exemplo: professor aviso Prova de matematica amanha as 10h."
    )


def handle_professor_command(phone: str, question: str) -> str:
    from app.billing.admin_service import broadcast_to_students, professor_status_summary

    normalized = normalize_text(question)
    if not is_professor_number(phone):
        return "Este comando e exclusivo para numeros de professores autorizados."

    parts = normalized.split(maxsplit=2)
    if len(parts) == 1 or parts[1] in {"ajuda", "menu"}:
        return professor_help_message()

    command = parts[1]
    if command == "status":
        return professor_status_summary()

    if command == "aviso":
        original_parts = question.split(maxsplit=2)
        if len(original_parts) < 3 or not original_parts[2].strip():
            return "Use: professor aviso <mensagem>"
        message = f"[Aviso do Professor]\n{original_parts[2].strip()}"
        report = broadcast_to_students(message=message, statuses=["active", "trial"])
        return (
            "Aviso enviado.\n"
            f"Alvos: {report['targeted']} | Enviados: {report['sent']} | Falhas: {report['failed']}"
        )

    return professor_help_message()
