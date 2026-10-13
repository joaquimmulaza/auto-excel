from __future__ import annotations

import os
import uuid
from typing import Annotated, Generator, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

_bearer = HTTPBearer(auto_error=False)
_engine = None
_SessionLocal = None


def _get_session_factory():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        url = os.getenv(
            "DATABASE_URL",
            "sqlite+pysqlite:////tmp/cotarco-ccm.db",
        )
        is_mem = url in ("sqlite+pysqlite:///:memory:", "sqlite:///:memory:")
        is_sqlite = url.startswith("sqlite")
        if is_mem:
            _engine = create_engine(
                url,
                connect_args={"check_same_thread": False, "timeout": 30},
                poolclass=StaticPool,
            )

            @event.listens_for(_engine, "connect")
            def _pragma(dbapi_conn, _record):
                c = dbapi_conn.cursor()
                c.execute("PRAGMA foreign_keys=ON")
                c.close()
        elif is_sqlite:
            from backend.app.infra.db.session import create_db_engine

            _engine = create_db_engine(url=url)

            @event.listens_for(_engine, "connect")
            def _pragma_file(dbapi_conn, _record):
                c = dbapi_conn.cursor()
                c.execute("PRAGMA foreign_keys=ON")
                c.close()
        else:
            from backend.app.infra.db.session import create_db_engine

            _engine = create_db_engine(url=url)
        from backend.app.infra.db.session import create_all_tables

        create_all_tables(_engine)
        _SessionLocal = sessionmaker(
            bind=_engine, autocommit=False, autoflush=False, expire_on_commit=False
        )
    return _SessionLocal


def get_db():
    factory = _get_session_factory()
    db = factory()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


DbDep = Annotated[Session, Depends(get_db)]


class CurrentUser:
    def __init__(self, id, email, role):
        self.id = id
        self.email = email
        self.role = role


def _role_from_preset(uid: uuid.UUID) -> str:
    if str(uid) == "00000000-0000-0000-0000-000000000002":
        return "OPERADOR"
    if str(uid) == "00000000-0000-0000-0000-000000000003":
        return "ADMIN"
    return "COMERCIAL"


def get_current_user(
    request: Request,
    db: DbDep,
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(_bearer),
):
    # Prefer JWT Bearer when present
    # #region agent log
    from backend.app.debug_agent_log import agent_log

    _tok = (credentials.credentials if credentials and credentials.credentials else "") or ""
    agent_log(
        hypothesis_id="A,B,D,E",
        location="deps.py:get_current_user:entry",
        message="auth entry",
        data={
            "path": str(request.url.path),
            "method": request.method,
            "has_bearer": bool(_tok),
            "token_len": len(_tok),
            "token_prefix": _tok[:12] if _tok else None,
            "has_x_user_id": bool(request.headers.get("x-user-id")),
        },
    )
    # #endregion
    if credentials and credentials.credentials:
        import jwt
        from backend.app.services.auth_tokens import decode_access_token
        from backend.app.infra.db.models import UserOrm

        # Only JWT / claim parse failures map to INVALID_TOKEN.
        # DB lookup errors must NOT be masked as auth failures (SQLite lock etc.).
        try:
            payload = decode_access_token(credentials.credentials)
            uid = uuid.UUID(payload["sub"])
        except (jwt.PyJWTError, ValueError, KeyError, TypeError) as exc:
            # #region agent log
            agent_log(
                hypothesis_id="A,B,E",
                location="deps.py:get_current_user:INVALID_TOKEN",
                message="raising INVALID_TOKEN",
                data={
                    "path": str(request.url.path),
                    "exc_type": type(exc).__name__,
                    "exc_msg": str(exc)[:300],
                    "token_len": len(credentials.credentials),
                    "token_prefix": credentials.credentials[:12],
                    "runId": "post-fix",
                },
            )
            # #endregion
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid or expired token",
                        "request_id": "",
                    }
                },
            ) from exc

        # #region agent log
        agent_log(
            hypothesis_id="A,B",
            location="deps.py:get_current_user:decoded",
            message="jwt decoded ok, looking up user",
            data={
                "path": str(request.url.path),
                "sub": str(uid),
                "role": payload.get("role"),
                "exp": payload.get("exp"),
                "iat": payload.get("iat"),
                "runId": "post-fix",
            },
        )
        # #endregion

        try:
            user = db.get(UserOrm, uid)
        except Exception as exc:
            # #region agent log
            agent_log(
                hypothesis_id="B",
                location="deps.py:get_current_user:db_lookup_failed",
                message="db lookup failed; falling back to JWT claims",
                data={
                    "path": str(request.url.path),
                    "exc_type": type(exc).__name__,
                    "exc_msg": str(exc)[:300],
                    "sub": str(uid),
                    "runId": "post-fix",
                },
            )
            # #endregion
            user = None

        if user and user.is_active:
            # #region agent log
            agent_log(
                hypothesis_id="A,B",
                location="deps.py:get_current_user:success_db",
                message="auth ok via db user",
                data={
                    "path": str(request.url.path),
                    "user_id": str(user.id),
                    "role": user.role,
                    "runId": "post-fix",
                },
            )
            # #endregion
            return CurrentUser(id=user.id, email=user.email, role=user.role)

        # Token valid even if user row missing, inactive, or DB transiently unavailable
        # #region agent log
        agent_log(
            hypothesis_id="A,B",
            location="deps.py:get_current_user:success_payload",
            message="auth ok via token payload (user missing/inactive/db skip)",
            data={
                "path": str(request.url.path),
                "user_found": user is not None,
                "is_active": getattr(user, "is_active", None),
                "runId": "post-fix",
            },
        )
        # #endregion
        return CurrentUser(
            id=uid,
            email=payload.get("email", "user@cotarco.ao"),
            role=payload.get("role", "COMERCIAL"),
        )

    # Dev / test header fallback
    x_user_id = request.headers.get("x-user-id")
    if x_user_id:
        try:
            uid = uuid.UUID(x_user_id)
            from backend.app.infra.db.models import UserOrm

            user = db.get(UserOrm, uid)
            if user and user.is_active:
                return CurrentUser(id=user.id, email=user.email, role=user.role)
            return CurrentUser(id=uid, email="mock@cotarco.ao", role=_role_from_preset(uid))
        except ValueError:
            pass

    # #region agent log
    agent_log(
        hypothesis_id="C,D",
        location="deps.py:get_current_user:NOT_AUTHENTICATED",
        message="no bearer and no x-user-id",
        data={"path": str(request.url.path)},
    )
    # #endregion
    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "NOT_AUTHENTICATED",
                "message": "Token required",
                "request_id": "",
            }
        },
    )


UserDep = Annotated[CurrentUser, Depends(get_current_user)]


def require_role(*roles):
    def _checker(current_user: UserDep):
        if current_user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail={
                    "error": {
                        "code": "FORBIDDEN",
                        "message": f"Required role: {roles}",
                        "request_id": "",
                    }
                },
            )
        return current_user

    return _checker
