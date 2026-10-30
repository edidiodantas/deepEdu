#!/usr/bin/env bash
# Instala o DeepEdu a partir do pendrive, SEM internet (Linux x86_64, ex.: Ubuntu).
#
#   bash INSTALAR.sh              notebook/PC com tela: cria o ícone DeepEdu
#   bash INSTALAR.sh --servidor   servidor: painel aberto na rede e liga junto com a máquina
#   bash INSTALAR.sh --destino /outra/pasta
#
# Instala em ~/deepEdu. Se já existir, atualiza o código e mantém .env, chaves e dados.
set -euo pipefail

HERE="$(cd "$(dirname "$0")" && pwd)"
MODE="notebook"
TARGET="${DEEPEDU_DIR:-$HOME/deepEdu}"
while [[ $# -gt 0 ]]; do
  case "$1" in
    --servidor) MODE="servidor" ;;
    --destino) TARGET="$2"; shift ;;
    -h|--help) sed -n '2,9p' "$0"; exit 0 ;;
    *) echo "Opção desconhecida: $1"; exit 1 ;;
  esac
  shift
done

step() { echo; echo "==> $*"; }
die() { echo; echo "ERRO: $*" >&2; exit 1; }

echo "=============================================="
echo "  DeepEdu — instalação a partir do pendrive"
echo "=============================================="
echo "Destino: $TARGET   (modo: $MODE)"

[[ "$(uname -m)" == "x86_64" ]] || die "este pacote é para Linux x86_64 (esta máquina: $(uname -m))."
ls "$HERE"/pacote/deepedu.tar.part* >/dev/null 2>&1 || die "pasta 'pacote' não encontrada ao lado deste arquivo."

PKG_KB=$(du -sk "$HERE/pacote" | cut -f1)
mkdir -p "$(dirname "$TARGET")"
FREE_KB=$(df -Pk "$(dirname "$TARGET")" | awk 'NR==2 {print $4}')
# Pico: pacote extraído + bibliotecas instaladas. O programa e o Python são movidos
# (não copiados) e as wheels são apagadas antes dos modelos, então 2x basta.
NEED_KB=$((PKG_KB * 2))
if [[ -d "$TARGET/.venv" ]]; then   # atualização: o .venv antigo é substituído
  FREE_KB=$((FREE_KB + $(du -sk "$TARGET/.venv" | cut -f1)))
fi
if (( FREE_KB < NEED_KB )); then
  die "espaço insuficiente: precisa de ~$((NEED_KB / 1024 / 1024 + 1)) GB livres, há $((FREE_KB / 1024 / 1024)) GB."
fi

step "1/7 Conferindo o pacote (detecta pendrive corrompido)"
(cd "$HERE/pacote" && sha256sum --quiet -c SHA256SUMS) || die "arquivos do pacote corrompidos. Copie o pendrive de novo."
echo "    OK"

step "2/7 Extraindo (alguns minutos)"
WORK="$(mktemp -d "$(dirname "$TARGET")/.deepedu-instalador.XXXXXX")"
trap 'rm -rf "$WORK"' EXIT
cat "$HERE"/pacote/deepedu.tar.part* | tar -xf - -C "$WORK"
PKG="$WORK/deepedu-pacote"
UV="$PKG/uv"
chmod +x "$UV"

step "3/7 Copiando o programa para $TARGET"
UPDATE=0
if [[ -f "$TARGET/.env" ]]; then
  UPDATE=1
  echo "    Instalação existente encontrada: atualizando código, mantendo .env e dados."
  tar -C "$PKG/deepEdu" --exclude=./data --exclude=./.env --exclude=./control_panel/.env -cf - . \
    | tar -C "$TARGET" -xf -
  # Materiais novos do pacote entram; nada existente é apagado.
  cp -an "$PKG/deepEdu/data/materials/." "$TARGET/data/materials/" 2>/dev/null || true
elif [[ ! -e "$TARGET" ]]; then
  mv "$PKG/deepEdu" "$TARGET"   # mesmo disco: não ocupa espaço extra
else
  cp -a "$PKG/deepEdu/." "$TARGET/"
fi
mkdir -p "$TARGET/data"/{materials,chroma,audit,billing,chat_history,logs}
mkdir -p "$HOME/.local/bin"
[[ -x "$HOME/.local/bin/uv" ]] || cp "$UV" "$HOME/.local/bin/uv"

step "4/7 Instalando Python e bibliotecas (sem internet)"
if [[ -d "$PKG/python" ]]; then
  rm -rf "$TARGET/.python"
  mv "$PKG/python" "$TARGET/.python"
  PY="$TARGET/.python/bin/python3.12"
