"""FastAPI application entry point for Cotarco Commercial Manager.

GUARDRAIL: This is backend/app/main.py - NOT the legacy main.py at the repo root.
The legacy main.py MUST remain untouched.
"""
from __future__ import annotations
import json
import logging
import os
import typing
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from backend.app.api.v1.router import v1_router
from backend.app.api.errors import http_exception_handler, validation_exception_handler

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


@asynccontextmanager
async def lifespan(application: FastAPI):
    """Eagerly initialise the database on every startup / hot-reload.

    The session factory in deps.py uses a module-level singleton that is
    created lazily on the first request.  When uvicorn --reload restarts the
    worker the old singleton may point to a stale in-memory engine whose
    tables were never (re)created, causing 'no such table' OperationalErrors
    (HTTP 500).  Calling _get_session_factory() here forces table creation
    before the first request arrives.
    """
    from backend.app.api.deps import _get_session_factory  # local import avoids circular
    from backend.app.services.bootstrap import bootstrap_database

    factory = _get_session_factory()
    db = factory()
    try:
        bootstrap_database(db)
        logger.info("Database initialised — tables and seeds ready.")
    finally:
        db.close()
    yield


app = FastAPI(
    title="Cotarco Commercial Manager API",
    description="Internal API for managing commercial price/stock tables.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    default_response_class=UTF8JSONResponse,
    lifespan=lifespan,
)


_cors_origins = [
    o.strip()
    for o in os.getenv(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000",
    ).split(",")
    if o.strip()
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins or ["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Error handlers
app.add_exception_handler(HTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

# Routes
app.include_router(v1_router)

@app.get("/health", tags=["health"])
def health_check():
    return {"status": "ok", "service": "cotarco-commercial-manager"}
