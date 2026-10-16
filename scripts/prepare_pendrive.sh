#!/usr/bin/env bash
# Prepara o projeto DeepEdu para copiar ao pendrive (PC offline).
# Uso:
#   ./scripts/prepare_pendrive.sh
#   ./scripts/prepare_pendrive.sh /media/Edidio/MEU_PENDRIVE
#   ./scripts/prepare_pendrive.sh --with-wheels   # baixa pacotes pip (requer internet)
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
STAMP="$(date +%Y%m%d)"
DEFAULT_DEST="${HOME}/Desktop/deepEdu-PENDRIVE"
DEST="${DEFAULT_DEST}"
WITH_WHEELS=0

for arg in "$@"; do
  case "$arg" in
    --with-wheels) WITH_WHEELS=1 ;;
    *) DEST="$arg" ;;
  esac
done

BUNDLE="${DEST}/deepEdu"
WHEELS_DIR="${BUNDLE}/offline/wheels"

echo "== DeepEdu | Preparar pendrive =="
echo "Origem: ${ROOT}"
echo "Destino: ${BUNDLE}"
echo

mkdir -p "${BUNDLE}"

RSYNC_EXCLUDES=(
  --exclude '.venv/'
  --exclude 'venv/'
  --exclude '**/__pycache__/'
  --exclude '**/*.pyc'
  --exclude '.pytest_cache/'
  --exclude '.mypy_cache/'
  --exclude 'data/chroma/*'
  --exclude 'data/chat_history/*.db'
  --exclude 'data/billing/*.db'
  --exclude 'data/audit/*.db'
  --exclude 'data/backups/'
  --exclude '.env'
  --exclude 'control_panel/.env'
  --exclude 'docs/.pdf-venv/'
  --exclude 'deepedu_phi_compare/.git/'
  --exclude 'reports/'
  --exclude 'PENDRIVE/'
)

rsync -a --delete "${RSYNC_EXCLUDES[@]}" "${ROOT}/" "${BUNDLE}/"

mkdir -p "${BUNDLE}/data/chroma" "${BUNDLE}/data/materials" "${BUNDLE}/data/chat_history" \
         "${BUNDLE}/data/billing" "${BUNDLE}/data/audit" "${BUNDLE}/reports"

# Garante PDF na raiz do pacote (fácil de achar)
if [[ -f "${BUNDLE}/docs/output/DOCUMENTO_FINAL.pdf" ]]; then
  cp -f "${BUNDLE}/docs/output/DOCUMENTO_FINAL.pdf" "${DEST}/DOCUMENTO_FINAL_deepEdu.pdf"
fi

mkdir -p "${BUNDLE}/offline"
cp -f "${ROOT}/offline/LEIA-ME-PENDRIVE.md" "${BUNDLE}/offline/" 2>/dev/null || true
cp -f "${ROOT}/offline/INSTALAR_OFFLINE.md" "${BUNDLE}/offline/" 2>/dev/null || true
cp -f "${ROOT}/offline/requirements-offline.txt" "${BUNDLE}/offline/" 2>/dev/null || true

if [[ "${WITH_WHEELS}" -eq 1 ]]; then
  echo "Baixando wheels Python (pode demorar e ocupar ~2-4 GB)..."
  mkdir -p "${WHEELS_DIR}"
  pip3 download -r "${BUNDLE}/offline/requirements-offline.txt" -d "${WHEELS_DIR}" || {
    echo "Aviso: pip download falhou parcialmente. Copie mesmo assim e use internet no destino se necessário."
  }
fi

# Arquivo compactado extra (backup)
ARCHIVE="${DEST}/deepEdu-offline-${STAMP}.tar.gz"
tar -czf "${ARCHIVE}" -C "${DEST}" "deepEdu" "DOCUMENTO_FINAL_deepEdu.pdf" 2>/dev/null || \
  tar -czf "${ARCHIVE}" -C "${DEST}" "deepEdu"

SIZE="$(du -sh "${DEST}" | cut -f1)"
echo
echo "Pronto!"
echo "  Pasta:  ${BUNDLE}"
echo "  PDF:    ${DEST}/DOCUMENTO_FINAL_deepEdu.pdf"
echo "  Arquivo: ${ARCHIVE}"
echo "  Tamanho total: ${SIZE}"
echo
echo "Copie a pasta ${DEST} inteira para o pendrive."
echo "No PC offline, leia: deepEdu/offline/LEIA-ME-PENDRIVE.md"
