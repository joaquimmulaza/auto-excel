"""Storage adapter unit tests (Prompt D — persistent storage).

Cobre LocalStorageAdapter, mock SupabaseStorageAdapter e regressão
de download após “nova sessão” (reset do adapter singleton).
"""
from __future__ import annotations

import uuid
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest

from backend.app.core.settings import clear_settings_cache
from backend.app.services.storage import (
    LocalStorageAdapter,
    SupabaseStorageAdapter,
    build_storage_path,
    get_storage_adapter,
    read_bytes,
    reset_storage_adapter,
    store_bytes,
)


@pytest.fixture(autouse=True)
def _reset_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("COTARCO_STORAGE_DIR", str(tmp_path))
    monkeypatch.delenv("APP_ENV", raising=False)
    monkeypatch.setenv("ENVIRONMENT", "local")
    clear_settings_cache()
    reset_storage_adapter()
    yield
    reset_storage_adapter()
    clear_settings_cache()


def test_build_storage_path_layout():
    job_id = uuid.uuid4()
    path = build_storage_path(
        job_id=job_id,
        kind="INPUT",
        sha256="abcdef1234567890",
        original_name="Tabela Precos.xlsx",
    )
    assert path.startswith(f"jobs/{job_id}/inputs/")
    assert "abcdef123456" in path
    assert path.endswith("Tabela_Precos.xlsx")


def test_local_store_read_and_sha256(tmp_path):
    adapter = LocalStorageAdapter(root=str(tmp_path))
    job_id = uuid.uuid4()
    content = b"excel-bytes-demo"
    meta = adapter.store(
        job_id=job_id, kind="INPUT", original_name="a.xlsx", content=content
    )
    assert meta["size_bytes"] == len(content)
    assert len(meta["sha256"]) == 64
    assert meta["storage_path"].startswith(f"jobs/{job_id}/inputs/")
    assert (tmp_path / meta["storage_path"]).is_file()
    assert adapter.read(meta["storage_path"]) == content


def test_local_store_idempotent_same_bytes(tmp_path):
    adapter = LocalStorageAdapter(root=str(tmp_path))
    job_id = uuid.uuid4()
    content = b"same"
    meta1 = adapter.store(
        job_id=job_id, kind="OUTPUT", original_name="o.xlsx", content=content
    )
    meta2 = adapter.store(
        job_id=job_id, kind="OUTPUT", original_name="o.xlsx", content=content
    )
    assert meta1["storage_path"] == meta2["storage_path"]


def test_local_store_refuses_overwrite_different_bytes(tmp_path):
    adapter = LocalStorageAdapter(root=str(tmp_path))
    job_id = uuid.uuid4()
    meta = adapter.store(
        job_id=job_id, kind="INPUT", original_name="x.xlsx", content=b"aaa"
    )
    Path(tmp_path / meta["storage_path"]).write_bytes(b"tampered-different")
    with pytest.raises(FileExistsError):
        adapter.store(
            job_id=job_id, kind="INPUT", original_name="x.xlsx", content=b"aaa"
        )


def test_store_bytes_read_bytes_facade_local(tmp_path):
    content = b"via-facade"
    job_id = uuid.uuid4()
    meta = store_bytes(
        job_id=job_id, kind="INPUT", original_name="in.xlsx", content=content
    )
    assert read_bytes(meta["storage_path"]) == content


def test_download_survives_new_session_local(tmp_path):
    """Regressão FILE_MISSING_ON_DISK: novo processo/sessão ainda lê o ficheiro."""
    job_id = uuid.uuid4()
    content = b"persist-across-session"
    meta = store_bytes(
        job_id=job_id, kind="OUTPUT", original_name="out.xlsx", content=content
    )
    logical = meta["storage_path"]

    # Simula novo worker / cold start
    reset_storage_adapter()
    clear_settings_cache()
    assert read_bytes(logical) == content


def test_supabase_adapter_store_and_read_mocked():
    job_id = uuid.uuid4()
    content = b"supabase-bytes"
    bucket = MagicMock()
    client = MagicMock()
    client.storage.from_.return_value = bucket

    adapter = SupabaseStorageAdapter(
        url="https://example.supabase.co",
        service_role_key="service-role-secret",
        bucket="job-files",
    )
    with patch.object(adapter, "_client", return_value=client):
        meta = adapter.store(
            job_id=job_id, kind="INPUT", original_name="a.xlsx", content=content
        )
        assert meta["storage_path"].startswith(f"jobs/{job_id}/inputs/")
        bucket.upload.assert_called_once()
        args, kwargs = bucket.upload.call_args
        assert args[0] == meta["storage_path"]
        assert args[1] == content
        assert kwargs["file_options"]["upsert"] == "false"

        bucket.download.return_value = content
        assert adapter.read(meta["storage_path"]) == content


def test_supabase_signed_url_mocked():
    bucket = MagicMock()
    bucket.create_signed_url.return_value = {"signedURL": "https://signed.example/x"}
    client = MagicMock()
    client.storage.from_.return_value = bucket
    adapter = SupabaseStorageAdapter(
        url="https://example.supabase.co",
        service_role_key="service-role-secret",
        bucket="job-files",
    )
    with patch.object(adapter, "_client", return_value=client):
        url = adapter.get_download_url("jobs/x/inputs/a.xlsx", expires_in=60)
    assert url == "https://signed.example/x"


def test_get_storage_adapter_uses_supabase_when_backend_flag(monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "supabase")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "srk")
    clear_settings_cache()
    reset_storage_adapter()
    adapter = get_storage_adapter()
    assert isinstance(adapter, SupabaseStorageAdapter)


def test_production_app_env_defaults_to_supabase(monkeypatch, tmp_path):
    monkeypatch.delenv("STORAGE_BACKEND", raising=False)
    monkeypatch.setenv("APP_ENV", "production")
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "srk")
    monkeypatch.setenv("COTARCO_STORAGE_DIR", str(tmp_path))
    clear_settings_cache()
    reset_storage_adapter()
    from backend.app.core.settings import get_settings

    assert get_settings().storage_backend == "supabase"
    assert isinstance(get_storage_adapter(), SupabaseStorageAdapter)
