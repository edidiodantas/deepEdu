from datetime import date, timedelta

import httpx

from app.core.config import settings


class AsaasClient:
    def __init__(self):
        self.base_url = settings.ASAAS_BASE_URL.rstrip("/")
        self.api_key = settings.ASAAS_API_KEY
        self.timeout = 20.0

    def _headers(self):
        if not self.api_key:
            raise ValueError("ASAAS_API_KEY nao configurada no .env")
        return {"access_token": self.api_key, "Content-Type": "application/json"}

    def create_customer(self, name: str, cpf_cnpj: str | None, phone: str | None, email: str | None):
        payload = {"name": name}
        if phone:
            payload["mobilePhone"] = phone
        if cpf_cnpj:
            payload["cpfCnpj"] = cpf_cnpj
        if email:
            payload["email"] = email
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/customers", json=payload, headers=self._headers())
            resp.raise_for_status()
            return resp.json()

    def create_charge(self, customer_id: str, value: float, billing_type: str, external_reference: str):
        due_date = (date.today() + timedelta(days=1)).isoformat()
        payload = {
            "customer": customer_id,
            "billingType": billing_type,
            "value": value,
            "dueDate": due_date,
            "description": "Assinatura DeepEdu",
            "externalReference": external_reference,
        }
        with httpx.Client(timeout=self.timeout) as client:
            resp = client.post(f"{self.base_url}/payments", json=payload, headers=self._headers())
            resp.raise_for_status()
            return resp.json()
