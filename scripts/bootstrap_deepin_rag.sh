#!/usr/bin/env bash
# Bootstrap deepEdu: venv + deps + .env com Amadeus-Verbo (Hugging Face PT-BR).
# Uso: bash scripts/bootstrap_deepin_rag.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

MODEL="amadeusai/Amadeus-Verbo-FI-Qwen2.5-1.5B-PT-BR-Instruct"

echo "==> deepEdu bootstrap (Amadeus-Verbo PT-BR via Hugging Face — RAG)"
echo "    raiz: $ROOT"

python3 --version

mkdir -p data/materials data/chroma data/audit data/chat_history data/billing

if [[ ! -d .venv ]]; then
  echo "==> Criando .venv"
  python3 -m venv .venv
else
  echo "==> .venv já existe"
fi

# shellcheck disable=SC1091
source .venv/bin/activate
python -m pip install -U pip
echo "==> Instalando requirements (pode demorar — inclui torch + embeddings)"
pip install -r requirements.txt

ADMIN_API_KEY="$(openssl rand -hex 32)"
AUDIT_PHONE_SALT="$(openssl rand -hex 32)"
PHONE_ENCRYPTION_KEY="$(
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
)"

if [[ -f .env ]]; then
  echo "==> .env já existe — NÃO sobrescrevendo"
  echo "    Confira: LLM_PROVIDER=huggingface e LLM_MODEL=${MODEL}"
else
  echo "==> Criando .env (padrão: Amadeus-Verbo Hugging Face)"
  cp .env.example .env
  sed -i 's/^ENV=.*/ENV=development/' .env
  sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=huggingface/' .env
  sed -i "s|^LLM_MODEL=.*|LLM_MODEL=${MODEL}|" .env
  sed -i "s|^LLM_TOKENIZER_ID=.*|LLM_TOKENIZER_ID=${MODEL}|" .env
  sed -i 's/^LLM_DEVICE_MAP=.*/LLM_DEVICE_MAP=auto/' .env
  sed -i "s|^ADMIN_API_KEY=.*|ADMIN_API_KEY=${ADMIN_API_KEY}|" .env
  sed -i "s|^AUDIT_PHONE_SALT=.*|AUDIT_PHONE_SALT=${AUDIT_PHONE_SALT}|" .env
  sed -i "s|^PHONE_ENCRYPTION_KEY=.*|PHONE_ENCRYPTION_KEY=${PHONE_ENCRYPTION_KEY}|" .env
  sed -i 's/^LANGCHAIN_TRACING_V2=.*/LANGCHAIN_TRACING_V2=false/' .env
  sed -i 's/^BILLING_ENFORCE_SUBSCRIPTION=.*/BILLING_ENFORCE_SUBSCRIPTION=false/' .env
  echo "==> Segredos ADMIN/SALT/Fernet gravados."
fi

echo
echo "==> Próximos passos (RAG completo):"
echo "    1) bash scripts/install_hf_model.sh        # baixa Amadeus-Verbo"
echo "    2) Copie PDFs para data/materials/         # corpus do RAG"
echo "    3) source .venv/bin/activate"
echo "    4) python scripts/run_indexing.py          # cria data/chroma/"
echo "    5) uvicorn app.api.main:app --host 127.0.0.1 --port 8000"
echo "    6) curl http://127.0.0.1:8000/health"
echo
echo "Plano: docs/PLANO_ESTE_PC.md"
