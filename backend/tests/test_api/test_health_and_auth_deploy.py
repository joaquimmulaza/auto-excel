"""Deployment-focused API smoke tests: /health, /auth/login, /auth/me."""
from __future__ import annotations

from fastapi.testclient import TestClient

from backend.app.main import app
from backend.app.api.deps import get_db, get_current_user
from backend.app.services.auth_tokens import hash_password
from backend.app.infra.db.models import UserOrm
from .conftest import COMERCIAL_USER_ID


def test_health_endpoint(comercial_client):
    resp = comercial_client.get("/health")
    assert resp.status_code == 200, resp.text
    body = resp.json()
    assert body["status"] == "ok"
    assert body["service"] == "cotarco-commercial-manager"


def test_auth_login_and_me(session_factory):
    """Exercise real JWT login + /auth/me without identity overrides."""
    session = session_factory()
    user = session.get(UserOrm, COMERCIAL_USER_ID)
    assert user is not None
    user.password_hash = hash_password("comercial123")
    session.commit()
    session.close()

    def override_get_db():
        db = session_factory()
        try:
            yield db
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides.pop(get_current_user, None)

    raw = TestClient(app, raise_server_exceptions=True)
    try:
        login = raw.post(
            "/api/v1/auth/login",
            json={"email": "comercial@test.ao", "password": "comercial123"},
        )
        assert login.status_code == 200, login.text
        token = login.json()["access_token"]
        assert token

        me = raw.get(
            "/api/v1/auth/me",
            headers={"Authorization": f"Bearer {token}"},
        )
        assert me.status_code == 200, me.text
        assert me.json()["email"] == "comercial@test.ao"
    finally:
        app.dependency_overrides.clear()
