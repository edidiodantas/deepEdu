#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "Uso: $0 <dominio>"
  echo "Exemplo: $0 tutor.escola.com"
  exit 1
fi

DOMAIN="$1"
APP_HEALTH_URL="http://127.0.0.1:8000/health"
PUBLIC_HEALTH_URL="https://${DOMAIN}/health"
PUBLIC_ASK_URL="https://${DOMAIN}/perguntar"

check_cmd() {
  local cmd="$1"
  local label="$2"
  if command -v "$cmd" >/dev/null 2>&1; then
    echo "[OK] ${label}"
  else
    echo "[ERRO] Comando ausente: ${cmd} (${label})"
    return 1
  fi
}

echo "== deepEdu | Validacao de producao =="
echo "Dominio: ${DOMAIN}"
echo

check_cmd "curl" "curl instalado"
check_cmd "openssl" "openssl instalado"
check_cmd "systemctl" "systemctl disponivel"
echo

echo "== Servicos =="
sudo systemctl is-active --quiet deepedu && echo "[OK] deepedu ativo" || echo "[ERRO] deepedu inativo"
sudo systemctl is-active --quiet nginx && echo "[OK] nginx ativo" || echo "[ERRO] nginx inativo"
echo

echo "== Rede local =="
if sudo ss -ltn | grep -q ":8000 "; then
  echo "[OK] app ouvindo na porta 8000"
else
  echo "[ERRO] porta 8000 nao encontrada"
fi

if sudo ss -ltn | grep -q ":80 "; then
  echo "[OK] nginx ouvindo na porta 80"
else
  echo "[ERRO] porta 80 nao encontrada"
fi

if sudo ss -ltn | grep -q ":443 "; then
  echo "[OK] nginx ouvindo na porta 443"
else
  echo "[ERRO] porta 443 nao encontrada"
fi
echo

echo "== DNS =="
if getent hosts "${DOMAIN}" >/dev/null 2>&1; then
  echo "[OK] DNS resolve ${DOMAIN}"
  getent hosts "${DOMAIN}" | head -n 1
else
  echo "[ERRO] DNS nao resolve ${DOMAIN}"
fi
echo

echo "== TLS =="
if echo | openssl s_client -connect "${DOMAIN}:443" -servername "${DOMAIN}" 2>/dev/null | openssl x509 -noout -subject -issuer -dates >/tmp/deepedu_tls_info.txt 2>/dev/null; then
  echo "[OK] Certificado TLS encontrado"
  cat /tmp/deepedu_tls_info.txt
else
  echo "[ERRO] Falha ao ler certificado TLS em ${DOMAIN}:443"
fi
echo

echo "== Health checks =="
if curl -fsS "${APP_HEALTH_URL}" >/tmp/deepedu_health_local.json; then
  echo "[OK] Health local respondeu: ${APP_HEALTH_URL}"
  cat /tmp/deepedu_health_local.json
else
  echo "[ERRO] Health local falhou: ${APP_HEALTH_URL}"
fi

echo

if curl -fsS "${PUBLIC_HEALTH_URL}" >/tmp/deepedu_health_public.json; then
  echo "[OK] Health publico respondeu: ${PUBLIC_HEALTH_URL}"
  cat /tmp/deepedu_health_public.json
else
  echo "[ERRO] Health publico falhou: ${PUBLIC_HEALTH_URL}"
fi
echo

echo "== Pergunta local =="
echo "Rota do aluno: POST ${PUBLIC_ASK_URL}"
echo "Nao disparada neste script: ela carrega o modelo e grava auditoria."
echo

echo "== Logs recentes =="
echo "-- deepedu (ultimas 20 linhas) --"
sudo journalctl -u deepedu -n 20 --no-pager || true
echo
echo "-- nginx (ultimas 20 linhas) --"
sudo journalctl -u nginx -n 20 --no-pager || true
echo

echo "Validacao concluida."
