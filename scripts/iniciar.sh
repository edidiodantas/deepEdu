#!/usr/bin/env bash
# Liga a API e o painel do DeepEdu e abre o navegador.
# Fechar esta janela (ou Ctrl+C) desliga os dois.
set -uo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

API_PORT="${API_PORT:-8000}"
PANEL_PORT="${PANEL_PORT:-8501}"
LOG_DIR="$ROOT/data/logs"
mkdir -p "$LOG_DIR"

pause_and_exit() {
  echo
  read -r -p "Aperte Enter para fechar..." _
  exit 1
}

if [[ ! -f .venv/bin/activate ]]; then
  echo "ERRO: ambiente .venv não encontrado em $ROOT"
  echo "Crie com: uv venv --python 3.12 .venv && uv pip install -r requirements.txt -r control_panel/requirements-control.txt"
  pause_and_exit
fi
# shellcheck disable=SC1091
source .venv/bin/activate

if [[ ! -f .env ]]; then
  echo "ERRO: arquivo .env não encontrado. Rode: cp .env.example .env"
  pause_and_exit
fi

API_PID=""
PANEL_PID=""
cleanup() {
  echo
  echo "==> Desligando DeepEdu..."
  [[ -n "$PANEL_PID" ]] && kill "$PANEL_PID" 2>/dev/null
  [[ -n "$API_PID" ]] && kill "$API_PID" 2>/dev/null
  wait 2>/dev/null
  echo "==> Desligado."
}
trap cleanup EXIT
trap 'exit 0' INT TERM HUP

echo "==> DeepEdu — ligando..."

if curl -fs "http://127.0.0.1:${API_PORT}/health" >/dev/null 2>&1; then
  echo "    API já estava ligada na porta ${API_PORT}."
else
  echo "    Ligando API (log: data/logs/api.log)..."
  uvicorn app.api.main:app --host 127.0.0.1 --port "$API_PORT" >"$LOG_DIR/api.log" 2>&1 &
  API_PID=$!
  for _ in $(seq 1 60); do
    curl -fs "http://127.0.0.1:${API_PORT}/health" >/dev/null 2>&1 && break
    if ! kill -0 "$API_PID" 2>/dev/null; then
      echo "ERRO: a API não ligou. Últimas linhas do log:"
      tail -n 20 "$LOG_DIR/api.log"
      API_PID=""
      pause_and_exit
    fi
    sleep 1
  done
  echo "    API OK."
fi

if curl -fs "http://127.0.0.1:${PANEL_PORT}" >/dev/null 2>&1; then
  echo "    Painel já estava ligado na porta ${PANEL_PORT}."
else
  echo "    Ligando painel (log: data/logs/painel.log)..."
  (cd control_panel && streamlit run streamlit_app.py \
    --server.port "$PANEL_PORT" --server.headless true \
    --browser.gatherUsageStats false --client.toolbarMode viewer) >"$LOG_DIR/painel.log" 2>&1 &
  PANEL_PID=$!
  for _ in $(seq 1 60); do
    curl -fs "http://127.0.0.1:${PANEL_PORT}" >/dev/null 2>&1 && break
    if ! kill -0 "$PANEL_PID" 2>/dev/null; then
      echo "ERRO: o painel não ligou. Últimas linhas do log:"
      tail -n 20 "$LOG_DIR/painel.log"
      PANEL_PID=""
      pause_and_exit
    fi
    sleep 1
  done
  echo "    Painel OK."
fi

URL="http://localhost:${PANEL_PORT}"
command -v xdg-open >/dev/null 2>&1 && xdg-open "$URL" >/dev/null 2>&1 &

echo
echo "==> DeepEdu ligado: $URL"
echo "    Deixe esta janela aberta. Para desligar, feche a janela ou aperte Ctrl+C."

if [[ -z "$API_PID" && -z "$PANEL_PID" ]]; then
  pause_and_exit
fi
wait
