"""Aggregator for all v1 routes."""
from fastapi import APIRouter

from backend.app.api.v1 import (
    ai,
    approvals,
    auth,
    files,
    history,
    jobs,
    processing,
    profiles,
)

v1_router = APIRouter(prefix="/api/v1")
v1_router.include_router(auth.router)
v1_router.include_router(profiles.router)
v1_router.include_router(jobs.router)
v1_router.include_router(files.router)
v1_router.include_router(processing.router)
v1_router.include_router(approvals.router)
v1_router.include_router(ai.router)
v1_router.include_router(history.router)
