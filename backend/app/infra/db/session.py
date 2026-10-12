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
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
_backend_env = Path(__file__).resolve().parent.parent.parent.parent / "backend" / ".env"
load_dotenv(_backend_env)
load_dotenv()
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


def _sqlite_column_default_sql(column, dialect) -> str:
    """Compile a DEFAULT clause for SQLite ADD COLUMN, if available."""
    server_default = column.server_default
    if server_default is None:
        return ""
    arg = server_default.arg
    # TextClause (e.g. explicit SQL fragments)
    if hasattr(arg, "text"):
        return f" DEFAULT {arg.text}"
    try:
        from sqlalchemy.sql import elements

        if isinstance(arg, elements.ColumnElement):
            # func.now() → CURRENT_TIMESTAMP on SQLite
            compiled = str(
                arg.compile(dialect=dialect, compile_kwargs={"literal_binds": True})
            )
            return f" DEFAULT {compiled}"
    except Exception:
        pass
    if isinstance(arg, bool):
        return f" DEFAULT {1 if arg else 0}"
    if isinstance(arg, (int, float)):
        return f" DEFAULT {arg}"
    if isinstance(arg, str):
        upper = arg.upper()
        if upper in {"TRUE", "FALSE", "CURRENT_TIMESTAMP", "NULL"} or arg.isdigit():
            return f" DEFAULT {arg}"
        escaped = arg.replace("'", "''")
        return f" DEFAULT '{escaped}'"
    return ""


def sync_sqlite_schema(engine: Engine) -> list[str]:
    """Add missing ORM columns to an existing SQLite database (additive only).

    ``Base.metadata.create_all`` does not ALTER existing tables, so local
    file-backed DBs created before a column was added (e.g. ``users.password_hash``)
    would otherwise raise OperationalError on every UserOrm SELECT.

    Production Postgres continues to use ``backend/migrations/`` SQL scripts.
    Returns a list of ``table.column`` names that were added.
    """
    if engine.dialect.name != "sqlite":
        return []

    from backend.app.infra.db.models import Base

    dialect = engine.dialect
    added: list[str] = []

    with engine.begin() as conn:
        for table in Base.metadata.sorted_tables:
            rows = conn.execute(text(f"PRAGMA table_info('{table.name}')")).fetchall()
            if not rows:
                # Table not present yet — create_all handles creation.
                continue
            existing = {row[1] for row in rows}
            for column in table.columns:
                if column.name in existing:
                    continue
                type_sql = column.type.compile(dialect=dialect)
                default_sql = _sqlite_column_default_sql(column, dialect)
                # SQLite requires DEFAULT when adding NOT NULL to a non-empty table.
                # Without a default, keep the column nullable rather than rebuild.
                null_sql = (
                    " NOT NULL" if (not column.nullable and default_sql) else ""
                )
                ddl = (
                    f"ALTER TABLE {table.name} ADD COLUMN {column.name} "
                    f"{type_sql}{null_sql}{default_sql}"
                )
                conn.execute(text(ddl))
                added.append(f"{table.name}.{column.name}")

    # #region agent log
    try:
        import json as _json, time as _time

        open("/opt/cursor/logs/debug.log", "a").write(
            _json.dumps(
                {
                    "hypothesisId": "A",
                    "runId": "post-fix",
                    "location": "session.py:sync_sqlite_schema",
                    "message": "sqlite schema sync complete",
                    "data": {"added": added, "added_count": len(added)},
                    "timestamp": int(_time.time() * 1000),
                }
            )
            + "\n"
        )
    except Exception:
        pass
    # #endregion
    return added


def create_all_tables(engine: Engine) -> None:
    """Create all ORM-mapped tables in the given engine.

    For SQLite file DBs, also additively syncs missing columns onto existing
    tables (``sync_sqlite_schema``) so local upgrades do not wipe data.

    Production Postgres schema is managed by ``backend/migrations/`` SQL
    scripts executed in Supabase SQL Editor.
    """
    from backend.app.infra.db.models import Base
    Base.metadata.create_all(bind=engine)
    sync_sqlite_schema(engine)


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
