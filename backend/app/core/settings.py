"""Centralised environment configuration for Cotarco Commercial Manager.

Secrets must never be logged or sent to the frontend.
Service-role keys stay on the backend only.
"""
from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

_backend_env = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(_backend_env)
load_dotenv()


def _env(name: str, default: str | None = None) -> str | None:
    value = os.getenv(name)
    if value is None or value == "":
        return default
    return value


@dataclass(frozen=True)
class Settings:
    environment: str
    auth_mode: str
    database_url: str
    auth_secret: str
    supabase_url: str | None
    supabase_anon_key: str | None
    supabase_service_role_key: str | None
    supabase_jwt_secret: str | None
    storage_backend: str
    storage_bucket: str
    storage_dir: str
    allowed_origins: tuple[str, ...]
    gemini_api_key: str | None
    gemini_model: str

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_local_auth(self) -> bool:
        return self.auth_mode == "local"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


class SettingsError(RuntimeError):
    """Raised when runtime environment configuration is unsafe or incomplete."""


def _resolve_environment() -> str:
    # APP_ENV takes precedence when set (Prompt D); ENVIRONMENT remains supported.
    return (_env("APP_ENV") or _env("ENVIRONMENT", "local") or "local").lower()


def _resolve_storage_backend(environment: str) -> str:
    explicit = _env("STORAGE_BACKEND")
    if explicit:
        return explicit.lower()
    if environment == "production":
        return "supabase"
    return "local"


def validate_runtime_settings(settings: Settings) -> None:
    """Fail fast on misconfiguration that would lose files or use SQLite in prod."""
    if not settings.is_production:
        return

    if settings.is_sqlite:
        raise SettingsError(
            "DATABASE_URL must be PostgreSQL in production; SQLite is forbidden."
        )

    if settings.storage_backend == "supabase":
        missing = [
            name
            for name, value in (
                ("SUPABASE_URL", settings.supabase_url),
                ("SUPABASE_SERVICE_ROLE_KEY", settings.supabase_service_role_key),
            )
            if not value
        ]
        if missing:
            raise SettingsError(
                "Missing required production Supabase storage env vars: "
                + ", ".join(missing)
            )


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    environment = _resolve_environment()
    auth_mode = (
        _env("AUTH_MODE")
        or ("local" if environment in {"local", "test"} else "supabase")
    ).lower()
    database_url = _env("DATABASE_URL", "sqlite+pysqlite:////tmp/cotarco-ccm.db") or ""
    if database_url.startswith("postgres://"):
        database_url = database_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif database_url.startswith("postgresql://") and "+psycopg" not in database_url:
        database_url = database_url.replace("postgresql://", "postgresql+psycopg://", 1)

    origins_raw = _env(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ) or ""
    origins = tuple(o.strip() for o in origins_raw.split(",") if o.strip())

    return Settings(
        environment=environment,
        auth_mode=auth_mode,
        database_url=database_url,
        auth_secret=_env("AUTH_SECRET", "cotarco-dev-secret-change-me") or "",
        supabase_url=_env("SUPABASE_URL"),
        supabase_anon_key=_env("SUPABASE_ANON_KEY"),
        supabase_service_role_key=_env("SUPABASE_SERVICE_ROLE_KEY"),
        supabase_jwt_secret=_env("SUPABASE_JWT_SECRET"),
        storage_backend=_resolve_storage_backend(environment),
        storage_bucket=_env("STORAGE_BUCKET", "job-files") or "job-files",
        storage_dir=_env("COTARCO_STORAGE_DIR", "/tmp/cotarco-storage")
        or "/tmp/cotarco-storage",
        allowed_origins=origins,
        gemini_api_key=_env("GEMINI_API_KEY"),
        # Override: GEMINI_MODEL=gemini-3.6-flash|gemini-3.8-flash
        gemini_model=_env("GEMINI_MODEL", "gemini-3.5-flash-lite")
        or "gemini-3.5-flash-lite",
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
