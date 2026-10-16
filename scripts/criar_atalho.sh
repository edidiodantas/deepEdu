#!/usr/bin/env bash
# Cria o atalho "DeepEdu" no menu de aplicativos e na Área de Trabalho (Ubuntu/GNOME).
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
chmod +x "$ROOT/scripts/iniciar.sh"

APPS_DIR="$HOME/.local/share/applications"
mkdir -p "$APPS_DIR"
DESKTOP_FILE="$APPS_DIR/deepedu.desktop"

cat >"$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=DeepEdu
Comment=Liga a API e o painel do DeepEdu
Exec=bash "$ROOT/scripts/iniciar.sh"
Path=$ROOT
Icon=applications-science
Terminal=true
Categories=Education;
EOF
chmod +x "$DESKTOP_FILE"
echo "OK — atalho no menu de aplicativos: procure por \"DeepEdu\"."

DESK_DIR="$(xdg-user-dir DESKTOP 2>/dev/null || echo "$HOME/Desktop")"
if [[ -d "$DESK_DIR" ]]; then
  cp "$DESKTOP_FILE" "$DESK_DIR/DeepEdu.desktop"
  chmod +x "$DESK_DIR/DeepEdu.desktop"
  # Marca como confiável para o GNOME deixar abrir com dois cliques.
  gio set "$DESK_DIR/DeepEdu.desktop" metadata::trusted true 2>/dev/null || true
  echo "OK — atalho na Área de Trabalho: $DESK_DIR/DeepEdu.desktop"
  echo "    Se aparecer com um X, clique com o botão direito → \"Permitir execução\"."
fi
