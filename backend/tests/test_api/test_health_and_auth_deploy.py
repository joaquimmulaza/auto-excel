"""Deployment-focused API smoke tests: /health, /auth/login, /auth/me."""
from __future__ import annotations

from unittest.mock import patch

from fastapi.testclient import TestClient
from sqlalchemy.exc import OperationalError

from backend.app.main import app
from backend.app.api.deps import get_db, get_current_user
from backend.app.services.auth_tokens import hash_password
from backend.app.infra.db.models import UserOrm
from .conftest import COMERCIAL_USER_ID, TEST_PROFILE_ID


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


def test_db_lock_during_auth_does_not_mask_as_invalid_token(session_factory):
    """Regression: SQLite OperationalError in user lookup must not become INVALID_TOKEN.

    Root cause of UI "Invalid or expired token" on consecutive job submits:
    get_current_user used a broad ``except Exception`` around JWT decode *and*
    ``db.get(UserOrm)``, so ``database is locked`` was reported as auth failure.
    """
    from fastapi.security import HTTPAuthorizationCredentials
    from sqlalchemy.orm import Session
    from starlette.requests import Request

    from backend.app.api.deps import get_current_user as real_get_current_user
    from backend.app.services.auth_tokens import create_access_token

    token = create_access_token(
        user_id=COMERCIAL_USER_ID,
        email="comercial@test.ao",
        role="COMERCIAL",
    )
    creds = HTTPAuthorizationCredentials(scheme="Bearer", credentials=token)
    scope = {
        "type": "http",
        "asgi": {"version": "3.0"},
        "http_version": "1.1",
        "method": "POST",
        "scheme": "http",
        "path": "/api/v1/jobs",
        "raw_path": b"/api/v1/jobs",
        "query_string": b"",
        "headers": [],
        "client": ("127.0.0.1", 123),
        "server": ("test", 80),
    }
    request = Request(scope)

    db = session_factory()
    try:
        with patch.object(
            Session,
            "get",
            side_effect=OperationalError(
                "SELECT", {}, Exception("database is locked")
            ),
        ):
            user = real_get_current_user(request, db, creds)
        assert str(user.id) == str(COMERCIAL_USER_ID)
        assert user.email == "comercial@test.ao"
        assert user.role == "COMERCIAL"
    finally:
        db.close()

    # Integration: valid JWT + UserOrm lookup locked → endpoint must not 401 INVALID_TOKEN
    session = session_factory()
    row = session.get(UserOrm, COMERCIAL_USER_ID)
    assert row is not None
    row.password_hash = hash_password("comercial123")
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

    _orig_get = Session.get

    def _user_lookup_locked(self, entity, *args, **kwargs):
        if entity is UserOrm:
            raise OperationalError(
                "SELECT", {}, Exception("database is locked")
            )
        return _orig_get(self, entity, *args, **kwargs)

    raw = TestClient(app, raise_server_exceptions=True)
    try:
        login = raw.post(
            "/api/v1/auth/login",
            json={"email": "comercial@test.ao", "password": "comercial123"},
        )
        assert login.status_code == 200, login.text
        bearer = login.json()["access_token"]

        with patch.object(Session, "get", _user_lookup_locked):
            # profiles only needs auth + CommercialProfileOrm (not UserOrm after auth)
            profiles = raw.get(
                "/api/v1/profiles",
                headers={"Authorization": f"Bearer {bearer}"},
            )
            assert profiles.status_code == 200, profiles.text

            create = raw.post(
                "/api/v1/jobs",
                headers={"Authorization": f"Bearer {bearer}"},
                json={
                    "profile_id": str(TEST_PROFILE_ID),
                    "source_system": "SAMSUNG",
                    "description": "lock-regression",
                    "options": {"dry_run": True},
                },
            )
            assert create.status_code != 401, create.text
            err = create.json().get("error") or create.json().get("detail", {}).get(
                "error", {}
            )
            assert err.get("code") != "INVALID_TOKEN"
            assert create.status_code == 201, create.text

        bad = raw.get(
            "/api/v1/auth/me",
            headers={"Authorization": "Bearer not.a.jwt"},
        )
        assert bad.status_code == 401, bad.text
        body = bad.json()
        nested = body.get("error") or body.get("detail", {}).get("error", {})
        assert nested.get("code") == "INVALID_TOKEN"
        assert nested.get("message") == "Invalid or expired token"
    finally:
        app.dependency_overrides.clear()
