"""JWT helpers for local auth (Supabase Auth can replace later)."""
from __future__ import annotations

import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
ALGORITHM = "HS256"


def _secret() -> str:
    return os.getenv("AUTH_SECRET", "cotarco-dev-secret-change-me")


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def verify_password(password: str, password_hash: str | None) -> bool:
    if not password_hash:
        return False
    return pwd_context.verify(password, password_hash)


def create_access_token(*, user_id: uuid.UUID, email: str, role: str, hours: int = 12) -> str:
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "email": email,
        "role": role,
        "exp": datetime.now(timezone.utc) + timedelta(hours=hours),
        "iat": datetime.now(timezone.utc),
    }
    token = jwt.encode(payload, _secret(), algorithm=ALGORITHM)
    # #region agent log
    from backend.app.debug_agent_log import agent_log
    import hashlib

    secret = _secret()
    agent_log(
        hypothesis_id="A,E",
        location="auth_tokens.py:create_access_token",
        message="token created",
        data={
            "user_id": str(user_id),
            "role": role,
            "hours": hours,
            "token_len": len(token) if isinstance(token, str) else None,
            "secret_fp": hashlib.sha256(secret.encode()).hexdigest()[:10],
            "exp": payload["exp"].isoformat(),
        },
    )
    # #endregion
    return token


def decode_access_token(token: str) -> dict[str, Any]:
    # #region agent log
    from backend.app.debug_agent_log import agent_log
    import hashlib

    secret = _secret()
    secret_fp = hashlib.sha256(secret.encode()).hexdigest()[:10]
    try:
        payload = jwt.decode(token, secret, algorithms=[ALGORITHM])
        agent_log(
            hypothesis_id="A,E",
            location="auth_tokens.py:decode_access_token:ok",
            message="decode ok",
            data={
                "token_len": len(token),
                "token_prefix": token[:12],
                "secret_fp": secret_fp,
                "sub": payload.get("sub"),
                "exp": payload.get("exp"),
            },
        )
        return payload
    except Exception as exc:
        agent_log(
            hypothesis_id="A,E",
            location="auth_tokens.py:decode_access_token:fail",
            message="decode failed",
            data={
                "token_len": len(token),
                "token_prefix": token[:12] if token else None,
                "secret_fp": secret_fp,
                "exc_type": type(exc).__name__,
                "exc_msg": str(exc)[:300],
            },
        )
        raise
    # #endregion
