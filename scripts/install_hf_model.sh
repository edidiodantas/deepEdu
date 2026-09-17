#!/usr/bin/env bash
# Pré-baixa o LLM oficial deepEdu no cache Hugging Face.
# Modelo: Amadeus-Verbo-FI-Qwen2.5-1.5B-PT-BR-Instruct (PT-BR, base Qwen2.5)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL="${LLM_MODEL:-amadeusai/Amadeus-Verbo-FI-Qwen2.5-1.5B-PT-BR-Instruct}"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> Pré-baixando modelo Hugging Face:"
echo "    ${MODEL}"
echo "    (precisa de internet; ~2–4 GB no 1º download)"

python - <<PY
from huggingface_hub import snapshot_download

model_id = "${MODEL}"
path = snapshot_download(repo_id=model_id)
print("OK — modelo em cache:", path)
PY

python - <<PY
from transformers import AutoTokenizer, AutoModelForCausalLM

model_id = "${MODEL}"
tok = AutoTokenizer.from_pretrained(model_id, trust_remote_code=True)
print("tokenizer OK:", type(tok).__name__)
# Carrega só a config/pesos no cache; pode usar RAM na 1ª vez.
_ = AutoModelForCausalLM.from_pretrained(
    model_id,
    device_map="cpu",
    torch_dtype="auto",
    trust_remote_code=True,
)
print("modelo OK:", model_id)
print()
print("Configure no .env:")
print("  LLM_PROVIDER=huggingface")
print(f"  LLM_MODEL={model_id}")
print(f"  LLM_TOKENIZER_ID={model_id}")
print("  LLM_DEVICE_MAP=auto")
PY
