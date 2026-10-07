"""Production fail-fast: reject SQLite and incomplete Supabase config."""
from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.core.settings import (
    SettingsError,
    clear_settings_cache,
    get_settings,
    validate_runtime_settings,
)
from backend.app.infra.db.models import CommercialProfileOrm, UserOrm
from backend.app.infra.db.session import create_all_tables
from backend.app.services.bootstrap import bootstrap_database


@pytest.fixture
def db_session():
    engine = create_engine(
        "sqlite+pysqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    create_all_tables(engine)
    Session = sessionmaker(bind=engine, autocommit=False, autoflush=False)
    session = Session()
    try:
        yield session
    finally:
        session.close()


def test_validate_production_rejects_sqlite(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv("DATABASE_URL", "sqlite+pysqlite:////tmp/bad.db")
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service")
    clear_settings_cache()
    try:
        with pytest.raises(SettingsError, match="PostgreSQL"):
            validate_runtime_settings(get_settings())
    finally:
        clear_settings_cache()


def test_validate_production_requires_supabase_service_role(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:x@localhost:5432/postgres",
    )
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    monkeypatch.delenv("SUPABASE_SERVICE_ROLE_KEY", raising=False)
    clear_settings_cache()
    try:
        with pytest.raises(SettingsError, match="SUPABASE_SERVICE_ROLE_KEY"):
            validate_runtime_settings(get_settings())
    finally:
        clear_settings_cache()


def test_validate_production_ok_with_postgres_and_supabase(monkeypatch):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql://postgres:x@localhost:5432/postgres",
    )
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_ANON_KEY", "anon")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service")
    clear_settings_cache()
    try:
        settings = get_settings()
        validate_runtime_settings(settings)
        assert settings.database_url.startswith("postgresql+psycopg://")
    finally:
        clear_settings_cache()


def test_bootstrap_skips_seed_profiles_in_production(monkeypatch, db_session):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    clear_settings_cache()
    try:
        bootstrap_database(db_session)
        assert db_session.query(UserOrm).count() == 0
        assert db_session.query(CommercialProfileOrm).count() == 0
    finally:
        clear_settings_cache()
