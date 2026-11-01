"""Testes da verificação de consentimento antes do atendimento."""

import os
import tempfile
import unittest

os.environ.setdefault("AUDIT_DB_PATH", tempfile.mktemp(suffix=".db"))
os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt-min-16-chars")
os.environ.setdefault("PHONE_ENCRYPTION_KEY", "")
os.environ.setdefault("CONSENT_TERMS_VERSION", "1.0")

from app.audit import init_audit
from app.audit.consent import consent_prompt, has_active_consent, optout_confirmation
from app.audit.repository import fetch_audit_logs
from app.services.consent_gate import CONSENT_GRANTED_MESSAGE, consent_gate


class ConsentGateTests(unittest.TestCase):
    def setUp(self):
        init_audit()

    def test_question_without_consent_is_blocked(self):
        phone = "aluno-gate-1"
        result = consent_gate(phone, "Quanto é 2+2?", correlation_id="g1")
        self.assertIsNotNone(result)
        self.assertEqual(result["answer"], consent_prompt())
        self.assertFalse(result["consent_active"])
        self.assertFalse(has_active_consent(phone))
        actions = [row["action"] for row in fetch_audit_logs() if row["correlation_id"] == "g1"]
        self.assertIn("consent.required", actions)

    def test_accept_grants_consent_and_then_question_passes(self):
        phone = "aluno-gate-2"
        accepted = consent_gate(phone, "ACEITO", correlation_id="g2")
        self.assertEqual(accepted["answer"], CONSENT_GRANTED_MESSAGE)
        self.assertTrue(has_active_consent(phone))
        self.assertIsNone(consent_gate(phone, "Quanto é 2+2?", correlation_id="g3"))

    def test_optout_revokes_consent(self):
        phone = "aluno-gate-3"
        consent_gate(phone, "aceito", correlation_id="g4")
        self.assertTrue(has_active_consent(phone))
        result = consent_gate(phone, "SAIR", correlation_id="g5")
        self.assertEqual(result["answer"], optout_confirmation())
        self.assertFalse(has_active_consent(phone))
        blocked = consent_gate(phone, "Quanto é 2+2?", correlation_id="g6")
        self.assertEqual(blocked["answer"], consent_prompt())

    def test_perguntar_endpoint_calls_consent_gate_first(self):
        path = os.path.join(os.path.dirname(__file__), "..", "app", "api", "main.py")
        with open(path, encoding="utf-8") as fh:
            source = fh.read()
        body = source.split("def perguntar", 1)[1]
        self.assertIn("consent_gate(", body)
        self.assertLess(body.index("consent_gate("), body.index("answer_question_detailed("))


if __name__ == "__main__":
    unittest.main()
