"""Supabase JWT verification — ES256/JWKS (project default) + legacy HS256."""
from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock, patch

import jwt
import pytest
from cryptography.hazmat.primitives.asymmetric import ec
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.settings import clear_settings_cache
from backend.app.infra.db.models import UserOrm
from backend.app.infra.db.session import create_all_tables
from backend.app.services import supabase_auth
from backend.app.services.supabase_auth import (
    SupabaseAuthError,
    clear_jwks_cache,
    decode_supabase_token,
    resolve_user_from_supabase_claims,
)

SUPABASE_URL = "https://gaofsokeaqymsmgyjwfm.supabase.co"
ISSUER = f"{SUPABASE_URL}/auth/v1"


@pytest.fixture
def ec_keypair():
    return ec.generate_private_key(ec.SECP256R1())


@pytest.fixture
def supabase_settings(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", SUPABASE_URL)
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv("ENVIRONMENT", "test")
    monkeypatch.delenv("SUPABASE_JWT_SECRET", raising=False)
    clear_settings_cache()
    clear_jwks_cache()
    yield
    clear_settings_cache()
    clear_jwks_cache()


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


def _es256_token(private_key, *, sub: str, email: str, exp_hours: int = 1) -> str:
    now = datetime.now(timezone.utc)
    return jwt.encode(
        {
            "sub": sub,
            "email": email,
            "aud": "authenticated",
            "iss": ISSUER,
            "role": "authenticated",
            "exp": now + timedelta(hours=exp_hours),
            "iat": now,
        },
        private_key,
        algorithm="ES256",
        headers={"kid": "test-kid"},
    )


def test_decode_es256_via_jwks(supabase_settings, ec_keypair):
    uid = str(uuid.uuid4())
    token = _es256_token(ec_keypair, sub=uid, email="c@cotarco.ao")
    mock_key = MagicMock()
    mock_key.key = ec_keypair.public_key()
    with patch.object(supabase_auth, "_jwks_client") as mock_client_factory:
        client = MagicMock()
        client.get_signing_key_from_jwt.return_value = mock_key
        mock_client_factory.return_value = client
        claims = decode_supabase_token(token)
    assert claims["sub"] == uid
    assert claims["email"] == "c@cotarco.ao"
    client.get_signing_key_from_jwt.assert_called_once()


def test_decode_rejects_wrong_es256_key(supabase_settings, ec_keypair):
    other = ec.generate_private_key(ec.SECP256R1())
    token = _es256_token(ec_keypair, sub=str(uuid.uuid4()), email="c@cotarco.ao")
    mock_key = MagicMock()
    mock_key.key = other.public_key()
    with patch.object(supabase_auth, "_jwks_client") as mock_client_factory:
        client = MagicMock()
        client.get_signing_key_from_jwt.return_value = mock_key
        mock_client_factory.return_value = client
        with pytest.raises(SupabaseAuthError):
            decode_supabase_token(token)


def test_legacy_hs256_when_token_alg_is_hs256(monkeypatch, supabase_settings):
    secret = "legacy-jwt-secret-for-tests"
    monkeypatch.setenv("SUPABASE_JWT_SECRET", secret)
    clear_settings_cache()
    uid = str(uuid.uuid4())
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": uid,
            "email": "legacy@cotarco.ao",
            "aud": "authenticated",
            "iss": ISSUER,
            "exp": now + timedelta(hours=1),
            "iat": now,
        },
        secret,
        algorithm="HS256",
    )
    claims = decode_supabase_token(token)
    assert claims["sub"] == uid


def test_hs256_without_secret_fails(supabase_settings):
    now = datetime.now(timezone.utc)
    token = jwt.encode(
        {
            "sub": str(uuid.uuid4()),
            "aud": "authenticated",
            "iss": ISSUER,
            "exp": now + timedelta(hours=1),
            "iat": now,
        },
        "any",
        algorithm="HS256",
    )
    with pytest.raises(SupabaseAuthError):
        decode_supabase_token(token)


def test_resolve_user_ignores_metadata_role(supabase_settings, db_session):
    uid = uuid.uuid4()
    claims = {
        "sub": str(uid),
        "email": "novo@cotarco.ao",
        "user_metadata": {"role": "ADMIN"},
    }
    user = resolve_user_from_supabase_claims(db_session, claims)
    assert user.role == "COMERCIAL"


def test_resolve_user_keeps_db_role(supabase_settings, db_session):
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
