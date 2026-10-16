"""Gestão dos arquivos do corpus em data/materials (upload/listagem/remoção pelo painel)."""

from __future__ import annotations

import hashlib
import re
import threading
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

ALLOWED_SUFFIXES = {".pdf", ".txt", ".md"}
MAX_MATERIAL_BYTES = 50 * 1024 * 1024

# Evita duas reindexações simultâneas (a segunda apagaria a coleção da primeira).
index_lock = threading.Lock()


class MaterialError(ValueError):
    """Arquivo inválido para o corpus."""


def _materials_dir() -> Path:
    path = Path(settings.MATERIALS_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def safe_filename(filename: str) -> str:
    """Aceita só o nome do arquivo (sem pastas) com extensão permitida."""
    name = Path((filename or "").replace("\\", "/")).name.strip()
    name = re.sub(r"[^\w.\- ]", "_", name)
    if not name or name.startswith("."):
        raise MaterialError("Nome de arquivo inválido")
    if Path(name).suffix.lower() not in ALLOWED_SUFFIXES:
        raise MaterialError("Formato não suportado (use .pdf, .txt ou .md)")
    return name


def _resolve(filename: str) -> Path:
    base = _materials_dir().resolve()
    target = (base / safe_filename(filename)).resolve()
    if target.parent != base:
        raise MaterialError("Caminho fora da pasta de materiais")
    return target


def list_materials() -> list[dict]:
    items = []
    for file in sorted(_materials_dir().rglob("*")):
        if not file.is_file() or file.suffix.lower() not in ALLOWED_SUFFIXES:
            continue
        stat = file.stat()
        items.append(
            {
                "name": str(file.relative_to(_materials_dir())),
                "bytes": stat.st_size,
                "modified_at": datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc).isoformat(),
            }
        )
    return items


def save_material(filename: str, data: bytes) -> dict:
    if not data:
        raise MaterialError("Arquivo vazio")
    if len(data) > MAX_MATERIAL_BYTES:
        raise MaterialError(f"Arquivo maior que {MAX_MATERIAL_BYTES // (1024 * 1024)} MB")
    target = _resolve(filename)
    replaced = target.exists()
    target.write_bytes(data)
    return {
        "name": target.name,
        "bytes": len(data),
        "sha256": hashlib.sha256(data).hexdigest(),
        "replaced": replaced,
    }


def delete_material(filename: str) -> dict:
    target = _resolve(filename)
    if not target.exists():
        raise FileNotFoundError(target.name)
    target.unlink()
    return {"name": target.name}
