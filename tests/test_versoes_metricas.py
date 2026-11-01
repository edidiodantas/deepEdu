"""Testes do versionamento da base, das métricas consolidadas e do relatório de avaliação."""

import hashlib
import importlib.util
import os
import shutil
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

os.environ.setdefault("AUDIT_DB_PATH", tempfile.mktemp(suffix=".db"))
os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt-min-16-chars")
os.environ.setdefault("PHONE_ENCRYPTION_KEY", "")

from app.audit.metrics import compute_metrics
from app.rag.index_versions import (
    IndexVersionError,
    build_manifest,
    create_version,
    current_version,
    list_versions,
    restore_version,
)

ROOT = Path(__file__).resolve().parents[1]


class IndexVersionTests(unittest.TestCase):
    def setUp(self):
        self.tmp = Path(tempfile.mkdtemp())
        self.chroma = self.tmp / "chroma"
        self.materials = self.tmp / "materials"
        self.versions = self.tmp / "versions"
        self.chroma.mkdir()
        self.materials.mkdir()
        (self.materials / "funcoes.pdf").write_bytes(b"conteudo funcoes")
        (self.materials / "notas.md").write_text("PA e PG", encoding="utf-8")
        (self.materials / "ignorar.docx").write_bytes(b"fora do acervo")
        self.t0 = datetime(2026, 11, 1, 10, 0, tzinfo=timezone.utc)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _snapshot(self, content: str, minutes: int, keep: int = 5) -> dict:
        (self.chroma / "base.bin").write_text(content, encoding="utf-8")
        return create_version(
            self.chroma,
            self.materials,
            chunks=10,
            documents=2,
            versions_dir=self.versions,
            keep=keep,
            now=self.t0 + timedelta(minutes=minutes),
        )

    def test_manifest_lists_materials_with_sha256(self):
        manifest = build_manifest(self.materials)
        names = [f["name"] for f in manifest["files"]]
        self.assertEqual(names, ["funcoes.pdf", "notas.md"])
        expected = hashlib.sha256(b"conteudo funcoes").hexdigest()
        self.assertEqual(manifest["files"][0]["sha256"], expected)
        self.assertEqual(len(manifest["manifest_hash"]), 64)

    def test_manifest_hash_changes_when_material_changes(self):
        before = build_manifest(self.materials)["manifest_hash"]
        (self.materials / "notas.md").write_text("PA, PG e juros", encoding="utf-8")
        self.assertNotEqual(before, build_manifest(self.materials)["manifest_hash"])

    def test_create_version_sets_current(self):
        manifest = self._snapshot("v1", 0)
        self.assertEqual(manifest["version"], "v20261101-100000")
        self.assertEqual(current_version(self.versions), manifest["version"])
        copied = self.versions / manifest["version"] / "chroma" / "base.bin"
        self.assertEqual(copied.read_text(encoding="utf-8"), "v1")

    def test_old_versions_are_pruned_but_current_is_kept(self):
        for i in range(4):
            self._snapshot(f"v{i}", i, keep=2)
        versions = list_versions(self.versions)
        self.assertEqual(len(versions), 2)
        self.assertTrue(versions[0]["current"])

    def test_restore_brings_back_previous_base(self):
        first = self._snapshot("primeira", 0)
        self._snapshot("segunda", 1)
        restore_version(first["version"], self.chroma, versions_dir=self.versions)
        self.assertEqual((self.chroma / "base.bin").read_text(encoding="utf-8"), "primeira")
        self.assertEqual(current_version(self.versions), first["version"])

    def test_restore_unknown_version_fails(self):
        with self.assertRaises(IndexVersionError):
            restore_version("v19990101-000000", self.chroma, versions_dir=self.versions)

    def test_indexer_creates_version_and_logs_it(self):
        source = (ROOT / "app" / "rag" / "indexer.py").read_text(encoding="utf-8")
        self.assertIn("create_version(", source)
        self.assertIn('"index_version": manifest["version"]', source)

    def test_answers_record_index_version(self):
        source = (ROOT / "app" / "services" / "tutor_service.py").read_text(encoding="utf-8")
        self.assertIn("index_version = current_version()", source)
        self.assertGreaterEqual(source.count('"index_version": index_version'), 4)


