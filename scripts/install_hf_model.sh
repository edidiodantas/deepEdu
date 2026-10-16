#!/usr/bin/env bash
# Pré-baixa o LLM oficial DeepEdu no cache Hugging Face.
# Modelo: Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct (PT-BR, 0,49B, base Qwen2.5)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL="${LLM_MODEL:-amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct}"
RERANK="${RERANK_MODEL:-unicamp-dl/monoptt5-3b}"

if [[ -f .venv/bin/activate ]]; then
  # shellcheck disable=SC1091
  source .venv/bin/activate
fi

echo "==> Pré-baixando modelo Hugging Face:"
echo "    ${MODEL}"
echo "    (precisa de internet; ~1 GB no 1º download)"

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

echo "==> Pré-baixando reranker monoPTT5 (português):"
echo "    ${RERANK}"
echo "    (1º download ~6 GB; carrega na primeira pergunta, de preferência com GPU)"

python - <<PY
from huggingface_hub import snapshot_download
from transformers import AutoTokenizer

model_id = "${RERANK}"
path = snapshot_download(repo_id=model_id)
tok = AutoTokenizer.from_pretrained(model_id)
vocab = tok.get_vocab()
ok = ("▁true" in vocab or "true" in vocab) and ("▁false" in vocab or "false" in vocab)
print("OK — reranker em cache:", path)
print("tokens true/false:", "sim" if ok else "NAO ENCONTRADOS")
if not ok:
    raise SystemExit(1)
print()
print("Configure no .env:")
print("  RERANK_ENABLED=true")
print(f"  RERANK_MODEL={model_id}")
PY
