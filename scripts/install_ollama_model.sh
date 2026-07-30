#!/usr/bin/env bash
# Instala Ollama e baixa Qwen2.5-Math (P01 / RNF09)
set -euo pipefail

MODEL="${LLM_MODEL:-qwen2.5-math:1.5b-instruct}"

if ! command -v ollama >/dev/null 2>&1; then
  echo "Instalando Ollama..."
  curl -fsSL https://ollama.com/install.sh | sh
fi

echo "Baixando modelo ${MODEL}..."
ollama pull "${MODEL}"

echo "Verificando modelo..."
ollama list | grep -i "qwen2.5-math" || ollama list

echo "Pronto. Configure no .env:"
echo "  LLM_PROVIDER=ollama"
echo "  LLM_MODEL=${MODEL}"
echo "  OLLAMA_BASE_URL=http://127.0.0.1:11434"
