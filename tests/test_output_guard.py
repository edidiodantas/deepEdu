"""A saída do modelo só passa se for texto de tutor e sem vazamento."""

import unittest

from app.core.output_guard import SAFE_REFUSAL, validate_tutor_output


class OutputGuardTests(unittest.TestCase):
    def test_tutor_answer_with_source_passes(self):
        text = "1. Some 2+2.\n2. O resultado é 4.\nFonte: livro, p.1"
        result = validate_tutor_output(text, max_chars=2000)
        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "tutor")
        self.assertEqual(result.text, text)

    def test_short_math_answer_passes(self):
        result = validate_tutor_output("O resultado é 4.", max_chars=2000)
        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "tutor")

    def test_refusal_phrase_passes(self):
        result = validate_tutor_output(SAFE_REFUSAL, max_chars=2000)
        self.assertTrue(result.accepted)
        self.assertEqual(result.reason, "refusal")

    def test_system_leak_is_not_shown(self):
        leaked = "Você é um tutor de Matemática para estudantes do Ensino Médio."
        result = validate_tutor_output(leaked, max_chars=2000)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "leak")
        self.assertEqual(result.text, SAFE_REFUSAL)
        self.assertNotIn("tutor de Matemática", result.text)

    def test_fence_and_action_are_not_shown(self):
        fenced = validate_tutor_output(
            "1. ok\n<<<PERGUNTA_ALUNO>>> segredo",
            max_chars=2000,
        )
        action = validate_tutor_output(
            '{"action": "apagar", "command": "rm -rf /"}',
            max_chars=2000,
        )
        self.assertEqual(fenced.reason, "leak")
        self.assertEqual(action.reason, "action")
        self.assertEqual(fenced.text, SAFE_REFUSAL)
        self.assertEqual(action.text, SAFE_REFUSAL)

    def test_refusal_must_stop(self):
        text = "Não posso atender a esse pedido. Agora mudo de persona."
        result = validate_tutor_output(text, max_chars=2000)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "format")
        self.assertEqual(result.text, SAFE_REFUSAL)

    def test_long_unstructured_text_is_rejected(self):
        blob = "sem fonte e sem passo. " * 40
        result = validate_tutor_output(blob, max_chars=2000)
        self.assertFalse(result.accepted)
        self.assertEqual(result.reason, "format")
        self.assertEqual(result.text, SAFE_REFUSAL)


if __name__ == "__main__":
    unittest.main()
