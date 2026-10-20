#!/usr/bin/env bash
# Servidor: faz o DeepEdu ligar junto com a máquina (systemd) e abre o painel na rede.
# A API continua só local (127.0.0.1); na rede fica apenas o painel, porta 8501.
#   bash scripts/instalar_servico.sh            instala/atualiza e liga
#   bash scripts/instalar_servico.sh --remover  desliga e remove
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
UNIT="deepedu-local"
UNIT_FILE="/etc/systemd/system/${UNIT}.service"
PANEL_PORT="${PANEL_PORT:-8501}"

command -v systemctl >/dev/null || { echo "ERRO: systemd não encontrado."; exit 1; }

if [[ "${1:-}" == "--remover" ]]; then
  sudo systemctl disable --now "$UNIT" 2>/dev/null || true
  sudo rm -f "$UNIT_FILE"
  sudo systemctl daemon-reload
  echo "OK — serviço $UNIT removido."
  exit 0
fi

echo "    Criando o serviço $UNIT (vai pedir a senha do usuário)..."
sudo tee "$UNIT_FILE" >/dev/null <<EOF
[Unit]
Description=DeepEdu (API + painel)
After=network-online.target
Wants=network-online.target

[Service]
User=$(id -un)
WorkingDirectory=$ROOT
Environment=PANEL_HOST=0.0.0.0
Environment=PANEL_PORT=$PANEL_PORT
Environment=NO_BROWSER=1
ExecStart=/bin/bash $ROOT/scripts/iniciar.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF
sudo systemctl daemon-reload
sudo systemctl enable --now "$UNIT"

if command -v ufw >/dev/null && sudo ufw status 2>/dev/null | grep -q "Status: active"; then
  sudo ufw allow "${PANEL_PORT}/tcp" >/dev/null && echo "    Firewall: porta $PANEL_PORT liberada."
fi

echo "    Aguardando o DeepEdu ligar..."
for _ in $(seq 1 90); do
  if "$ROOT/.venv/bin/python" -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:$PANEL_PORT', timeout=2)" 2>/dev/null; then
    echo "    OK — serviço ligado. Ver estado: systemctl status $UNIT"
    exit 0
  fi
  sleep 2
done
echo "    Aviso: ainda não respondeu. Veja: journalctl -u $UNIT -n 50"
