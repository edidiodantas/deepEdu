#!/usr/bin/env bash
# Gera o pacote do DeepEdu para pendrive: instala em outro Linux (x86_64) SEM internet.
#
# Rode no PC COM internet, dentro da pasta do projeto:
#   bash scripts/preparar_pendrive.sh                 # cria ~/DeepEdu-pendrive
#   bash scripts/preparar_pendrive.sh /media/$USER/PENDRIVE/DeepEdu
#   bash scripts/preparar_pendrive.sh --sem-materiais # não leva PDFs nem índice
#
# O pacote leva: código, Python 3.12 portátil, todas as bibliotecas (torch só CPU),
# modelos Hugging Face (Amadeus + embeddings), materiais e índice. No destino:
#   bash INSTALAR.sh             (notebook)   |   bash INSTALAR.sh --servidor
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

DEST="$HOME/DeepEdu-pendrive"
INCLUDE_DATA=1
for arg in "$@"; do
  case "$arg" in
    --sem-materiais) INCLUDE_DATA=0 ;;
    -h|--help) sed -n '2,13p' "$0"; exit 0 ;;
    *) DEST="$arg" ;;
  esac
done

TORCH_INDEX="${TORCH_INDEX:-https://download.pytorch.org/whl/cpu}"
PART_SIZE="${PART_SIZE:-1900M}"   # partes < 4 GB cabem em pendrive FAT32

step() { echo; echo "==> $*"; }
die() { echo "ERRO: $*" >&2; exit 1; }

[[ "$(uname -m)" == "x86_64" ]] || die "este script gera pacote para Linux x86_64."
UV="$(command -v uv || true)"
[[ -z "$UV" && -x "$HOME/.local/bin/uv" ]] && UV="$HOME/.local/bin/uv"
[[ -n "$UV" ]] || die "uv não encontrado. Instale com: curl -LsSf https://astral.sh/uv/install.sh | sh"
[[ -x .venv/bin/python ]] || die "ambiente .venv do projeto não encontrado (precisa dele para baixar os modelos)."

env_value() {  # lê KEY do .env do projeto, com valor padrão
  local key="$1" default="$2" val=""
  [[ -f .env ]] && val="$(grep -E "^${key}=" .env | tail -1 | cut -d= -f2- | tr -d '\r' || true)"
  echo "${val:-$default}"
}

LLM_MODEL="$(env_value LLM_MODEL amadeusai/Amadeus-Verbo-FI-Qwen2.5-0.5B-PT-BR-Instruct)"
EMBEDDING_MODEL="$(env_value EMBEDDING_MODEL sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2)"
RERANK_ENABLED="$(env_value RERANK_ENABLED true | tr '[:upper:]' '[:lower:]')"
RERANK_MODEL="$(env_value RERANK_MODEL unicamp-dl/monoptt5-3b)"
MODELS=("$LLM_MODEL" "$EMBEDDING_MODEL")
[[ "$RERANK_ENABLED" == "true" ]] && MODELS+=("$RERANK_MODEL")

WORK="$DEST/.montagem"
PKG="$WORK/deepedu-pacote"
echo "== DeepEdu | Gerar pacote para pendrive =="
echo "Projeto: $ROOT"
echo "Destino: $DEST"
rm -rf "$WORK" "$DEST/pacote"
mkdir -p "$PKG" "$DEST/pacote"
trap 'rm -rf "$WORK"' EXIT

# 1) Python 3.12 portátil (o mesmo em que as bibliotecas são montadas).
step "1/6 Python 3.12 portátil"
if [[ -n "${DEEPEDU_PYTHON:-}" ]]; then
  PY="$DEEPEDU_PYTHON"   # uso em testes: Python do sistema, não vai no pacote
  echo "    Usando $PY (não será incluído no pacote)."
else
  "$UV" python install 3.12 >/dev/null
  # Fora do projeto e sem VIRTUAL_ENV: senão o uv devolve o .venv, que é só um
  # atalho para o Python desta máquina e quebra no destino.
  PY="$(cd / && env -u VIRTUAL_ENV "$UV" python find --managed-python 3.12)"
  PY_HOME="$(cd "$(dirname "$(readlink -f "$PY")")/.." && pwd)"
  [[ ! -f "$PY_HOME/pyvenv.cfg" ]] || die "uv devolveu um venv ($PY_HOME), não um Python completo."
  cp -a "$PY_HOME" "$PKG/python"
  PY="$PKG/python/bin/python3.12"
  echo "    $(basename "$PY_HOME")"
fi

# 2) Lista travada de versões (torch só CPU: menor e roda em qualquer máquina).
step "2/6 Resolvendo versões das bibliotecas"
INDEX_ARGS=(--extra-index-url "$TORCH_INDEX")
if ! "$UV" pip compile requirements.txt control_panel/requirements-control.txt \
    --python "$PY" "${INDEX_ARGS[@]}" --index-strategy unsafe-best-match \
    --no-header --quiet -o "$PKG/requirements.lock"; then
  echo "    Aviso: índice do torch-CPU indisponível; usando torch padrão do PyPI (bem maior)."
  INDEX_ARGS=()
  "$UV" pip compile requirements.txt control_panel/requirements-control.txt \
    --python "$PY" --no-header --quiet -o "$PKG/requirements.lock"
