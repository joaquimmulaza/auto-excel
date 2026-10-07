"""Storage adapters for job Excel artefacts.

Local filesystem for tests/dev; Supabase Storage for production.
PostgreSQL stores metadata only — never the binary blob.
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from pathlib import Path
from typing import Protocol

from backend.app.core.settings import get_settings

logger = logging.getLogger(__name__)

KIND_DIR = {
    "INPUT": "inputs",
    "OUTPUT": "outputs",
    "LOG": "logs",
    "REPORT": "reports",
}


def build_storage_path(
    *,
    job_id: uuid.UUID,
    kind: str,
    sha256: str,
    original_name: str,
) -> str:
    """Logical path: jobs/{job_id}/{inputs|outputs|logs|reports}/{hash}_{name}."""
    folder = KIND_DIR.get(kind.upper(), kind.lower())
    safe_name = Path(original_name).name.replace(" ", "_")
    return f"jobs/{job_id}/{folder}/{sha256[:12]}_{safe_name}"


class StorageAdapter(Protocol):
    def store(
        self,
        *,
        job_id: uuid.UUID,
        kind: str,
        original_name: str,
        content: bytes,
    ) -> dict: ...

    def read(self, storage_path: str) -> bytes: ...

    def delete(self, storage_path: str) -> None: ...

    def get_download_url(self, storage_path: str, *, expires_in: int = 3600) -> str | None: ...


class LocalStorageAdapter:
    def __init__(self, root: str | None = None) -> None:
        self._root = Path(root or get_settings().storage_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    def store(
        self,
        *,
        job_id: uuid.UUID,
        kind: str,
        original_name: str,
        content: bytes,
    ) -> dict:
        digest = hashlib.sha256(content).hexdigest()
        relative = build_storage_path(
            job_id=job_id, kind=kind, sha256=digest, original_name=original_name
        )
        dest = self._root / relative
        if dest.exists():
            # Idempotent: same content/path — never overwrite with different bytes
            existing = dest.read_bytes()
            if existing != content:
                raise FileExistsError(f"Refusing to overwrite distinct content at {relative}")
        else:
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(content)
        return {
            "storage_path": str(dest),
            "sha256": digest,
            "size_bytes": len(content),
            "original_name": Path(original_name).name.replace(" ", "_"),
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

    def read(self, storage_path: str) -> bytes:
        path = Path(storage_path)
        if not path.is_file():
            raise FileNotFoundError(storage_path)
        return path.read_bytes()

    def delete(self, storage_path: str) -> None:
        path = Path(storage_path)
        if path.is_file():
            path.unlink()

    def get_download_url(self, storage_path: str, *, expires_in: int = 3600) -> str | None:
        return None


class SupabaseStorageAdapter:
    def __init__(
        self,
        *,
        url: str | None = None,
        service_role_key: str | None = None,
        bucket: str | None = None,
    ) -> None:
        settings = get_settings()
        self._url = (url or settings.supabase_url or "").rstrip("/")
        self._key = service_role_key or settings.supabase_service_role_key or ""
        self._bucket = bucket or settings.storage_bucket
        if not self._url or not self._key:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY required for supabase storage"
            )

    def _client(self):
        from supabase import create_client

        return create_client(self._url, self._key)

    def store(
        self,
        *,
        job_id: uuid.UUID,
        kind: str,
        original_name: str,
        content: bytes,
    ) -> dict:
        digest = hashlib.sha256(content).hexdigest()
        relative = build_storage_path(
            job_id=job_id, kind=kind, sha256=digest, original_name=original_name
        )
        client = self._client()
        # upsert=False → never overwrite originals
        client.storage.from_(self._bucket).upload(
            relative,
            content,
            file_options={
                "content-type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "upsert": "false",
            },
        )
        return {
            "storage_path": relative,
            "sha256": digest,
            "size_bytes": len(content),
            "original_name": Path(original_name).name.replace(" ", "_"),
            "mime_type": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        }

    def read(self, storage_path: str) -> bytes:
        client = self._client()
        data = client.storage.from_(self._bucket).download(storage_path)
        return bytes(data)

    def delete(self, storage_path: str) -> None:
        client = self._client()
        client.storage.from_(self._bucket).remove([storage_path])

    def get_download_url(self, storage_path: str, *, expires_in: int = 3600) -> str | None:
        client = self._client()
        result = client.storage.from_(self._bucket).create_signed_url(storage_path, expires_in)
        if isinstance(result, dict):
            return result.get("signedURL") or result.get("signedUrl")
        return getattr(result, "signed_url", None) or getattr(result, "signedURL", None)


_adapter: StorageAdapter | None = None


def get_storage_adapter() -> StorageAdapter:
    global _adapter
    if _adapter is None:
        backend = get_settings().storage_backend
        if backend == "supabase":
            _adapter = SupabaseStorageAdapter()
        else:
            _adapter = LocalStorageAdapter()
    return _adapter


def reset_storage_adapter() -> None:
    global _adapter
    _adapter = None


def store_bytes(
    *,
    job_id: uuid.UUID,
    kind: str,
    original_name: str,
    content: bytes,
) -> dict:
    return get_storage_adapter().store(
        job_id=job_id, kind=kind, original_name=original_name, content=content
    )


def read_bytes(storage_path: str) -> bytes:
    return get_storage_adapter().read(storage_path)


def delete_bytes(storage_path: str) -> None:
    get_storage_adapter().delete(storage_path)


def get_download_url(storage_path: str, *, expires_in: int = 3600) -> str | None:
    return get_storage_adapter().get_download_url(storage_path, expires_in=expires_in)
