import importlib.util
import os
import tempfile
import unittest
from unittest.mock import patch

os.environ.setdefault("AUDIT_PHONE_SALT", "test-salt-for-unit-tests-only")

HAS_TORCH = importlib.util.find_spec("torch") is not None
HAS_HF = HAS_TORCH and importlib.util.find_spec("langchain_huggingface") is not None


@unittest.skipUnless(HAS_TORCH, "torch não instalado")
class PlanPlacementTests(unittest.TestCase):
    def setUp(self):
        import torch

        self.cuda = torch.cuda
        from app.core.hardware import plan_llm_placement

        self.plan = plan_llm_placement

    def _gpu(self, major=7, free_gb=4.0, name="NVIDIA GeForce GTX 1650"):
        return [
            patch.object(self.cuda, "is_available", return_value=True),
            patch.object(self.cuda, "get_device_capability", return_value=(major, 5)),
            patch.object(self.cuda, "get_device_name", return_value=name),
            patch.object(self.cuda, "mem_get_info", return_value=(int(free_gb * 1024**3), 8 * 1024**3)),
        ]

    def _with(self, patches, fn):
        for p in patches:
            p.start()
        try:
            return fn()
        finally:
            for p in patches:
                p.stop()

    def test_old_gpu_goes_to_gpu_in_float16(self):
        p = self._with(self._gpu(major=7), lambda: self.plan("auto", "auto"))
        self.assertEqual((p.device_map, p.dtype_name), ("auto", "float16"))
        self.assertIn("GTX 1650", p.device_label)

    def test_low_vram_notebook_goes_to_cpu(self):
        p = self._with(self._gpu(free_gb=0.8), lambda: self.plan("auto", "auto"))
        self.assertEqual((p.device_map, p.dtype_name), ("cpu", "float32"))
        self.assertIn("0.8 GB", p.reason)

    def test_no_gpu_goes_to_cpu(self):
        with patch.object(self.cuda, "is_available", return_value=False):
            p = self.plan("auto", "auto")
        self.assertEqual((p.device_map, p.device_label), ("cpu", "Processador (CPU)"))

    def test_forced_cpu(self):
        p = self._with(self._gpu(major=8), lambda: self.plan("cpu", "auto"))
        self.assertEqual(p.device_map, "cpu")
        self.assertIn("LLM_DEVICE_MAP=cpu", p.reason)


@unittest.skipUnless(HAS_HF, "transformers/langchain_huggingface não instalados")
class GpuFallbackTests(unittest.TestCase):
    """Se a GPU falha no teste de carregamento, o LLM deve ir para a CPU."""

    @classmethod
    def setUpClass(cls):
        from tokenizers import Tokenizer, models, pre_tokenizers
        from transformers import PreTrainedTokenizerFast, Qwen2Config, Qwen2ForCausalLM

        cls.tmp = tempfile.TemporaryDirectory()
        words = ["<unk>", "<|im_end|>", "<|endoftext|>"] + [chr(c) for c in range(32, 127)] + list("áéíóúã")
        vocab = {w: i for i, w in enumerate(dict.fromkeys(words))}
        tk = Tokenizer(models.WordLevel(vocab=vocab, unk_token="<unk>"))
        tk.pre_tokenizer = pre_tokenizers.Split("", "isolated")
        tok = PreTrainedTokenizerFast(
            tokenizer_object=tk, unk_token="<unk>", eos_token="<|im_end|>", pad_token="<|endoftext|>"
        )
        tok.chat_template = (
            "{% for m in messages %}{{ m['role'] }}: {{ m['content'] }}\n{% endfor %}"
            "{% if add_generation_prompt %}assistant: {% endif %}"
        )
        tok.save_pretrained(cls.tmp.name)
        cfg = Qwen2Config(
            vocab_size=len(vocab), hidden_size=16, intermediate_size=32, num_hidden_layers=1,
            num_attention_heads=2, num_key_value_heads=1,
            eos_token_id=vocab["<|im_end|>"], pad_token_id=vocab["<|endoftext|>"],
        )
        Qwen2ForCausalLM(cfg).save_pretrained(cls.tmp.name)

    @classmethod
    def tearDownClass(cls):
        cls.tmp.cleanup()

    def test_falls_back_to_cpu_when_gpu_smoke_test_fails(self):
        from app.core import hardware, llm_factory
        from app.core.hardware import LlmPlacement

        calls = []

        def plan(_dm, _dt):
            # "gpu-falsa" carrega na CPU (ver from_pretrained abaixo), mas o
            # llm_factory a trata como GPU e roda o teste de carregamento.
            return LlmPlacement("gpu-falsa", "float32", "GPU NVIDIA Falsa", "")

        def smoke(_pipe):
            calls.append(1)
            raise RuntimeError("CUDA error: CUBLAS_STATUS_NOT_SUPPORTED")

        from transformers import AutoModelForCausalLM

        orig = AutoModelForCausalLM.from_pretrained

        def from_pretrained(model_id, device_map=None, **kw):
            return orig(model_id, device_map="cpu" if device_map == "gpu-falsa" else device_map, **kw)

        key = ("huggingface", self.tmp.name, "auto", 0.0, 4, "", "", "", "auto")
        with patch.object(llm_factory, "plan_llm_placement", plan), \
             patch.object(llm_factory, "_smoke_test", smoke), \
             patch.object(AutoModelForCausalLM, "from_pretrained", side_effect=from_pretrained):
            llm_factory._build_chat_model_cached.cache_clear()
            chat = llm_factory._build_chat_model_cached(key)
        llm_factory._build_chat_model_cached.cache_clear()

        self.assertEqual(calls, [1])
        status = hardware.runtime_status()
        self.assertEqual(status["device_map"], "cpu")
        self.assertIn("CUBLAS_STATUS_NOT_SUPPORTED", status["reason"])
        self.assertIsNotNone(chat.invoke("Olá").content)


if __name__ == "__main__":
    unittest.main()
