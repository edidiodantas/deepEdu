from twilio.rest import Client

from app.core.config import settings


def send_whatsapp_message(to_phone: str, body: str):
    if not settings.TWILIO_ACCOUNT_SID or not settings.TWILIO_AUTH_TOKEN:
        raise ValueError("Credenciais Twilio nao configuradas")
    if not settings.TWILIO_WHATSAPP_NUMBER:
        raise ValueError("TWILIO_WHATSAPP_NUMBER nao configurado")

    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    to_value = to_phone if to_phone.startswith("whatsapp:") else f"whatsapp:{to_phone}"
    from_value = (
        settings.TWILIO_WHATSAPP_NUMBER
        if settings.TWILIO_WHATSAPP_NUMBER.startswith("whatsapp:")
        else f"whatsapp:{settings.TWILIO_WHATSAPP_NUMBER}"
    )
    return client.messages.create(body=body, from_=from_value, to=to_value)
