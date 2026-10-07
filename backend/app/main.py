"""FastAPI application entry point for Cotarco Commercial Manager.

GUARDRAIL: This is backend/app/main.py - NOT the legacy main.py at the repo root.
The legacy main.py MUST remain untouched.
"""
from __future__ import annotations

import json
import logging
import typing
import uuid
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.exceptions import HTTPException, RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from backend.app.api.errors import http_exception_handler, validation_exception_handler
from backend.app.api.v1.router import v1_router
from backend.app.core.settings import get_settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)


class UTF8JSONResponse(JSONResponse):
    media_type = "application/json; charset=utf-8"

    def render(self, content: typing.Any) -> bytes:
        return json.dumps(
            content,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class RequestIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request_id = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-Id"] = request_id
        return response


@asynccontextmanager
async def lifespan(application: FastAPI):
    from backend.app.api.deps import _get_session_factory
    from backend.app.core.settings import validate_runtime_settings
    from backend.app.services.bootstrap import bootstrap_database

    runtime_settings = get_settings()
    validate_runtime_settings(runtime_settings)

    factory = _get_session_factory()
    db = factory()
    try:
        bootstrap_database(db)
        logger.info("Database initialised — bootstrap complete.")
    finally:
        db.close()
    yield


settings = get_settings()

app = FastAPI(
    title="Cotarco Commercial Manager API",
    description="Internal API for managing commercial price/stock tables.",
    version="1.0.0",
    docs_url="/docs" if not settings.is_production else "/docs",
    redoc_url="/redoc",
    default_response_class=UTF8JSONResponse,
    lifespan=lifespan,
)

app.add_middleware(RequestIdMiddleware)

_cors_kwargs: dict = {
    "allow_origins": list(settings.allowed_origins) or ["http://localhost:3000"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
if settings.cors_allow_vercel_preview:
    _cors_kwargs["allow_origin_regex"] = r"https://.*\.vercel\.app"

app.add_middleware(CORSMiddleware, **_cors_kwargs)

app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

app.include_router(v1_router)


@app.get("/health", tags=["health"])
def health_check():
    return {
        "status": "ok",
        "service": "cotarco-commercial-manager",
        "environment": settings.environment,
        "auth_mode": settings.auth_mode,
        "storage_backend": settings.storage_backend,
    }