class MetricsTests(unittest.TestCase):
    def test_compute_metrics_from_audit_events(self):
        logs = [
            {"action": "rag.started", "metadata": {}},
            {"action": "rag.started", "metadata": {}},
            {"action": "rag.started", "metadata": {}},
            {"action": "rag.started", "metadata": {}},
            {"action": "rag.abstained", "metadata": {"index_version": "v1"}},
            {"action": "rag.completed", "metadata": {"max_retrieval_score": 0.8, "index_version": "v1"}},
            {"action": "rag.completed", "metadata": {"max_retrieval_score": 0.6, "index_version": "v2"}},
            {"action": "output.blocked", "metadata": {"reason": "leak"}},
            {"action": "prompt.injection_neutralized", "metadata": {}},
            {"action": "consent.required", "metadata": {}},
            {"action": "sympy.verified", "metadata": {}},
            {"action": "sympy.divergence", "metadata": {}},
        ]
        m = compute_metrics(logs)
        self.assertEqual(m["perguntas"], 4)
        self.assertEqual(m["taxa_abstencao"], 0.25)
        self.assertEqual(m["respostas_bloqueadas"], 1)
        self.assertEqual(m["motivos_bloqueio"], {"leak": 1})
        self.assertEqual(m["injecoes_neutralizadas"], 1)
        self.assertEqual(m["pedidos_sem_consentimento"], 1)
        self.assertEqual(m["taxa_acerto_calculos"], 0.5)
        self.assertEqual(m["pontuacao_media_recuperacao"], 0.7)
        self.assertEqual(m["respostas_por_versao_da_base"], {"v1": 2, "v2": 1})

    def test_empty_period_has_no_division_by_zero(self):
        m = compute_metrics([])
        self.assertEqual(m["perguntas"], 0)
        self.assertEqual(m["taxa_abstencao"], 0.0)
        self.assertIsNone(m["pontuacao_media_recuperacao"])


def _load_eval_module():
    spec = importlib.util.spec_from_file_location("eval_rag", ROOT / "scripts" / "eval_rag.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class _Doc:
    def __init__(self, source):
        self.metadata = {"source_file": source}


class EvalReportTests(unittest.TestCase):
    def setUp(self):
        self.ev = _load_eval_module()

    def test_source_hit_compares_file_names(self):
        docs = [_Doc("/data/materials/apostila_funcoes.pdf")]
        self.assertTrue(self.ev.source_hit("apostila_funcoes.pdf", docs))
        self.assertFalse(self.ev.source_hit("geo_analitica.pdf", docs))
        self.assertIsNone(self.ev.source_hit("", docs))

    def test_summary_and_markdown(self):
        results = [
            {"abstained": False, "max_score": 0.8, "source_hit": True, "policy_ok": True,
             "latency_s": 2.0, "blocked": False, "calc_ok": True},
            {"abstained": True, "max_score": 0.2, "source_hit": False, "policy_ok": True,
             "latency_s": 1.0, "blocked": False, "calc_ok": None},
        ]
        summary = self.ev.summarize(results)
        self.assertEqual(summary["abstention_rate"], 0.5)
        self.assertEqual(summary["source_accuracy"], 0.5)
        self.assertEqual(summary["calc_accuracy"], 1.0)
        self.assertEqual(summary["mean_latency_s"], 1.5)
        report = self.ev.render_markdown(summary, {"date": "2026-11-01", "index_version": "v1",
                                                   "llm_model": "amadeus", "min_score": 0.35})
        self.assertIn("| Taxa de abstenção | 50,0% |", report)
        self.assertIn("Versão da base de conhecimento: v1", report)


if __name__ == "__main__":
    unittest.main()