else
  PY="${DEEPEDU_PYTHON:-python3.12}"   # pacote de teste sem Python embutido
fi
rm -rf "$TARGET/.venv"
"$UV" venv --quiet --python "$PY" "$TARGET/.venv"
UV_CACHE_DIR="$WORK/uv-cache" VIRTUAL_ENV="$TARGET/.venv" "$UV" pip install --quiet \
  --offline --no-index --find-links "$PKG/wheels" -r "$PKG/requirements.lock"
rm -rf "$PKG/wheels" "$WORK/uv-cache"   # libera espaço antes dos modelos
VPY="$TARGET/.venv/bin/python"
echo "    OK ($("$VPY" --version))"

step "5/7 Modelos de IA"
HF_HUB="${HF_HOME:-$HOME/.cache/huggingface}/hub"
mkdir -p "$HF_HUB"
cp -a "$PKG/hf_hub/." "$HF_HUB/"
ls "$PKG/hf_hub" | sed 's/^models--/    OK  /; s/--/\//g'

step "6/7 Configuração"
cd "$TARGET"
set_env() {  # set_env KEY VALUE: troca a linha KEY= ou acrescenta no fim
  if grep -qE "^$1=" .env; then
    sed -i "s|^$1=.*|$1=$2|" .env
  else
    printf '%s=%s\n' "$1" "$2" >>.env
  fi
}
if [[ "$UPDATE" -eq 0 ]]; then
  cp .env.example .env
  chmod 600 .env
  set_env APP_NAME DeepEdu
  set_env ADMIN_API_KEY "$("$VPY" -c 'import secrets; print(secrets.token_urlsafe(32))')"
  set_env AUDIT_PHONE_SALT "$("$VPY" -c 'import secrets; print(secrets.token_urlsafe(32))')"
  set_env PHONE_ENCRYPTION_KEY "$("$VPY" -c 'from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())')"
  RERANKER="$(grep -E '^RERANK_MODEL=' .env | cut -d= -f2- || true)"
  if [[ -d "$HF_HUB/models--${RERANKER//\//--}" ]]; then
    set_env RERANK_ENABLED true
  else
    set_env RERANK_ENABLED false   # reranker de 6 GB não veio no pacote
  fi
fi
set_env HF_HUB_OFFLINE 1   # usa só os modelos copiados, sem tentar internet
[[ -f control_panel/.env ]] || cp control_panel/.env.example control_panel/.env
ADMIN_KEY="$(grep -E '^ADMIN_API_KEY=' .env | cut -d= -f2- || true)"
printf 'Chave de administrador do DeepEdu (painel -> barra lateral):\n%s\n' "$ADMIN_KEY" >CHAVE_ADMIN.txt
chmod 600 CHAVE_ADMIN.txt

if [[ -z "$(find data/chroma -mindepth 1 ! -name .gitkeep -print -quit)" ]] \
   && [[ -n "$(find data/materials -type f ! -name .gitkeep -print -quit)" ]]; then
  echo "    Indexando os materiais..."
  HF_HUB_OFFLINE=1 "$VPY" scripts/run_indexing.py || echo "    Aviso: indexação falhou; faça depois pela aba Materiais."
fi

echo "    Testando o programa..."
HF_HUB_OFFLINE=1 "$VPY" -c "import app.api.main" >/dev/null 2>"$WORK/teste.log" \
  || { cat "$WORK/teste.log"; die "o programa não carregou (veja a mensagem acima)."; }
echo "    OK"

step "7/7 Atalho / serviço"
chmod +x scripts/*.sh
if [[ "$MODE" == "servidor" ]]; then
  bash scripts/instalar_servico.sh
elif [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
  bash scripts/criar_atalho.sh
else
  echo "    Sem tela gráfica: para ligar use  bash $TARGET/scripts/iniciar.sh"
fi

echo
echo "=============================================="
echo "  DeepEdu instalado em $TARGET"
echo "=============================================="
if [[ "$MODE" == "servidor" ]]; then
  IP="$(hostname -I 2>/dev/null | awk '{print $1}')"
  echo "  Já está ligado e liga sozinho quando o servidor reiniciar."
  echo "  Acesse de outro computador da rede:  http://${IP:-IP_DO_SERVIDOR}:8501"
elif [[ -n "${DISPLAY:-}${WAYLAND_DISPLAY:-}" ]]; then
  echo "  Para abrir: dois cliques no ícone DeepEdu (Área de Trabalho ou menu)."
else
  echo "  Para abrir: bash $TARGET/scripts/iniciar.sh  e acesse http://localhost:8501"
fi
echo "  Chave de administrador: $ADMIN_KEY"
echo "  (guardada em $TARGET/CHAVE_ADMIN.txt — não compartilhe)"
