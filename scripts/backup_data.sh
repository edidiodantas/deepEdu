#!/usr/bin/env bash
# Backup automatizado de dados sensíveis (RNF16 / P05)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
BACKUP_DIR="${ROOT}/data/backups"
STAMP="$(date +%Y%m%d_%H%M%S)"
TARGET="${BACKUP_DIR}/${STAMP}"
RETENTION_DAYS="${BACKUP_RETENTION_DAYS:-30}"

mkdir -p "${TARGET}"

copy_if_exists() {
  local src="$1"
  local name="$2"
  if [[ -f "${src}" ]]; then
    cp "${src}" "${TARGET}/${name}"
    echo "  OK ${name}"
  else
    echo "  -- ${name} (ausente)"
  fi
}

echo "DeepEdu backup → ${TARGET}"
copy_if_exists "${ROOT}/data/audit/audit.db" "audit.db"
copy_if_exists "${ROOT}/data/chat_history/chat_history.db" "chat_history.db"
copy_if_exists "${ROOT}/data/billing/billing.db" "billing.db"

tar -czf "${BACKUP_DIR}/deepedu_${STAMP}.tar.gz" -C "${BACKUP_DIR}" "${STAMP}"
rm -rf "${TARGET}"

find "${BACKUP_DIR}" -name 'deepedu_*.tar.gz' -mtime +"${RETENTION_DAYS}" -delete 2>/dev/null || true

echo "Arquivo: ${BACKUP_DIR}/deepedu_${STAMP}.tar.gz"
echo "Retenção: ${RETENTION_DAYS} dias"
