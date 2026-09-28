"""FastAPI application entry point for Cotarco Commercial Manager.

GUARDRAIL: This is backend/app/main.py — NOT the legacy main.py at the repo root.
The legacy main.py MUST remain untouched.
"""
from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import HTTPException, RequestValidationError
from backend.app.api.v1.router import v1_router
from backend.app.api.errors import http_exception_handler, validation_exception_handler

app = FastAPI(
    title="Cotarco Commercial Manager API",
    description="Internal API for managing commercial price/stock tables.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS — tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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
