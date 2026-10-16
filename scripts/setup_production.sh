#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 2 ]]; then
  echo "Uso: $0 <dominio> <usuario_linux>"
  echo "Exemplo: $0 tutor.exemplo.com edidio"
  exit 1
fi

DOMAIN="$1"
LINUX_USER="$2"
PROJECT_DIR="/home/${LINUX_USER}/Projects/deepEdu"
SERVICE_FILE="${PROJECT_DIR}/systemd/deepedu.service"
NGINX_TEMPLATE="${PROJECT_DIR}/nginx/deepedu.conf.template"
NGINX_TARGET="/etc/nginx/sites-available/deepedu"

if [[ ! -d "${PROJECT_DIR}" ]]; then
  echo "Projeto nao encontrado em ${PROJECT_DIR}"
  exit 1
fi

echo "[1/7] Instalando pacotes base..."
sudo apt update
sudo apt install -y nginx certbot python3-certbot-nginx

echo "[2/7] Configurando systemd do DeepEdu..."
sudo sed "s|SEU_USUARIO|${LINUX_USER}|g" "${SERVICE_FILE}" | sudo tee /etc/systemd/system/deepedu.service >/dev/null
sudo systemctl daemon-reload
sudo systemctl enable deepedu
sudo systemctl restart deepedu

echo "[3/7] Validando API local..."
sleep 1
curl -fsS http://127.0.0.1:8000/health >/dev/null

echo "[4/7] Criando config do Nginx..."
sudo sed "s|__DOMAIN__|${DOMAIN}|g" "${NGINX_TEMPLATE}" | sudo tee "${NGINX_TARGET}" >/dev/null
sudo ln -sf "${NGINX_TARGET}" /etc/nginx/sites-enabled/deepedu
sudo rm -f /etc/nginx/sites-enabled/default

echo "[5/7] Testando e recarregando Nginx..."
sudo nginx -t
sudo systemctl reload nginx

echo "[6/7] Emitindo certificado TLS..."
sudo certbot --nginx -d "${DOMAIN}" --non-interactive --agree-tos --register-unsafely-without-email --redirect

echo "[7/7] Finalizado."
echo "Pergunta local: http://127.0.0.1:8000/perguntar"
echo "Status app: sudo systemctl status deepedu"
echo "Status nginx: sudo systemctl status nginx"
