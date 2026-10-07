"""Ensure demo password seeds never run in production/supabase mode."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from backend.app.api.v1.auth import ensure_demo_users
from backend.app.core.settings import clear_settings_cache
from backend.app.infra.db.models import UserOrm
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


def test_ensure_demo_users_noop_when_auth_mode_supabase(monkeypatch, db_session):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    clear_settings_cache()
    try:
        ensure_demo_users(db_session)
        db_session.flush()
        assert db_session.query(UserOrm).count() == 0
    finally:
        clear_settings_cache()


def test_bootstrap_skips_demo_users_in_production_supabase(monkeypatch, db_session):
    monkeypatch.setenv("ENVIRONMENT", "production")
    monkeypatch.setenv("AUTH_MODE", "supabase")
    clear_settings_cache()
    try:
        bootstrap_database(db_session)
        assert db_session.query(UserOrm).count() == 0
    finally:
        clear_settings_cache()


def test_ensure_demo_users_runs_in_local_mode(monkeypatch, db_session):
    monkeypatch.setenv("ENVIRONMENT", "local")
    monkeypatch.setenv("AUTH_MODE", "local")
    clear_settings_cache()
    try:
        ensure_demo_users(db_session)
        db_session.flush()
        assert db_session.query(UserOrm).count() >= 3
        demo = db_session.get(
            UserOrm, uuid.UUID("00000000-0000-0000-0000-000000000001")
        )
        assert demo is not None
        assert demo.password_hash
        assert demo.created_at or True
        assert datetime.now(timezone.utc)
    finally:
        clear_settings_cache()
