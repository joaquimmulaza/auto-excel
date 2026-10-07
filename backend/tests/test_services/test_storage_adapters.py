"""Storage adapter unit tests."""
from __future__ import annotations

import uuid
from pathlib import Path

import pytest

from backend.app.core.settings import clear_settings_cache
from backend.app.services.storage import (
    LocalStorageAdapter,
    build_storage_path,
    reset_storage_adapter,
)


@pytest.fixture(autouse=True)
def _reset_storage(tmp_path, monkeypatch):
    monkeypatch.setenv("STORAGE_BACKEND", "local")
    monkeypatch.setenv("COTARCO_STORAGE_DIR", str(tmp_path))
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
    assert Path(meta["storage_path"]).is_file()
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
    # Force same path by same sha prefix + name — different content ⇒ different sha ⇒ different path.
    # Overwrite guard triggers only when path collides with different bytes.
    path_dir = tmp_path / f"jobs/{job_id}/inputs"
    path_dir.mkdir(parents=True)
    collision = path_dir / "aaaaaaaaaaaa_x.xlsx"
    collision.write_bytes(b"old")
    # Monkeypatch build path by using store then manually colliding is hard;
    # call store then write different bytes then store again with crafted adapter method.
    meta = adapter.store(
        job_id=job_id, kind="INPUT", original_name="x.xlsx", content=b"aaa"
    )
    Path(meta["storage_path"]).write_bytes(b"tampered-different")
    with pytest.raises(FileExistsError):
        adapter.store(
            job_id=job_id, kind="INPUT", original_name="x.xlsx", content=b"aaa"
        )
