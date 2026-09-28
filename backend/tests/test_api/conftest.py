"""Test fixtures for API layer — Phase 3.

Strategy:
- Uses FastAPI TestClient with in-memory SQLite via StaticPool.
- StaticPool forces ALL connections to share the same in-memory SQLite instance,
  so seed_db, get_db override, and db_session fixture all see the same data.
- Overrides get_db and get_current_user via app.dependency_overrides.
- Provides two mock identities: comercial_user and operador_user.
"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, event
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
from backend.app.main import app
from backend.app.api.deps import get_db, get_current_user, CurrentUser
from backend.app.infra.db.session import create_all_tables, drop_all_tables
from backend.app.infra.db.models import (
    UserOrm,
    CommercialProfileOrm,
)

# ---------------------------------------------------------------------------
# Fixed UUIDs for test identities
# ---------------------------------------------------------------------------
COMERCIAL_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000001")
OPERADOR_USER_ID = uuid.UUID("00000000-0000-0000-0000-000000000002")
TEST_PROFILE_ID = uuid.UUID("00000000-0000-0000-0000-000000000010")


@pytest.fixture(scope="session")
def test_engine():
    """
    Creates a single in-memory SQLite engine shared across ALL test connections
    via StaticPool. This ensures seed_db, get_db override, and db_session all
    operate on the exact same database instance.
    """
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    @event.listens_for(engine, "connect")
    def _set_sqlite_pragma(dbapi_connection, _connection_record):
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()

    create_all_tables(engine)
    yield engine
    drop_all_tables(engine)
    engine.dispose()


@pytest.fixture(scope="session")
def session_factory(test_engine):
    return sessionmaker(
        bind=test_engine, autocommit=False, autoflush=False, expire_on_commit=False
    )


@pytest.fixture(autouse=True, scope="function")
def seed_db(session_factory):
    """Seed baseline users and profile before each test."""
    session: Session = session_factory()
    try:
        comercial = UserOrm(
            id=COMERCIAL_USER_ID,
            email="comercial@test.ao",
            display_name="Comercial Test",
            role="COMERCIAL",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        operador = UserOrm(
            id=OPERADOR_USER_ID,
            email="operador@test.ao",
            display_name="Operador Test",
            role="OPERADOR",
            is_active=True,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        profile = CommercialProfileOrm(
            id=TEST_PROFILE_ID,
            code="TEST_PROFILE",
            name="Test Profile",
            type="MARKETPLACE",
            description="Profile for API tests",
            active=True,
            config={"integration_type": "EXCEL_EXPORT"},
            rules_version=1,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(timezone.utc),
        )
        session.merge(comercial)
        session.merge(operador)
        session.merge(profile)
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()
    yield


@pytest.fixture
def db_session(session_factory):
    session: Session = session_factory()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Client helpers with DI overrides
# ---------------------------------------------------------------------------
# We use a ContextVar so that two clients can coexist within the same test
# without overwriting each other's dependency override.

from contextvars import ContextVar as _ContextVar

_current_user_var: _ContextVar[CurrentUser | None] = _ContextVar(
    "_current_user_var", default=None
)


def _setup_shared_overrides(session_factory) -> None:
    """Install the shared db and user overrides (idempotent — called once per test)."""

    def override_get_db():
        session: Session = session_factory()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def override_get_current_user():
        user = _current_user_var.get()
        if user is None:
            raise RuntimeError("No current user set in ContextVar")
        return user

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_current_user] = override_get_current_user


class _UserClient:
    """Thin wrapper that sets the ContextVar before each HTTP call."""

    def __init__(self, user: CurrentUser, raw: TestClient):
        self._user = user
        self._raw = raw

    def _with_user(self, method, *args, **kwargs):
        token = _current_user_var.set(self._user)
        try:
            return getattr(self._raw, method)(*args, **kwargs)
        finally:
            _current_user_var.reset(token)

    def get(self, *a, **kw):
        return self._with_user("get", *a, **kw)

    def post(self, *a, **kw):
        return self._with_user("post", *a, **kw)

    def put(self, *a, **kw):
        return self._with_user("put", *a, **kw)

    def patch(self, *a, **kw):
        return self._with_user("patch", *a, **kw)

    def delete(self, *a, **kw):
        return self._with_user("delete", *a, **kw)


@pytest.fixture
def comercial_client(session_factory):
    _setup_shared_overrides(session_factory)
    user = CurrentUser(id=COMERCIAL_USER_ID, email="comercial@test.ao", role="COMERCIAL")
    raw = TestClient(app, raise_server_exceptions=True)
    yield _UserClient(user, raw)
    app.dependency_overrides.clear()


@pytest.fixture
def operador_client(session_factory):
    _setup_shared_overrides(session_factory)
    user = CurrentUser(id=OPERADOR_USER_ID, email="operador@test.ao", role="OPERADOR")
    raw = TestClient(app, raise_server_exceptions=True)
    yield _UserClient(user, raw)
    app.dependency_overrides.clear()
