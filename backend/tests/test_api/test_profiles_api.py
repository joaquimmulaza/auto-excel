"""Tests for GET /api/v1/profiles and GET /api/v1/profiles/{id}."""
from .conftest import TEST_PROFILE_ID
import uuid


class TestProfilesEndpoint:
    def test_list_profiles_returns_200(self, comercial_client):
        resp = comercial_client.get("/api/v1/profiles")
        assert resp.status_code == 200
        body = resp.json()
        assert "items" in body
        assert "total" in body
        assert body["total"] >= 1

    def test_list_profiles_contains_test_profile(self, comercial_client):
        resp = comercial_client.get("/api/v1/profiles")
        ids = [item["id"] for item in resp.json()["items"]]
        assert str(TEST_PROFILE_ID) in ids

    def test_get_profile_by_id(self, comercial_client):
        resp = comercial_client.get(f"/api/v1/profiles/{TEST_PROFILE_ID}")
        assert resp.status_code == 200
        body = resp.json()
        assert body["id"] == str(TEST_PROFILE_ID)
        assert body["code"] == "TEST_PROFILE"

    def test_get_profile_not_found(self, comercial_client):
        resp = comercial_client.get(f"/api/v1/profiles/{uuid.uuid4()}")
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "PROFILE_NOT_FOUND"

    def test_list_profiles_accessible_by_operador(self, operador_client):
        resp = operador_client.get("/api/v1/profiles")
        assert resp.status_code == 200
