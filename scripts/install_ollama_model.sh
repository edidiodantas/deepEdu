#!/usr/bin/env bash
# LEGADO — Ollama + Qwen2.5-Math (opcional).
# O padrao do projeto agora e Hugging Face Amadeus-Verbo:
#   bash scripts/install_hf_model.sh
set -euo pipefail

MODEL="${LLM_MODEL:-qwen2.5-math:1.5b-instruct}"

echo "AVISO: o LLM padrao do deepEdu e Amadeus-Verbo (Hugging Face)."
echo "       Este script so e necessario se LLM_PROVIDER=ollama."
echo

if ! command -v ollama >/dev/null 2>&1; then
  echo "Instalando Ollama..."
  curl -fsSL https://ollama.com/install.sh -o /tmp/ollama-install.sh
  sh /tmp/ollama-install.sh
  rm -f /tmp/ollama-install.sh
fi

echo "Baixando modelo ${MODEL}..."
ollama pull "${MODEL}"

echo "Verificando modelo..."
ollama list

echo "Pronto. Configure no .env:"
echo "  LLM_PROVIDER=ollama"
echo "  LLM_MODEL=${MODEL}"
echo "  OLLAMA_BASE_URL=http://127.0.0.1:11434"
