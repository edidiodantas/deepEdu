import os

from dotenv import load_dotenv
from twilio.rest import Client


def main():
    load_dotenv()

    account_sid = os.getenv("TWILIO_ACCOUNT_SID", "").strip()
    auth_token = os.getenv("TWILIO_AUTH_TOKEN", "").strip()
    phone_sid = os.getenv("TWILIO_PHONE_NUMBER_SID", "").strip()
    base_url = os.getenv("PUBLIC_BASE_URL", "").strip().rstrip("/")

    missing = [
        name
        for name, value in [
            ("TWILIO_ACCOUNT_SID", account_sid),
            ("TWILIO_AUTH_TOKEN", auth_token),
            ("TWILIO_PHONE_NUMBER_SID", phone_sid),
            ("PUBLIC_BASE_URL", base_url),
        ]
        if not value
    ]
    if missing:
        raise ValueError(f"Variaveis ausentes no .env: {', '.join(missing)}")

    webhook_url = f"{base_url}/webhook/whatsapp"
    client = Client(account_sid, auth_token)

    updated = client.incoming_phone_numbers(phone_sid).update(
        sms_url=webhook_url,
        sms_method="POST",
    )
    print(f"Webhook atualizado com sucesso: {updated.sms_url}")


if __name__ == "__main__":
    main()
