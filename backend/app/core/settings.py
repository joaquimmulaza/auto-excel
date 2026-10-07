"""Centralised environment configuration for Cotarco Commercial Manager.

Secrets must never be logged or sent to the frontend.
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
    cors_allow_vercel_preview: bool

    @property
    def is_production(self) -> bool:
        return self.environment == "production"

    @property
    def is_local_auth(self) -> bool:
        return self.auth_mode == "local"

    @property
    def is_sqlite(self) -> bool:
        return self.database_url.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    environment = (_env("ENVIRONMENT", "local") or "local").lower()
    auth_mode = (_env("AUTH_MODE") or ("local" if environment in {"local", "test"} else "supabase")).lower()
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

    # Preview regex only outside production (explicit allowlist required in prod)
    cors_allow_vercel_preview = environment != "production" and (
        (_env("CORS_ALLOW_VERCEL_PREVIEW", "true") or "true").lower() == "true"
    )

    return Settings(
        environment=environment,
        auth_mode=auth_mode,
        database_url=database_url,
        auth_secret=_env("AUTH_SECRET", "cotarco-dev-secret-change-me") or "",
        supabase_url=_env("SUPABASE_URL"),
        supabase_anon_key=_env("SUPABASE_ANON_KEY"),
        supabase_service_role_key=_env("SUPABASE_SERVICE_ROLE_KEY"),
        supabase_jwt_secret=_env("SUPABASE_JWT_SECRET"),
        storage_backend=(_env("STORAGE_BACKEND", "local") or "local").lower(),
        storage_bucket=_env("STORAGE_BUCKET", "job-files") or "job-files",
        storage_dir=_env("COTARCO_STORAGE_DIR", "/tmp/cotarco-storage") or "/tmp/cotarco-storage",
        allowed_origins=origins,
        gemini_api_key=_env("GEMINI_API_KEY"),
        gemini_model=_env("GEMINI_MODEL", "gemini-2.5-flash") or "gemini-2.5-flash",
        cors_allow_vercel_preview=cors_allow_vercel_preview,
    )


def clear_settings_cache() -> None:
    get_settings.cache_clear()
