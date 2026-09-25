"""SQLAlchemy 2.0 session and engine management.

Supports two modes:
  - ``ASYNC_DATABASE_URL`` / ``DATABASE_URL``  → PostgreSQL / Supabase (production)
  - SQLite in-memory                            → tests (via ``get_test_engine()``)

GUARDRAILS:
  - SUPABASE_SERVICE_ROLE_KEY is never exposed in client-accessible code.
  - Connection strings are loaded from environment variables only.
  - ``poolclass=NullPool`` is used in test mode to avoid connection leaks.
"""

from __future__ import annotations

import os
from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker


# ---------------------------------------------------------------------------
# Connection URL resolution
# ---------------------------------------------------------------------------

def _get_database_url() -> str:
    """Resolve the database URL from environment.

    Priority:
      1. ``DATABASE_URL`` env var  (PostgreSQL / Supabase connection string)
      2. SQLite in-memory fallback for local development without Supabase

    Never use SUPABASE_SERVICE_ROLE_KEY here — that key must stay server-side
    only and is NOT used for standard DB connections.
    """
    url = os.getenv("DATABASE_URL")
    if url:
        # Supabase / PostgreSQL connection pooler uses ``postgresql+psycopg2://``
        # or ``postgresql://`` — normalise the scheme for SQLAlchemy 2.x
        if url.startswith("postgres://"):
            url = url.replace("postgres://", "postgresql+psycopg2://", 1)
        return url
    # Fallback: SQLite in-memory for local development / testing
    return "sqlite+pysqlite:///:memory:"


# ---------------------------------------------------------------------------
# Engine factory
# ---------------------------------------------------------------------------

def create_db_engine(
    url: str | None = None,
    *,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
) -> Engine:
    """Create a SQLAlchemy engine.

    Args:
        url: Database URL. Defaults to ``_get_database_url()``.
        echo: Enable SQL logging (never enable in production with sensitive data).
        pool_size: Connection pool size (ignored for SQLite).
        max_overflow: Pool overflow (ignored for SQLite).

    Returns:
        Configured ``Engine`` instance.
    """
    resolved_url = url or _get_database_url()
    is_sqlite = resolved_url.startswith("sqlite")

    connect_args: dict = {}
    extra_kwargs: dict = {}

    if is_sqlite:
        # SQLite requires check_same_thread=False for multi-threaded usage
        connect_args["check_same_thread"] = False
    else:
        extra_kwargs = {
            "pool_size": pool_size,
            "max_overflow": max_overflow,
            "pool_pre_ping": True,
        }

    engine = create_engine(
        resolved_url,
        echo=echo,
        connect_args=connect_args,
        **extra_kwargs,
    )

    # For SQLite: enable foreign key enforcement (OFF by default in SQLite)
    if is_sqlite:
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record):  # type: ignore[misc]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


# ---------------------------------------------------------------------------
# Global engine & session factory (lazily initialised)
# ---------------------------------------------------------------------------

_engine: Engine | None = None
_SessionLocal: sessionmaker[Session] | None = None


def _get_engine() -> Engine:
    global _engine
    if _engine is None:
        _engine = create_db_engine()
    return _engine


def _get_session_factory() -> sessionmaker[Session]:
    global _SessionLocal
    if _SessionLocal is None:
        _SessionLocal = sessionmaker(
            bind=_get_engine(),
            autocommit=False,
            autoflush=False,
            expire_on_commit=False,
        )
    return _SessionLocal


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------

@contextmanager
def get_db_session() -> Generator[Session, None, None]:
    """Context manager yielding a transactional database session.

    Usage::

        with get_db_session() as session:
            session.add(entity)
            session.commit()

    Rolls back automatically on exception.
    """
    factory = _get_session_factory()
    session: Session = factory()
    try:
        yield session
        session.commit()
    except Exception:
        session.rollback()
        raise
    finally:
        session.close()


def get_test_engine(url: str = "sqlite+pysqlite:///:memory:") -> Engine:
    """Create an isolated test engine.

    Uses SQLite in-memory by default. Can be overridden with a PostgreSQL
    URL to run integration tests against a real Supabase project.

    Must be used with ``create_all_tables()`` to set up the schema.
    """
    return create_db_engine(url=url, echo=False)


def create_all_tables(engine: Engine) -> None:
    """Create all ORM-mapped tables in the given engine.

    Intended for testing only. Production schema is managed by
    ``backend/migrations/`` SQL scripts executed in Supabase SQL Editor.
    """
    from backend.app.infra.db.models import Base
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine: Engine) -> None:
    """Drop all ORM-mapped tables — TEST USE ONLY."""
    from backend.app.infra.db.models import Base
    Base.metadata.drop_all(bind=engine)


def ping_database(engine: Engine) -> bool:
    """Verify database connectivity. Returns True if reachable."""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
