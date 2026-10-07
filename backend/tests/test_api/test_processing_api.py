"""Tests for POST /jobs/{id}/validate, GET /jobs/{id}/summary, items, issues."""
from __future__ import annotations

import io
import uuid

import pandas as pd

from .conftest import TEST_PROFILE_ID

JOB_PAYLOAD = {
    "profile_id": str(TEST_PROFILE_ID),
    "source_system": "SAMSUNG",
    "description": "Processing test",
    "options": {},
}


def _xlsx_bytes(rows: list[dict]) -> bytes:
    buf = io.BytesIO()
    pd.DataFrame(rows).to_excel(buf, index=False)
    return buf.getvalue()


def _upload_input(client, job_id: str) -> None:
    content = _xlsx_bytes(
        [
            {"REF": "SKU-A", "PRECO": 110, "STOCK": 5},
            {"REF": "SKU-B", "PRECO": 200, "STOCK": 2},
        ]
    )
    files = {
        "file": (
            "input.xlsx",
            content,
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        )
    }
    resp = client.post(f"/api/v1/jobs/{job_id}/files?kind=INPUT", files=files)
    assert resp.status_code == 201, resp.text


class TestValidateEndpoint:
    def test_validate_without_file_returns_409(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
        assert resp.status_code == 409
        body = resp.json()
        code = body.get("error", {}).get("code") or body.get("detail", {}).get("error", {}).get("code")
        assert code == "MISSING_INPUT_FILE"

    def test_validate_uploaded_job(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        _upload_input(comercial_client, job_id)
        resp = comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
        assert resp.status_code == 200, resp.text
        body = resp.json()
        assert body["job_id"] == job_id
        assert body["status"] in ("READY_FOR_REVIEW", "NEEDS_CORRECTION")
        assert "summary" in body

    def test_validate_wrong_state_returns_409(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        _upload_input(comercial_client, job_id)
        first = comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
        assert first.status_code == 200
        # After validate, status is READY/NEEDS — not UPLOADED
        resp = comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
        assert resp.status_code == 409

    def test_validate_nonexistent_job_404(self, comercial_client):
        resp = comercial_client.post(f"/api/v1/jobs/{uuid.uuid4()}/validate")
        assert resp.status_code == 404


class TestSummaryEndpoint:
    def test_get_summary(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = comercial_client.get(f"/api/v1/jobs/{job_id}/summary")
        assert resp.status_code == 200
        body = resp.json()
        assert body["job_id"] == job_id
        assert "status" in body
        assert "issues_by_severity" in body

    def test_summary_not_found(self, comercial_client):
        resp = comercial_client.get(f"/api/v1/jobs/{uuid.uuid4()}/summary")
        assert resp.status_code == 404


class TestItemsAndIssuesEndpoints:
    def test_get_items_empty(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = comercial_client.get(f"/api/v1/jobs/{job_id}/items")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_issues_empty(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = comercial_client.get(f"/api/v1/jobs/{job_id}/issues")
        assert resp.status_code == 200
        assert resp.json() == []

    def test_get_issues_severity_filter(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = comercial_client.get(f"/api/v1/jobs/{job_id}/issues?severity=BLOCKER")
        assert resp.status_code == 200
