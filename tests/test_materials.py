import os
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt-for-unit-tests-only")

from app.core.config import settings
from app.rag.materials import (
    MaterialError,
    delete_material,
    list_materials,
    safe_filename,
    save_material,
)


class MaterialsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.patch = patch.object(settings, "MATERIALS_DIR", self.tmp.name)
        self.patch.start()

    def tearDown(self):
        self.patch.stop()
        self.tmp.cleanup()

    def test_save_list_delete_roundtrip(self):
        info = save_material("funcoes.txt", b"f(x) = 2x + 3")
        self.assertEqual(info["name"], "funcoes.txt")
        self.assertFalse(info["replaced"])
        self.assertEqual(len(info["sha256"]), 64)
        self.assertEqual([i["name"] for i in list_materials()], ["funcoes.txt"])

        self.assertTrue(save_material("funcoes.txt", b"novo")["replaced"])

        delete_material("funcoes.txt")
        self.assertEqual(list_materials(), [])

    def test_path_traversal_stays_inside_materials_dir(self):
        info = save_material("../../etc/evil.txt", b"x")
        self.assertEqual(info["name"], "evil.txt")
        self.assertTrue(os.path.exists(os.path.join(self.tmp.name, "evil.txt")))

    def test_rejects_bad_files(self):
        with self.assertRaises(MaterialError):
            safe_filename("script.sh")
        with self.assertRaises(MaterialError):
            safe_filename(".env")
        with self.assertRaises(MaterialError):
            save_material("vazio.pdf", b"")

    def test_delete_missing_raises(self):
        with self.assertRaises(FileNotFoundError):
            delete_material("nao_existe.pdf")


if __name__ == "__main__":
    unittest.main()
