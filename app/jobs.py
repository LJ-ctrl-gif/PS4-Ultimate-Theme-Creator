"""Almacen de trabajos en disco.

Cada archivo que sube el usuario abre un job con su propia carpeta dentro de
`workspace/`. Ahi vive el original, los frames de preview y lo exportado, asi
que cambiar la cantidad de frames o el wait no obliga a volver a subir nada.
"""

from __future__ import annotations

import json
import shutil
import time
import uuid
from dataclasses import dataclass, field
from pathlib import Path

from .config import MAX_JOBS_KEPT, WORKSPACE


@dataclass
class Job:
    id: str
    kind: str                      # "animated" | "static" | "icon"
    root: Path
    source: Path
    original_name: str
    meta: dict = field(default_factory=dict)

    @property
    def preview_dir(self) -> Path:
        return self.root / "preview"

    @property
    def out_dir(self) -> Path:
        return self.root / "out"

    @property
    def meta_path(self) -> Path:
        return self.root / "job.json"

    def save(self) -> None:
        self.meta_path.write_text(
            json.dumps(
                {
                    "id": self.id,
                    "kind": self.kind,
                    "source": self.source.name,
                    "original_name": self.original_name,
                    "meta": self.meta,
                },
                indent=2,
            ),
            encoding="utf-8",
        )


def _safe_suffix(filename: str) -> str:
    """Solo conserva la extension del nombre subido; el resto se descarta.

    El nombre original nunca toca el sistema de archivos, asi se evita que
    algo como `..\\..\\x.mp4` escriba fuera del workspace.
    """
    suffix = Path(filename).suffix.lower()
    if len(suffix) > 10 or not suffix.lstrip(".").isalnum():
        return ".bin"
    return suffix or ".bin"


def create(kind: str, filename: str, data: bytes) -> Job:
    WORKSPACE.mkdir(parents=True, exist_ok=True)
    _prune()

    job_id = uuid.uuid4().hex[:12]
    root = WORKSPACE / f"{kind}-{job_id}"
    root.mkdir(parents=True)

    source = root / f"source{_safe_suffix(filename)}"
    source.write_bytes(data)

    job = Job(id=job_id, kind=kind, root=root, source=source, original_name=filename)
    job.preview_dir.mkdir(exist_ok=True)
    job.out_dir.mkdir(exist_ok=True)
    job.save()
    return job


def load(kind: str, job_id: str) -> Job | None:
    """Recupera un job por id.

    El id se valida como hex antes de tocar el disco, para que no pueda
    escaparse de `workspace/` por mas que venga manipulado desde el cliente.
    """
    if not job_id or len(job_id) > 32 or not all(c in "0123456789abcdef" for c in job_id):
        return None

    root = WORKSPACE / f"{kind}-{job_id}"
    meta_path = root / "job.json"
    if not meta_path.is_file():
        return None

    try:
        raw = json.loads(meta_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return None

    source = root / str(raw.get("source", ""))
    if not source.is_file():
        return None

    return Job(
        id=job_id,
        kind=kind,
        root=root,
        source=source,
        original_name=str(raw.get("original_name", "")),
        meta=raw.get("meta") or {},
    )


def _prune() -> None:
    """Deja solo los jobs mas recientes; los viejos se borran enteros."""
    if not WORKSPACE.is_dir():
        return
    dirs = [d for d in WORKSPACE.iterdir() if d.is_dir()]
    if len(dirs) <= MAX_JOBS_KEPT:
        return
    dirs.sort(key=lambda d: d.stat().st_mtime, reverse=True)
    for stale in dirs[MAX_JOBS_KEPT:]:
        shutil.rmtree(stale, ignore_errors=True)


def list_recent(limit: int = 100) -> list[dict]:
    """Return safe metadata for workspace jobs without exposing filesystem paths."""
    if not WORKSPACE.is_dir():
        return []
    allowed = {"animated", "slot", "audio", "convert", "package"}
    found: list[dict] = []
    for root in WORKSPACE.iterdir():
        if not root.is_dir() or root.is_symlink():
            continue
        prefix, sep, job_id = root.name.partition("-")
        if not sep or prefix not in allowed or not job_id:
            continue
        job = load(prefix, job_id)
        if job is None:
            continue
        total = 0
        file_count = 0
        for item in root.rglob("*"):
            if item.is_file() and not item.is_symlink():
                try:
                    total += item.stat().st_size
                    file_count += 1
                except OSError:
                    continue
        try:
            updated = root.stat().st_mtime
        except OSError:
            updated = 0
        found.append({
            "id": job.id,
            "kind": job.kind,
            "name": job.original_name[:200],
            "size_bytes": total,
            "file_count": file_count,
            "updated": updated,
            "has_export": any((job.out_dir / name).is_file()
                              for name in ("background.raf.zip", "theme.zip", "theme.pkg")),
        })
    found.sort(key=lambda item: item["updated"], reverse=True)
    return found[:max(1, min(int(limit), 200))]


def delete(kind: str, job_id: str) -> bool:
    """Delete one validated job directory; never accepts arbitrary paths."""
    if kind not in {"animated", "slot", "audio", "convert", "package"}:
        return False
    job = load(kind, job_id)
    if job is None or job.root.is_symlink():
        return False
    shutil.rmtree(job.root)
    return True


def touch(job: Job) -> None:
    """Marca el job como usado para que _prune no se lo lleve."""
    try:
        job.root.touch()
    except OSError:
        pass
    job.meta["last_used"] = time.time()
