"""Local file storage adapter for job Excel artefacts.

Production path: replace with Supabase Storage behind the same interface.
"""
from __future__ import annotations

import hashlib
import os
import uuid
from pathlib import Path


def _root() -> Path:
    root = Path(os.getenv("COTARCO_STORAGE_DIR", "/tmp/cotarco-storage"))
    root.mkdir(parents=True, exist_ok=True)
    return root


def store_bytes(
    *,
    job_id: uuid.UUID,
    kind: str,
    original_name: str,
    content: bytes,
) -> dict:
    """Persist bytes and return metadata for JobFileOrm."""
    digest = hashlib.sha256(content).hexdigest()
    safe_name = Path(original_name).name.replace(" ", "_")
    relative = f"{job_id}/{kind.lower()}_{digest[:12]}_{safe_name}"
    dest = _root() / relative
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_bytes(content)
    return {
        "storage_path": str(dest),
        "sha256": digest,
        "size_bytes": len(content),
        "original_name": safe_name,
        "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    }


def read_bytes(storage_path: str) -> bytes:
    path = Path(storage_path)
    if not path.is_file():
        raise FileNotFoundError(storage_path)
    return path.read_bytes()
