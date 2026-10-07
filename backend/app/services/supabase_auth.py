"""Supabase Auth JWT verification and public.users sync.

Production tokens for cotarco-ccm use asymmetric JWT Signing Keys (ES256)
verified via JWKS. Legacy HS256 (SUPABASE_JWT_SECRET) is an optional fallback
only when the token header declares alg=HS256.
"""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from functools import lru_cache
from typing import Any

import jwt
from jwt import PyJWKClient
from sqlalchemy.orm import Session

from backend.app.core.settings import get_settings
from backend.app.infra.db.models import UserOrm

logger = logging.getLogger(__name__)

ASYMMETRIC_ALGS = ("ES256", "RS256")
LEGACY_ALG = "HS256"


class SupabaseAuthError(Exception):
    pass


@lru_cache(maxsize=4)
def _jwks_client(supabase_url: str) -> PyJWKClient:
    base = supabase_url.rstrip("/")
    return PyJWKClient(f"{base}/auth/v1/.well-known/jwks.json", cache_keys=True)


def clear_jwks_cache() -> None:
    _jwks_client.cache_clear()


def _token_alg(token: str) -> str | None:
    try:
        header = jwt.get_unverified_header(token)
    except jwt.PyJWTError:
        return None
    alg = header.get("alg")
    return str(alg) if alg else None


def _issuer(supabase_url: str) -> str:
    return f"{supabase_url.rstrip('/')}/auth/v1"


def decode_supabase_token(token: str) -> dict[str, Any]:
    """Validate a Supabase access token and return claims.

    Prefer JWKS (ES256/RS256). Fall back to legacy HS256 only when the token
    is HS256 and SUPABASE_JWT_SECRET is configured.

    Authorization claims in the token (role, app_metadata.role, etc.) are NOT
    trusted for RBAC — callers must resolve role from public.users.
    """
    settings = get_settings()
    if not settings.supabase_url:
        raise SupabaseAuthError("SUPABASE_URL is not configured")

    alg = _token_alg(token)
    if not alg:
        raise SupabaseAuthError("Unable to read JWT header")

    decode_kwargs: dict[str, Any] = {
        "audience": "authenticated",
        "issuer": _issuer(settings.supabase_url),
        "options": {"require": ["exp", "sub"]},
    }

    try:
        if alg in ASYMMETRIC_ALGS:
            client = _jwks_client(settings.supabase_url)
            signing_key = client.get_signing_key_from_jwt(token)
            payload = jwt.decode(
                token,
                signing_key.key,
                algorithms=list(ASYMMETRIC_ALGS),
                **decode_kwargs,
            )
        elif alg == LEGACY_ALG:
            secret = settings.supabase_jwt_secret
            if not secret:
                raise SupabaseAuthError(
                    "Token is HS256 but SUPABASE_JWT_SECRET is not configured"
                )
            payload = jwt.decode(
                token,
                secret,
                algorithms=[LEGACY_ALG],
                **decode_kwargs,
            )
        else:
            raise SupabaseAuthError(f"Unsupported JWT algorithm: {alg}")
    except SupabaseAuthError:
        raise
    except jwt.PyJWTError as exc:
        raise SupabaseAuthError(str(exc)) from exc

    if not payload.get("sub"):
        raise SupabaseAuthError("Token missing subject")
    return payload


def resolve_user_from_supabase_claims(
    db: Session,
    claims: dict[str, Any],
) -> UserOrm:
    """Load or upsert public.users from validated Supabase claims.

    New users always receive role=COMERCIAL. Token/user_metadata role is ignored.
    """
    uid = uuid.UUID(str(claims["sub"]))
    email = (claims.get("email") or "").lower()
    meta = claims.get("user_metadata") or {}
    if not isinstance(meta, dict):
        meta = {}
    display_name = meta.get("display_name") or meta.get("full_name")

    user = db.get(UserOrm, uid)
    if user:
        if email and user.email != email:
            user.email = email
        if display_name and not user.display_name:
            user.display_name = display_name
        if not user.is_active:
            raise SupabaseAuthError("User is inactive")
        return user

    now = datetime.now(timezone.utc)
    user = UserOrm(
        id=uid,
        email=email or f"{uid}@users.cotarco.local",
        display_name=display_name,
        role="COMERCIAL",
        password_hash=None,
        is_active=True,
        created_at=now,
        updated_at=now,
    )
    db.add(user)
    db.flush()
    logger.info("USER_SYNCED id=%s email=%s", uid, user.email)
    return user
