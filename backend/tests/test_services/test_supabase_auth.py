"""Supabase JWT verification tests (mocked secret)."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.settings import clear_settings_cache
from backend.app.infra.db.models import UserOrm
from backend.app.infra.db.session import create_all_tables
from backend.app.services.supabase_auth import (
    SupabaseAuthError,
    decode_supabase_token,
    resolve_user_from_supabase_claims,
)


@pytest.fixture
def jwt_secret(monkeypatch):
    secret = "test-supabase-jwt-secret"
    monkeypatch.setenv("SUPABASE_JWT_SECRET", secret)
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv("ENVIRONMENT", "test")
    clear_settings_cache()
    yield secret
    clear_settings_cache()


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def _make_token(secret: str, *, sub: str, email: str, exp_hours: int = 1) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": sub,
            "email": email,
            "aud": "authenticated",
            "role": "authenticated",
            "exp": now + timedelta(hours=exp_hours),
            "iat": now,
        },
        secret,
        algorithm="HS256",
    )


def test_decode_supabase_token_ok(jwt_secret):
    uid = str(uuid.uuid4())
    token = _make_token(jwt_secret, sub=uid, email="c@cotarco.ao")
    claims = decode_supabase_token(token)
    assert claims["sub"] == uid
    assert claims["email"] == "c@cotarco.ao"


def test_decode_supabase_token_rejects_bad_signature(jwt_secret):
    uid = str(uuid.uuid4())
    token = _make_token("wrong-secret", sub=uid, email="c@cotarco.ao")
    with pytest.raises(SupabaseAuthError):
        decode_supabase_token(token)


def test_resolve_user_creates_public_users_row(jwt_secret, db_session):
    uid = uuid.uuid4()
    claims = {"sub": str(uid), "email": "novo@cotarco.ao", "user_metadata": {}}
    user = resolve_user_from_supabase_claims(db_session, claims)
    assert user.id == uid
    assert user.role == "COMERCIAL"
    assert user.email == "novo@cotarco.ao"
    assert db_session.get(UserOrm, uid) is not None


def test_resolve_user_uses_db_role_not_token_role(jwt_secret, db_session):
    uid = uuid.uuid4()
    now = datetime.now(timezone.utc)
    db_session.add(
        UserOrm(
            id=uid,
            email="op@cotarco.ao",
            display_name="Op",
            role="OPERADOR",
            is_active=True,
            created_at=now,
            updated_at=now,
        )
    )
    db_session.flush()
    claims = {
        "sub": str(uid),
        "email": "op@cotarco.ao",
        "user_metadata": {"role": "ADMIN"},
    }
    user = resolve_user_from_supabase_claims(db_session, claims)
    assert user.role == "OPERADOR"
