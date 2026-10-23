import os
import tempfile
import time
import unittest
import uuid

os.environ.setdefault("AUDIT_DB_PATH", tempfile.mktemp(suffix=".db"))
os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt")
os.environ.setdefault("PHONE_ENCRYPTION_KEY", "")

from langchain_core.documents import Document

from app.audit import init_audit
from app.audit.repository import fetch_audit_logs
from app.audit.service import log_event
from app.rag.sources import source_summary


def _log(corr, action):
    log_event(
        correlation_id=corr, actor_type="system", actor_id="t", session_id="s",
        action=action, resource="test", outcome="success",
    )
    time.sleep(0.002)  # timestamps distintos para checar a ordem


class AuditFilterTests(unittest.TestCase):
    def setUp(self):
        init_audit()

    def test_filter_by_correlation_id_is_chronological(self):
        corr = f"resp-{uuid.uuid4()}"
        _log(corr, "rag.started")
        _log("outra-resposta", "rag.started")
        _log(corr, "retrieval.executed")
        _log(corr, "rag.completed")
        items = fetch_audit_logs(correlation_id=corr)
        self.assertEqual([i["action"] for i in items], ["rag.started", "retrieval.executed", "rag.completed"])

    def test_newest_first_returns_latest_events(self):
        for n in range(5):
            _log(f"old-{n}", "test.old")
        marker = f"new-{uuid.uuid4()}"
        _log(marker, "test.new")
        latest = fetch_audit_logs(limit=1, newest_first=True)
        self.assertEqual(latest[0]["correlation_id"], marker)
        oldest = fetch_audit_logs(limit=1)
        self.assertNotEqual(oldest[0]["correlation_id"], marker)


class SourceSummaryTests(unittest.TestCase):
    def test_summary_uses_basename_human_page_and_short_snippet(self):
        doc = Document(
            page_content="Número decimal  é o número com vírgula.\n" + "x" * 400,
            metadata={"source_file": "data/materials/apostila.pdf", "page": 11, "gate_score": 0.71234, "chunk_id": "c1"},
        )
        [src] = source_summary([doc])
        self.assertEqual(src["file"], "apostila.pdf")
        self.assertEqual(src["page"], 12)
        self.assertEqual(src["score"], 0.712)
        self.assertTrue(src["snippet"].startswith("Número decimal é o número com vírgula."))
        self.assertTrue(src["snippet"].endswith("…"))

    def test_txt_without_page(self):
        [src] = source_summary([Document(page_content="abc", metadata={"source": "notas.txt"})])
        self.assertIsNone(src["page"])
        self.assertEqual(src["snippet"], "abc")


if __name__ == "__main__":
    unittest.main()
