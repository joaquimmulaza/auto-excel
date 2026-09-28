"""Tests for POST /jobs/{id}/approve — RBAC critical.

CRITICAL: COMERCIAL must receive HTTP 403. OPERADOR must receive HTTP 200/409.
"""
from .conftest import TEST_PROFILE_ID
import uuid

JOB_PAYLOAD = {
    "profile_id": str(TEST_PROFILE_ID),
    "source_system": "SAMSUNG",
    "description": "Approval test",
    "options": {},
}


class TestApprovalRBAC:
    def test_comercial_cannot_approve_returns_403(self, comercial_client):
        """RBAC EVIDENCE: COMERCIAL role is forbidden from approving jobs."""
        # Create a job with comercial
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        assert r.status_code == 201
        job_id = r.json()["id"]

        # Comercial tries to approve — MUST return 403
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/approve",
            json={"comment": "Tentativa de aprovação não autorizada"},
        )
        assert resp.status_code == 403, (
            f"SECURITY: COMERCIAL deve receber 403. Recebeu {resp.status_code}. "
            "RBAC falhou."
        )
        error = resp.json()["error"]
        assert error["code"] == "FORBIDDEN"

    def test_operador_approve_wrong_status_returns_409(self, operador_client):
        """Operador can call approve but job is in UPLOADED state → 409 INVALID_STATE."""
        r = operador_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = operador_client.post(
            f"/api/v1/jobs/{job_id}/approve",
            json={"comment": "Approve attempt"},
        )
        # Job is UPLOADED not READY_FOR_REVIEW → 409
        assert resp.status_code == 409
        assert resp.json()["error"]["code"] == "INVALID_STATE"

    def test_operador_approves_ready_job(self, operador_client, db_session):
        """Operador can approve a job that is READY_FOR_REVIEW."""
        from backend.app.infra.repositories.jobs import JobRepository
        # Create job
        r = operador_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]

        # Manually set to READY_FOR_REVIEW in the test DB
        repo = JobRepository(db_session)
        import uuid as _uuid
        repo.update_status(_uuid.UUID(job_id), "READY_FOR_REVIEW")
        db_session.commit()

        resp = operador_client.post(
            f"/api/v1/jobs/{job_id}/approve",
            json={"comment": "Looks good"},
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["action"] == "APPROVED"
        assert body["job_id"] == job_id

    def test_approve_nonexistent_job(self, operador_client):
        resp = operador_client.post(
            f"/api/v1/jobs/{uuid.uuid4()}/approve",
            json={"comment": "test"},
        )
        assert resp.status_code == 404
