#!/usr/bin/env bash
# Bootstrap deepEdu no Deepin (Fase A): venv + deps + .env com Ollama + Qwen2.5-Math (RAG).
# Uso: bash scripts/bootstrap_deepin_rag.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "==> deepEdu bootstrap (Deepin + Ollama + Qwen2.5-Math — RAG)"
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
echo "==> Instalando requirements (pode demorar — inclui embeddings locais do RAG)"
pip install -r requirements.txt

ADMIN_API_KEY="$(openssl rand -hex 32)"
AUDIT_PHONE_SALT="$(openssl rand -hex 32)"
PHONE_ENCRYPTION_KEY="$(
  python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
)"

if [[ -f .env ]]; then
  echo "==> .env já existe — NÃO sobrescrevendo"
  echo "    Confira: LLM_PROVIDER=ollama e LLM_MODEL=qwen2.5-math:1.5b-instruct"
else
  echo "==> Criando .env (padrão do projeto: Ollama + Qwen2.5-Math)"
  cp .env.example .env
  sed -i 's/^ENV=.*/ENV=development/' .env
  sed -i 's/^LLM_PROVIDER=.*/LLM_PROVIDER=ollama/' .env
  sed -i 's/^LLM_MODEL=.*/LLM_MODEL=qwen2.5-math:1.5b-instruct/' .env
  sed -i 's|^OLLAMA_BASE_URL=.*|OLLAMA_BASE_URL=http://127.0.0.1:11434|' .env
  sed -i "s|^ADMIN_API_KEY=.*|ADMIN_API_KEY=${ADMIN_API_KEY}|" .env
  sed -i "s|^AUDIT_PHONE_SALT=.*|AUDIT_PHONE_SALT=${AUDIT_PHONE_SALT}|" .env
  sed -i "s|^PHONE_ENCRYPTION_KEY=.*|PHONE_ENCRYPTION_KEY=${PHONE_ENCRYPTION_KEY}|" .env
  sed -i 's/^LANGCHAIN_TRACING_V2=.*/LANGCHAIN_TRACING_V2=false/' .env
  sed -i 's/^BILLING_ENFORCE_SUBSCRIPTION=.*/BILLING_ENFORCE_SUBSCRIPTION=false/' .env
  echo "==> Segredos ADMIN/SALT/Fernet gravados."
fi

echo
echo "==> Próximos passos (RAG completo):"
echo "    1) bash scripts/install_ollama_model.sh   # baixa Qwen2.5-Math"
echo "    2) Copie PDFs para data/materials/         # corpus do RAG"
echo "    3) source .venv/bin/activate"
echo "    4) python scripts/run_indexing.py          # cria data/chroma/"
echo "    5) uvicorn app.api.main:app --host 127.0.0.1 --port 8000"
echo "    6) curl http://127.0.0.1:8000/health"
echo
echo "Plano: docs/PLANO_ESTE_PC.md"
