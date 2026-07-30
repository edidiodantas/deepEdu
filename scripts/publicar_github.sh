#!/usr/bin/env bash
# Publica 01_deepEdu no GitHub como repositório PRIVADO.
# Rode no Deepin (com internet):
#   bash ~/Projects/01_deepEdu/scripts/publicar_github.sh
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

REPO_NAME="${REPO_NAME:-deepEdu}"

echo "==> Projeto: $ROOT"
echo "==> Repo GitHub (privado): $REPO_NAME"
echo

if ! command -v git >/dev/null; then
  echo "ERRO: git nao instalado. sudo apt install -y git" >&2
  exit 1
fi

if ! command -v gh >/dev/null; then
  echo "ERRO: GitHub CLI (gh) nao instalado." >&2
  echo "Instale: sudo apt install -y gh" >&2
  echo "Depois: gh auth login" >&2
  exit 1
fi

if ! gh auth status >/dev/null 2>&1; then
  echo "Voce ainda nao esta logado no GitHub CLI."
  echo "Vou abrir o login. Escolha: GitHub.com → HTTPS → Login with browser"
  gh auth login
fi

gh auth status

# Garante .gitkeep de audit
mkdir -p data/audit
touch data/audit/.gitkeep

# Branch main
current="$(git branch --show-current 2>/dev/null || true)"
if [[ -z "$current" ]]; then
  git checkout -b main 2>/dev/null || git branch -M main
else
  git branch -M main
fi

echo
echo "==> Arquivos que SERAO enviados (confira: NAO deve ter .env nem .venv):"
git status -sb
echo
git status --short | head -80 || true

# Bloqueio basico se .env estiver staged/untracked de forma perigosa
if git status --short | grep -E '(^..|\s)\.env$' >/dev/null 2>&1; then
  echo "ERRO: .env apareceu no status. Remova/ignore antes de continuar." >&2
  exit 1
fi

git add -A
echo
echo "==> Apos git add (deve ignorar .env/.venv):"
git status --short | head -100

if git diff --cached --quiet; then
  echo "Nada novo para commit (ja estava commitado?)."
else
  git commit -m "$(cat <<'EOF'
Initial commit: deepEdu source for multi-PC Cursor.

EOF
)"
fi

if git remote get-url origin >/dev/null 2>&1; then
  echo "==> Remote origin ja existe: $(git remote get-url origin)"
  git push -u origin main
else
  echo "==> Criando repositorio PRIVADO no GitHub e fazendo push..."
  gh repo create "$REPO_NAME" --private --source=. --remote=origin --push
fi

echo
echo "PRONTO."
gh repo view --web 2>/dev/null || true
echo
URL="$(gh repo view --json url -q .url 2>/dev/null || true)"
echo "URL: ${URL:-veja no GitHub}"
echo
echo "No outro PC (Windows + Cursor):"
echo "  gh repo clone SEU_USUARIO/${REPO_NAME}"
echo "  # ou clone pela URL HTTPS e abra a pasta no Cursor"
echo
echo "NAO copie .env do Server para o Git. No outro PC: cp .env.example .env"
