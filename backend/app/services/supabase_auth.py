"""Supabase Auth JWT verification and public.users sync."""
from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

import jwt
from sqlalchemy.orm import Session

from backend.app.core.settings import get_settings
from backend.app.infra.db.models import UserOrm

logger = logging.getLogger(__name__)


class SupabaseAuthError(Exception):
    pass


def decode_supabase_token(token: str) -> dict[str, Any]:
    """Validate a Supabase access token and return claims.

    Uses SUPABASE_JWT_SECRET (HS256) when available — the standard Supabase
    JWT secret from project settings. Role claims in the token are NOT trusted
    for RBAC; callers must resolve role from public.users.
    """
    settings = get_settings()
    secret = settings.supabase_jwt_secret
    if not secret:
        raise SupabaseAuthError("SUPABASE_JWT_SECRET is not configured")

    try:
        payload = jwt.decode(
            token,
            secret,
            algorithms=["HS256"],
            audience="authenticated",
            options={"require": ["exp", "sub"]},
        )
    except jwt.PyJWTError as exc:
        raise SupabaseAuthError(str(exc)) from exc

    if not payload.get("sub"):
        raise SupabaseAuthError("Token missing subject")
    return payload


def resolve_user_from_supabase_claims(
    db: Session,
    claims: dict[str, Any],
) -> UserOrm:
    """Load or upsert public.users from validated Supabase claims."""
    uid = uuid.UUID(str(claims["sub"]))
    email = (claims.get("email") or "").lower()
    meta = claims.get("user_metadata") or claims.get("app_metadata") or {}
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

    # New auth user without public.users row — create with safe default role
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
