import importlib.util
import os
import unittest
from unittest.mock import patch

os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt-for-unit-tests-only")

HAS_TORCH = importlib.util.find_spec("torch") is not None


@unittest.skipUnless(HAS_TORCH, "torch não instalado")
class LlmDtypeTests(unittest.TestCase):
    def setUp(self):
        import torch

        self.torch = torch
        from app.core.hardware import _llm_dtype

        self.pick = _llm_dtype

    def _gpu(self, major):
        return (
            patch.object(self.torch.cuda, "is_available", return_value=True),
            patch.object(self.torch.cuda, "get_device_capability", return_value=(major, 0)),
        )

    def test_old_gpu_uses_float16(self):
        # GTX 10xx/16xx, RTX 20xx: bf16 quebra com CUBLAS_STATUS_NOT_SUPPORTED.
        a, b = self._gpu(7)
        with a, b:
            self.assertEqual(self.pick("auto", "auto"), self.torch.float16)

    def test_ampere_gpu_uses_bfloat16(self):
        a, b = self._gpu(8)
        with a, b:
            self.assertEqual(self.pick("auto", "auto"), self.torch.bfloat16)

    def test_cpu_uses_float32(self):
        with patch.object(self.torch.cuda, "is_available", return_value=False):
            self.assertEqual(self.pick("auto", "auto"), self.torch.float32)
        a, b = self._gpu(8)
        with a, b:
            self.assertEqual(self.pick("cpu", "auto"), self.torch.float32)

    def test_explicit_override(self):
        self.assertEqual(self.pick("auto", "float32"), self.torch.float32)
        self.assertEqual(self.pick("auto", " BFloat16 "), self.torch.bfloat16)


if __name__ == "__main__":
    unittest.main()
