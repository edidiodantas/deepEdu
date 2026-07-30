import os
import tempfile
import unittest

os.environ.setdefault("AUDIT_DB_PATH", tempfile.mktemp(suffix=".db"))
os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt")
os.environ.setdefault("PHONE_ENCRYPTION_KEY", "")

from app.audit import init_audit
from app.audit.consent import grant_consent, has_active_consent, revoke_consent
from app.audit.enrollment import admin_enroll_student, has_active_enrollment, verify_enrollment
from app.audit.hashing import phone_hash, pseudonymize_session_id
from app.audit.repository import fetch_audit_logs, get_latest_consent
from app.audit.service import log_event
from app.rag.abstinence import should_abstain


class AuditCoreTests(unittest.TestCase):
    def setUp(self):
        init_audit()

    def test_phone_hash_stable(self):
        self.assertEqual(phone_hash("+5511999990000"), phone_hash("+5511999990000"))

    def test_session_pseudonymized(self):
        session = pseudonymize_session_id("+5511999990000")
        self.assertTrue(session.startswith("sess_"))
        self.assertNotIn("5511", session)

    def test_audit_log_written(self):
        before = len(fetch_audit_logs())
        log_event(
            correlation_id="test",
            actor_type="system",
            actor_id="test",
            session_id="sess",
            action="test.event",
            resource="test",
            outcome="success",
        )
        self.assertEqual(len(fetch_audit_logs()), before + 1)

    def test_consent_flow(self):
        phone = "+5511888777666"
        grant_consent(phone=phone, correlation_id="c1", session_id=pseudonymize_session_id(phone))
        self.assertTrue(has_active_consent(phone))
        revoke_consent(phone=phone, correlation_id="c2", session_id=pseudonymize_session_id(phone))
        self.assertFalse(has_active_consent(phone))
        latest = get_latest_consent(phone_hash(phone))
        self.assertEqual(latest.status, "revoked")

    def test_enrollment_flow(self):
        phone = "+5511777666555"
        admin_enroll_student(
            phone=phone,
            school_id="escola-1",
            student_code="MAT2026A",
            parental_consent_ref="RESP-001",
        )
        self.assertFalse(has_active_enrollment(phone))
        ok, _ = verify_enrollment(
            phone=phone,
            student_code="MAT2026A",
            correlation_id="c3",
            session_id=pseudonymize_session_id(phone),
        )
        self.assertTrue(ok)
        self.assertTrue(has_active_enrollment(phone))

    def test_abstinence_policy(self):
        self.assertTrue(should_abstain(max_score=0.1, doc_count=3, min_score=0.35))
        self.assertTrue(should_abstain(max_score=0.9, doc_count=0, min_score=0.35))
        self.assertFalse(should_abstain(max_score=0.5, doc_count=2, min_score=0.35))


if __name__ == "__main__":
    unittest.main()
