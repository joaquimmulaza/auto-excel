from __future__ import annotations

import uuid
from typing import Annotated, Optional

from fastapi import Depends, HTTPException, Request, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.settings import get_settings

_bearer = HTTPBearer(auto_error=False)
_engine = None
_SessionLocal = None


def _get_session_factory():
    global _engine, _SessionLocal
    if _SessionLocal is None:
        settings = get_settings()
        url = settings.database_url
        is_mem = url in ("sqlite+pysqlite:///:memory:", "sqlite:///:memory:")
        is_sqlite = url.startswith("sqlite")
        if is_mem:
            _engine = create_engine(
                url, connect_args={"check_same_thread": False}, poolclass=StaticPool
            )

            @event.listens_for(_engine, "connect")
            def _pragma(dbapi_conn, _record):
                c = dbapi_conn.cursor()
                c.execute("PRAGMA foreign_keys=ON")
                c.close()
        else:
            from backend.app.infra.db.session import create_db_engine

            _engine = create_db_engine(url=url)
            if is_sqlite:
                @event.listens_for(_engine, "connect")
                def _pragma_file(dbapi_conn, _record):
                    c = dbapi_conn.cursor()
                    c.execute("PRAGMA foreign_keys=ON")
                    c.close()

        # create_all only for local/test — production uses SQL migrations
        if settings.environment in {"local", "test"} or is_sqlite:
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
    settings = get_settings()

    if credentials and credentials.credentials:
        token = credentials.credentials
        try:
            from backend.app.infra.db.models import UserOrm

            if settings.auth_mode == "supabase":
                from backend.app.services.supabase_auth import (
                    SupabaseAuthError,
                    decode_supabase_token,
                    resolve_user_from_supabase_claims,
                )

                try:
                    claims = decode_supabase_token(token)
                    user = resolve_user_from_supabase_claims(db, claims)
                    return CurrentUser(id=user.id, email=user.email, role=user.role)
                except SupabaseAuthError:
                    # Allow local HS256 tokens only when AUTH_MODE is mixed via local fallback
                    # In pure supabase mode, reject.
                    raise
            else:
                from backend.app.services.auth_tokens import decode_access_token

                payload = decode_access_token(token)
                uid = uuid.UUID(payload["sub"])
                user = db.get(UserOrm, uid)
                if user and user.is_active:
                    return CurrentUser(id=user.id, email=user.email, role=user.role)
                return CurrentUser(
                    id=uid,
                    email=payload.get("email", "user@cotarco.ao"),
                    role=payload.get("role", "COMERCIAL"),
                )
        except Exception:
            # In supabase mode, also try local JWT for dual-run tests if AUTH_SECRET matches
            if settings.auth_mode == "supabase":
                try:
                    from backend.app.infra.db.models import UserOrm
                    from backend.app.services.auth_tokens import decode_access_token

                    payload = decode_access_token(token)
                    # Only accept local tokens when they carry explicit local issuer mark
                    if payload.get("iss") == "cotarco-local":
                        uid = uuid.UUID(payload["sub"])
                        user = db.get(UserOrm, uid)
                        if user and user.is_active:
                            return CurrentUser(
                                id=user.id, email=user.email, role=user.role
                            )
                except Exception:
                    pass
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid or expired token",
                        "request_id": getattr(request.state, "request_id", ""),
                    }
                },
            )

    # Dev / test header fallback — never in production
    if settings.environment in {"local", "test"} and settings.auth_mode == "local":
        x_user_id = request.headers.get("x-user-id")
        if x_user_id:
            try:
                uid = uuid.UUID(x_user_id)
                from backend.app.infra.db.models import UserOrm

                user = db.get(UserOrm, uid)
                if user and user.is_active:
                    return CurrentUser(id=user.id, email=user.email, role=user.role)
                return CurrentUser(
                    id=uid, email="mock@cotarco.ao", role=_role_from_preset(uid)
                )
            except ValueError:
                pass

    raise HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error": {
                "code": "NOT_AUTHENTICATED",
                "message": "Token required",
                "request_id": getattr(request.state, "request_id", ""),
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
                        "message": f"Requires role in {roles}",
                        "request_id": "",
                    }
                },
            )
        return current_user

    return _checker
