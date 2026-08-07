"""Testes das correções: comandos WhatsApp, phone_key, consent version."""

import os
import tempfile
import unittest

os.environ.setdefault("AUDIT_DB_PATH", tempfile.mktemp(suffix=".db"))
os.environ.setdefault("BILLING_DB_PATH", tempfile.mktemp(suffix=".db"))
os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt-min-16-chars")
os.environ.setdefault("PHONE_ENCRYPTION_KEY", "")
os.environ.setdefault("ENV", "development")
os.environ.setdefault("CONSENT_TERMS_VERSION", "1.0")

from app.audit import init_audit
from app.audit.consent import grant_consent, has_active_consent
from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.billing.phone_identity import phone_key
from app.integrations.commands import is_payment_command, is_status_command
from app.rag.sympy_tool import verify_numeric_answer


class FixRegressionTests(unittest.TestCase):
    def setUp(self):
        init_audit()

    def test_payment_command_does_not_catch_math_plane(self):
        self.assertFalse(is_payment_command("o que e plano cartesiano?"))
        self.assertTrue(is_payment_command("pagar"))
        self.assertTrue(is_payment_command("pagar pix"))
        self.assertTrue(is_payment_command("plano"))

    def test_status_command_exact(self):
        self.assertTrue(is_status_command("status"))
        self.assertTrue(is_status_command("acesso"))
        self.assertFalse(is_status_command("quero acesso ao material de funcoes"))

    def test_phone_key_does_not_rehash(self):
        hashed = phone_hash("+5511999888777")
        self.assertEqual(phone_key(hashed), hashed.lower())
        self.assertEqual(len(phone_key("+5511999888777")), 32)

    def test_consent_requires_current_terms_version(self):
        phone = "+5511666555444"
        grant_consent(phone=phone, correlation_id="c", session_id=pseudonymize_session_id(phone))
        self.assertTrue(has_active_consent(phone))

    def test_sympy_uses_left_side_of_equation(self):
        result = verify_numeric_answer("2+2=4", "A resposta e 4")
        self.assertTrue(result.get("verified"))
        # Nao deve tratar o "4" da equacao como expressao isolada a verificar contra si.
        bad = verify_numeric_answer("2x+5=17", "o valor e 6")
        self.assertIn(bad.get("reason"), {"TypeError", "no_expression", "SympifyError", "ValueError"})


if __name__ == "__main__":
    unittest.main()
