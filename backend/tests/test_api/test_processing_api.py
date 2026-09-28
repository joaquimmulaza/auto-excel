"""Tests for POST /jobs/{id}/validate, GET /jobs/{id}/summary, items, issues."""
from .conftest import TEST_PROFILE_ID
import uuid


JOB_PAYLOAD = {
    "profile_id": str(TEST_PROFILE_ID),
    "source_system": "SAMSUNG",
    "description": "Processing test",
    "options": {},
}


class TestValidateEndpoint:
    def test_validate_uploaded_job(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
        assert resp.status_code == 202
        body = resp.json()
        assert body["status"] == "VALIDATING"
        assert body["job_id"] == job_id

    def test_validate_already_validating_returns_409(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        # First validate
        comercial_client.post(f"/api/v1/jobs/{job_id}/validate")
        # Second validate on same job now in VALIDATING
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