fi
grep -E "^torch==" "$PKG/requirements.lock" | sed 's/^/    /' || true

# 3) Baixa/monta todas as bibliotecas como wheels (instalação offline no destino).
step "3/6 Baixando bibliotecas (pode demorar)"
"$UV" venv --quiet --seed --python "$PY" "$WORK/wheel-venv"
"$WORK/wheel-venv/bin/pip" wheel --quiet --no-deps \
  -r "$PKG/requirements.lock" -w "$PKG/wheels" "${INDEX_ARGS[@]}"
rm -rf "$WORK/wheel-venv"
echo "    $(ls "$PKG/wheels" | wc -l) pacotes, $(du -sh "$PKG/wheels" | cut -f1)"

# 4) Código do projeto (sem segredos nem bancos de dados de alunos).
step "4/6 Copiando o projeto"
EXCLUDES=(
  --exclude=./.venv --exclude=./.python --exclude='*/__pycache__' --exclude='*.pyc'
  --exclude=./.env --exclude=./control_panel/.env --exclude=./CHAVE_ADMIN.txt
  --exclude='./data/audit/*.db' --exclude='./data/billing/*.db'
  --exclude='./data/chat_history/*.db' --exclude=./data/logs --exclude=./data/backups
  --exclude=./docs/.pdf-venv --exclude=./.pytest_cache --exclude=./.mypy_cache
)
if [[ "$INCLUDE_DATA" -eq 0 ]]; then
  EXCLUDES+=(--exclude='./data/materials/*' --exclude='./data/chroma/*')
fi
mkdir -p "$PKG/deepEdu"
tar -C "$ROOT" "${EXCLUDES[@]}" -cf - . | tar -C "$PKG/deepEdu" -xf -
mkdir -p "$PKG/deepEdu/data"/{materials,chroma,audit,billing,chat_history}
echo "    materiais: $(find "$PKG/deepEdu/data/materials" -type f ! -name .gitkeep | wc -l) arquivo(s)"

# 5) Modelos Hugging Face (copiados do cache; baixa o que faltar).
step "5/6 Modelos de IA"
HF_HUB="${HF_HOME:-$HOME/.cache/huggingface}/hub"
mkdir -p "$PKG/hf_hub"
MISSING=()
for model in "${MODELS[@]}"; do
  cache_dir="$HF_HUB/models--${model//\//--}"
  if HF_HUB_DISABLE_PROGRESS_BARS=1 .venv/bin/python - "$model" >/dev/null 2>&1 <<'PY'
import sys
from huggingface_hub import snapshot_download
snapshot_download(repo_id=sys.argv[1])
PY
  then :; fi
  if [[ -d "$cache_dir" ]]; then
    cp -a "$cache_dir" "$PKG/hf_hub/"
    echo "    OK  $model ($(du -sh "$cache_dir" | cut -f1))"
  else
    MISSING+=("$model")
    echo "    FALTA $model (sem internet para o Hugging Face?)"
  fi
done

{
  echo "Pacote DeepEdu gerado em $(date '+%d/%m/%Y %H:%M')"
  echo "Commit: $(git -C "$ROOT" rev-parse --short HEAD 2>/dev/null || echo '?')"
  echo "Modelos incluídos:"; ls "$PKG/hf_hub" | sed 's/^models--/  /; s/--/\//g'
  echo "Reranker ativo: $RERANK_ENABLED"
} >"$PKG/PACOTE.txt"
cp "$UV" "$PKG/uv"

# 6) Empacota em partes (pendrive FAT32 não aceita arquivo > 4 GB nem links).
step "6/6 Empacotando"
tar -C "$WORK" -cf - deepedu-pacote | split -b "$PART_SIZE" -d -a 2 - "$DEST/pacote/deepedu.tar.part"
(cd "$DEST/pacote" && sha256sum deepedu.tar.part* >SHA256SUMS)
cp "$ROOT/offline/INSTALAR.sh" "$DEST/INSTALAR.sh"
cp "$ROOT/offline/LEIA-ME.txt" "$DEST/LEIA-ME.txt"
cp "$PKG/PACOTE.txt" "$DEST/PACOTE.txt"
rm -rf "$WORK"

echo
echo "Pronto! Pacote em: $DEST ($(du -sh "$DEST" | cut -f1))"
echo "Copie a pasta inteira para o pendrive. No outro Linux: siga o LEIA-ME.txt da pasta."
if [[ ${#MISSING[@]} -gt 0 ]]; then
  echo
  echo "ATENÇÃO: modelos que não entraram no pacote: ${MISSING[*]}"
  echo "Sem eles o tutor não responde no destino. Rode com internet: bash scripts/install_hf_model.sh"
  exit 2
fi
