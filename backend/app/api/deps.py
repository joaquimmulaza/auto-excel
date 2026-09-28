"""
Dependency injection for FastAPI routes.
Provides: get_db, get_current_user, require_role.
"""
from __future__ import annotations
import os
import uuid
from typing import Generator, Annotated
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy.orm import Session, sessionmaker
from backend.app.infra.db.session import create_db_engine

# Bearer scheme
_bearer = HTTPBearer(auto_error=True)

# Engine / session factory — lazy init
_engine = None
_SessionLocal = None


def _get_session_factory() -> sessionmaker:
    global _engine, _SessionLocal
    if _SessionLocal is None:
        url = os.getenv("DATABASE_URL", "sqlite+pysqlite:///:memory:")
        _engine = create_db_engine(url=url)
        from backend.app.infra.db.session import create_all_tables
        create_all_tables(_engine)
        _SessionLocal = sessionmaker(
            bind=_engine, autocommit=False, autoflush=False, expire_on_commit=False
        )
    return _SessionLocal


def get_db() -> Generator[Session, None, None]:
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

# ---------------------------------------------------------------------------
# Auth — in production verifies Supabase JWT; in tests injected via override
# ---------------------------------------------------------------------------


class CurrentUser:
    """Minimal representation of the authenticated user for route handlers."""

    def __init__(self, id: uuid.UUID, email: str, role: str):
        self.id = id
        self.email = email
        self.role = role


def get_current_user(
    credentials: Annotated[HTTPAuthorizationCredentials, Depends(_bearer)],
    db: DbDep,
) -> CurrentUser:
    """
    In production: validates Supabase JWT and extracts user_id + role.
    In tests: this function is overridden via app.dependency_overrides.
    """
    # Minimal stub: in real production, decode JWT from credentials.credentials
    # and look up the user. For now, raise 401 to force test override.
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


def require_role(*roles: str):
    """Factory that returns a FastAPI dependency checking the user has one of the given roles."""

    def _checker(current_user: UserDep) -> CurrentUser:
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
