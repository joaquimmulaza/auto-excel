"""Standardized HTTP error handlers."""
from __future__ import annotations
import uuid
from fastapi import Request
from fastapi.responses import JSONResponse


def make_error_body(code: str, message: str, request_id: str | None = None) -> dict:
    return {
        "error": {
            "code": code,
            "message": message,
            "request_id": request_id or str(uuid.uuid4()),
        }
    }


async def http_exception_handler(request: Request, exc) -> JSONResponse:
    from fastapi.exceptions import HTTPException

    detail = exc.detail
    if isinstance(detail, dict) and "error" in detail:
        body = detail
    else:
        body = make_error_body("HTTP_ERROR", str(detail))
    return JSONResponse(status_code=exc.status_code, content=body)


async def validation_exception_handler(request: Request, exc) -> JSONResponse:
    errors = exc.errors()
    message = "; ".join(f"{e['loc']}: {e['msg']}" for e in errors)
    return JSONResponse(
        status_code=422,
        content=make_error_body("VALIDATION_ERROR", message),
    )
