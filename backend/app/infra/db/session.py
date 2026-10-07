"""SQLAlchemy 2.0 session and engine management.

Supports:
  - PostgreSQL / Supabase (staging/production) via DATABASE_URL
  - SQLite (local/tests)

GUARDRAILS:
  - SUPABASE_SERVICE_ROLE_KEY is never used for DB connections.
  - Connection strings come from environment only.
  - Production must not rely on create_all — use SQL migrations.
"""

from __future__ import annotations

from contextlib import contextmanager
from typing import Generator

from sqlalchemy import create_engine, event, text
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from backend.app.core.settings import get_settings


def _get_database_url() -> str:
    return get_settings().database_url


def create_db_engine(
    url: str | None = None,
    *,
    echo: bool = False,
    pool_size: int = 5,
    max_overflow: int = 10,
) -> Engine:
    """Create a SQLAlchemy engine tuned for local or Cloud Run usage."""
    settings = get_settings()
    resolved_url = url or settings.database_url
    is_sqlite = resolved_url.startswith("sqlite")

    connect_args: dict = {}
    extra_kwargs: dict = {}

    if is_sqlite:
        connect_args["check_same_thread"] = False
    elif settings.is_production or settings.environment in {"staging", "production"}:
        # Serverless/container: avoid large persistent pools
        extra_kwargs = {
            "poolclass": NullPool,
            "pool_pre_ping": True,
        }
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

    if is_sqlite:
        @event.listens_for(engine, "connect")
        def _set_sqlite_pragma(dbapi_connection, _connection_record):  # type: ignore[misc]
            cursor = dbapi_connection.cursor()
            cursor.execute("PRAGMA foreign_keys=ON")
            cursor.close()

    return engine


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


@contextmanager
def get_db_session() -> Generator[Session, None, None]:
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
    return create_db_engine(url=url, echo=False)


def create_all_tables(engine: Engine) -> None:
    """Create ORM tables — intended for local/tests only."""
    from backend.app.infra.db.models import Base
    Base.metadata.create_all(bind=engine)


def drop_all_tables(engine: Engine) -> None:
    from backend.app.infra.db.models import Base
    Base.metadata.drop_all(bind=engine)


def ping_database(engine: Engine) -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception:
        return False
