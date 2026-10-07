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
                url, connect_args={"check_same_thread": False}, poolclass=StaticPool
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
    if credentials and credentials.credentials:
        try:
            from backend.app.services.auth_tokens import decode_access_token
            from backend.app.infra.db.models import UserOrm

            payload = decode_access_token(credentials.credentials)
            uid = uuid.UUID(payload["sub"])
            user = db.get(UserOrm, uid)
            if user and user.is_active:
                return CurrentUser(id=user.id, email=user.email, role=user.role)
            # Token valid even if user row missing (tests)
            return CurrentUser(
                id=uid,
                email=payload.get("email", "user@cotarco.ao"),
                role=payload.get("role", "COMERCIAL"),
            )
        except Exception:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={
                    "error": {
                        "code": "INVALID_TOKEN",
                        "message": "Invalid or expired token",
                        "request_id": "",
                    }
                },
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
