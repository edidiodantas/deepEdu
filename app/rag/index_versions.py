"""Versionamento da base de conhecimento (Lei 15.211/2025, art. 17, § 4º, VIII).

Cada reindexação gera uma versão numerada da base vetorial, guardada em
INDEX_VERSIONS_DIR/<versão>/ com:

- chroma/        cópia da base vetorial daquela versão;
- manifest.json  lista dos materiais indexados, com o hash SHA-256 de cada arquivo.

O arquivo INDEX_VERSIONS_DIR/CURRENT indica a versão em uso. As respostas do tutor
registram essa versão na trilha de auditoria, e é possível restaurar uma versão
anterior. Mantêm-se as INDEX_VERSIONS_KEEP versões mais recentes (a versão em uso
nunca é apagada).
"""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime, timezone
from pathlib import Path

from app.core.config import settings

MANIFEST_NAME = "manifest.json"
CURRENT_NAME = "CURRENT"
_MATERIAL_SUFFIXES = {".pdf", ".txt", ".md"}


class IndexVersionError(ValueError):
    """Versão inexistente ou inválida."""


def _versions_dir(versions_dir: str | Path | None) -> Path:
    path = Path(versions_dir or settings.INDEX_VERSIONS_DIR)
    path.mkdir(parents=True, exist_ok=True)
    return path


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fh:
        for block in iter(lambda: fh.read(1 << 16), b""):
            digest.update(block)
    return digest.hexdigest()


def build_manifest(materials_dir: str | Path) -> dict:
    """Lista os materiais indexáveis com tamanho e hash; inclui um hash do conjunto."""
    root = Path(materials_dir)
    files = []
    for path in sorted(p for p in root.rglob("*") if p.is_file() and p.suffix.lower() in _MATERIAL_SUFFIXES):
        files.append(
            {
                "name": path.relative_to(root).as_posix(),
                "bytes": path.stat().st_size,
                "sha256": file_sha256(path),
            }
        )
    joined = "\n".join(f"{f['name']}:{f['sha256']}" for f in files)
    return {"files": files, "manifest_hash": hashlib.sha256(joined.encode("utf-8")).hexdigest()}


def _new_version_id(base: Path, now: datetime | None = None) -> str:
    stamp = (now or datetime.now(timezone.utc)).strftime("v%Y%m%d-%H%M%S")
    candidate, n = stamp, 1
    while (base / candidate).exists():
        n += 1
        candidate = f"{stamp}-{n}"
    return candidate


def current_version(versions_dir: str | Path | None = None) -> str | None:
    marker = _versions_dir(versions_dir) / CURRENT_NAME
    if not marker.exists():
        return None
    value = marker.read_text(encoding="utf-8").strip()
    return value or None


def _set_current(base: Path, version: str) -> None:
    (base / CURRENT_NAME).write_text(version + "\n", encoding="utf-8")


def _read_manifest(base: Path, version: str) -> dict:
    path = base / version / MANIFEST_NAME
    if not path.exists():
        raise IndexVersionError(f"Versão inexistente: {version}")
    return json.loads(path.read_text(encoding="utf-8"))


def list_versions(versions_dir: str | Path | None = None) -> list[dict]:
    """Versões guardadas, da mais recente para a mais antiga."""
    base = _versions_dir(versions_dir)
    current = current_version(base)
    items = []
    for entry in base.iterdir():
        if entry.is_dir() and (entry / MANIFEST_NAME).exists():
            manifest = _read_manifest(base, entry.name)
            manifest["current"] = entry.name == current
            items.append(manifest)
    return sorted(items, key=lambda m: (m.get("created_at", ""), m["version"]), reverse=True)


def prune_versions(keep: int, versions_dir: str | Path | None = None) -> list[str]:
    """Apaga as versões mais antigas além de `keep`; nunca apaga a versão em uso."""
    base = _versions_dir(versions_dir)
    current = current_version(base)
    removed = []
    for manifest in list_versions(base)[max(1, keep):]:
        if manifest["version"] == current:
            continue
        shutil.rmtree(base / manifest["version"], ignore_errors=True)
        removed.append(manifest["version"])
    return removed


def create_version(
    chroma_dir: str | Path,
    materials_dir: str | Path,
    *,
    chunks: int,
    documents: int,
    versions_dir: str | Path | None = None,
    keep: int | None = None,
    now: datetime | None = None,
) -> dict:
    """Guarda a base vetorial recém-construída como nova versão e a torna a versão em uso."""
    base = _versions_dir(versions_dir)
    version = _new_version_id(base, now)
    target = base / version
    shutil.copytree(chroma_dir, target / "chroma")
    manifest = {
        "version": version,
        "created_at": (now or datetime.now(timezone.utc)).isoformat(timespec="seconds"),
        "chunks": chunks,
        "documents": documents,
        **build_manifest(materials_dir),
    }
    (target / MANIFEST_NAME).write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    _set_current(base, version)
    prune_versions(settings.INDEX_VERSIONS_KEEP if keep is None else keep, base)
    return manifest


def _reset_chroma_cache() -> None:
    """Descarta clientes Chroma em memória para que a próxima consulta leia a base restaurada."""
    try:
        from chromadb.api.client import SharedSystemClient

        SharedSystemClient.clear_system_cache()
    except Exception:
        pass


def restore_version(
    version: str,
    chroma_dir: str | Path,
    versions_dir: str | Path | None = None,
) -> dict:
    """Substitui a base vetorial em uso pela cópia guardada de `version`."""
    base = _versions_dir(versions_dir)
    manifest = _read_manifest(base, version)
    snapshot = base / version / "chroma"
    if not snapshot.is_dir():
        raise IndexVersionError(f"Cópia da base ausente na versão {version}")
    _reset_chroma_cache()
    target = Path(chroma_dir)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(snapshot, target)
    _set_current(base, version)
    _reset_chroma_cache()
    return manifest
