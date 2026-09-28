"""Tests for POST /jobs, GET /jobs, GET /jobs/{id} with RBAC."""
from .conftest import TEST_PROFILE_ID, COMERCIAL_USER_ID, OPERADOR_USER_ID
import uuid


JOB_PAYLOAD = {
    "profile_id": str(TEST_PROFILE_ID),
    "source_system": "SAMSUNG",
    "description": "Test job setembro",
    "options": {},
}


class TestCreateJob:
    def test_comercial_can_create_job(self, comercial_client):
        resp = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        assert resp.status_code == 201
        body = resp.json()
        assert body["status"] == "UPLOADED"
        assert body["profile_id"] == str(TEST_PROFILE_ID)
        assert body["created_by_id"] == str(COMERCIAL_USER_ID)

    def test_create_job_invalid_profile(self, comercial_client):
        payload = {**JOB_PAYLOAD, "profile_id": str(uuid.uuid4())}
        resp = comercial_client.post("/api/v1/jobs", json=payload)
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "PROFILE_NOT_FOUND"

    def test_operador_can_create_job(self, operador_client):
        resp = operador_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        assert resp.status_code == 201


class TestListJobs:
    def test_comercial_only_sees_own_jobs(self, comercial_client, operador_client):
        # Comercial creates one job
        r1 = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        assert r1.status_code == 201
        comercial_job_id = r1.json()["id"]

        # Operador creates one job
        r2 = operador_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        assert r2.status_code == 201
        operador_job_id = r2.json()["id"]

        # Comercial GET /jobs — should NOT see operador's job
        resp = comercial_client.get("/api/v1/jobs")
        assert resp.status_code == 200
        ids = [j["id"] for j in resp.json()["items"]]
        assert comercial_job_id in ids
        assert operador_job_id not in ids

    def test_operador_sees_all_jobs(self, comercial_client, operador_client):
        # Comercial creates a job
        r1 = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        assert r1.status_code == 201
        comercial_job_id = r1.json()["id"]

        # Operador lists — should see comercial's job
        resp = operador_client.get("/api/v1/jobs")
        assert resp.status_code == 200
        ids = [j["id"] for j in resp.json()["items"]]
        assert comercial_job_id in ids


class TestGetJobById:
    def test_comercial_gets_own_job(self, comercial_client):
        r = comercial_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        resp = comercial_client.get(f"/api/v1/jobs/{job_id}")
        assert resp.status_code == 200
        assert resp.json()["id"] == job_id

    def test_comercial_cannot_access_other_job(self, comercial_client, operador_client):
        # Operador creates a job
        r = operador_client.post("/api/v1/jobs", json=JOB_PAYLOAD)
        job_id = r.json()["id"]
        # Comercial tries to GET it
        resp = comercial_client.get(f"/api/v1/jobs/{job_id}")
        assert resp.status_code == 403

    def test_job_not_found_returns_404(self, comercial_client):
        resp = comercial_client.get(f"/api/v1/jobs/{uuid.uuid4()}")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "JOB_NOT_FOUND"
