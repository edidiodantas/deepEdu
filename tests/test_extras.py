"""Testes de políticas de startup e reranker."""

import os
import tempfile
import unittest

os.environ.setdefault("AUDIT_DB_PATH", tempfile.mktemp(suffix=".db"))
os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt-min-16-chars")
os.environ.setdefault("ENV", "development")

from app.core.startup_checks import run_startup_checks
from app.rag.abstinence import should_abstain


class ExtraTests(unittest.TestCase):
    def test_startup_checks_dev(self):
        notes = run_startup_checks()
        self.assertIsInstance(notes, list)

    def test_abstinence_edge(self):
        self.assertFalse(should_abstain(max_score=0.35, doc_count=1, min_score=0.35))
        self.assertTrue(should_abstain(max_score=0.34, doc_count=1, min_score=0.35))


if __name__ == "__main__":
    unittest.main()
