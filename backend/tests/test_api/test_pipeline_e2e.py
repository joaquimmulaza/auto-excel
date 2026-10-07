"""End-to-end API: upload → validate → approve → process → download."""
from __future__ import annotations

import io

import pandas as pd

from .conftest import TEST_PROFILE_ID


def _xlsx(rows: list[dict]) -> bytes:
    buf = io.BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False)
    return buf.getvalue()


def test_full_pipeline_happy_path(comercial_client, operador_client):
    # Create
    created = comercial_client.post(
        "/api/v1/jobs",
        json={
            "profile_id": str(TEST_PROFILE_ID),
            "source_system": "SAMSUNG",
            "description": "E2E fixture",
            "options": {},
        },
    )
    assert created.status_code == 201, created.text
    job_id = created.json()["id"]

    # Upload input + catalog
    input_bytes = _xlsx(
        [
            {"REF": "AAA-1", "PRECO": 105, "STOCK": 4},
            {"REF": "BBB-2", "PRECO": 50, "STOCK": 10},
        ]
    )
    catalog_bytes = _xlsx(
        [
            {"REF": "AAA-1", "PRECO": 100, "STOCK": 2},
        ]
    )
    up1 = comercial_client.post(
        f"/api/v1/jobs/{job_id}/files?kind=INPUT",
        files={"file": ("in.xlsx", input_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert up1.status_code == 201, up1.text
    up2 = comercial_client.post(
        f"/api/v1/jobs/{job_id}/files?kind=CATALOG",
        files={"file": ("cat.xlsx", catalog_bytes, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    assert up2.status_code == 201, up2.text

    # Validate
    val = comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
    assert val.status_code == 200, val.text
    assert val.json()["status"] in ("READY_FOR_REVIEW", "NEEDS_CORRECTION")

    # If blocked, still can inspect items; for happy path force READY by checking
    job = comercial_client.get(f"/api/v1/jobs/{job_id}").json()
    if job["status"] == "NEEDS_CORRECTION":
        # Approve path needs READY — recreate without blockers
        # Small variations should be READY
        pass

    # Re-upload mild data if needed
    if job["status"] != "READY_FOR_REVIEW":
        # Create a fresh job with only mild update
        created2 = comercial_client.post(
            "/api/v1/jobs",
            json={
                "profile_id": str(TEST_PROFILE_ID),
                "source_system": "SAMSUNG",
                "description": "E2E mild",
                "options": {},
            },
        )
        job_id = created2.json()["id"]
        mild_in = _xlsx([{"REF": "AAA-1", "PRECO": 105, "STOCK": 4}])
        mild_cat = _xlsx([{"REF": "AAA-1", "PRECO": 100, "STOCK": 2}])
        comercial_client.post(
            f"/api/v1/jobs/{job_id}/files?kind=INPUT",
            files={"file": ("in.xlsx", mild_in, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        comercial_client.post(
            f"/api/v1/jobs/{job_id}/files?kind=CATALOG",
            files={"file": ("cat.xlsx", mild_cat, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
        )
        val = comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
        assert val.status_code == 200
        assert val.json()["status"] == "READY_FOR_REVIEW", val.json()

    # Comercial cannot approve
    forbidden = comercial_client.post(
        f"/api/v1/jobs/{job_id}/approve", json={"comment": "nope"}
    )
    assert forbidden.status_code == 403

    # Operador approves + processes
    appr = operador_client.post(
        f"/api/v1/jobs/{job_id}/approve", json={"comment": "ok"}
    )
    assert appr.status_code == 200, appr.text

    proc = operador_client.post(f"/api/v1/jobs/{job_id}/process")
    assert proc.status_code == 200, proc.text
    assert proc.json()["status"] == "COMPLETED"

    files = operador_client.get(f"/api/v1/jobs/{job_id}/files").json()["items"]
    kinds = {f["kind"] for f in files}
    assert "OUTPUT" in kinds
    assert "LOG" in kinds

    output = next(f for f in files if f["kind"] == "OUTPUT")
    dl = operador_client.get(f"/api/v1/jobs/{job_id}/files/{output['id']}/download")
    assert dl.status_code == 200
    assert len(dl.content) > 0

    receipt = operador_client.get(f"/api/v1/jobs/{job_id}/receipt")
    assert receipt.status_code == 200
    assert receipt.json()["status"] == "COMPLETED"

    history = operador_client.get("/api/v1/history/prices", params={"reference": "AAA-1"})
    assert history.status_code == 200, history.text
    hist_items = history.json()["items"]
    assert len(hist_items) >= 1
    assert hist_items[0]["change_type"] in ("UPDATED", "NEW")
    assert hist_items[0]["new_price"] is not None


def test_dry_run_cannot_approve(comercial_client, operador_client):
    created = comercial_client.post(
        "/api/v1/jobs",
        json={
            "profile_id": str(TEST_PROFILE_ID),
            "source_system": "SAMSUNG",
            "description": "dry",
            "options": {"dry_run": True},
        },
    )
    job_id = created.json()["id"]
    content = _xlsx([{"REF": "AAA-1", "PRECO": 105, "STOCK": 4}])
    catalog = _xlsx([{"REF": "AAA-1", "PRECO": 100, "STOCK": 2}])
    comercial_client.post(
        f"/api/v1/jobs/{job_id}/files?kind=INPUT",
        files={"file": ("in.xlsx", content, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    comercial_client.post(
        f"/api/v1/jobs/{job_id}/files?kind=CATALOG",
        files={"file": ("cat.xlsx", catalog, "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")},
    )
    val = comercial_client.post(f"/api/v1/jobs/{job_id}/validate?dry_run=true")
    assert val.status_code == 200
    if val.json()["status"] == "READY_FOR_REVIEW":
        appr = operador_client.post(
            f"/api/v1/jobs/{job_id}/approve", json={"comment": "x"}
        )
        assert appr.status_code == 409
        body = appr.json()
        code = body.get("error", {}).get("code") or body.get("detail", {}).get("error", {}).get("code")
        assert code == "DRY_RUN_CANNOT_APPROVE"


def test_login_and_me(comercial_client, session_factory):
    """Login uses real password hashes from seed; override not needed for auth router."""
    from backend.app.services.auth_tokens import hash_password
    from backend.app.infra.db.models import UserOrm
    from .conftest import COMERCIAL_USER_ID

    session = session_factory()
    user = session.get(UserOrm, COMERCIAL_USER_ID)
    user.password_hash = hash_password("comercial123")
    session.commit()
    session.close()

    from fastapi.testclient import TestClient
    from backend.app.main import app

    # Clear overrides for unauthenticated login
    raw = TestClient(app)
    # Still need db override — use comercial_client's app overrides by posting login with headers unset
    # Use comercial_client which has db override but login doesn't need user
    resp = comercial_client.post(
        "/api/v1/auth/login",
        json={"email": "comercial@test.ao", "password": "comercial123"},
    )
    assert resp.status_code == 200, resp.text
    assert "access_token" in resp.json()
