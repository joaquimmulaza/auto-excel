"""Temporary debug log ingest for browser-side instrumentation."""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from backend.app.debug_agent_log import agent_log

router = APIRouter(prefix="/__debug", tags=["debug"])


class AgentLogIn(BaseModel):
    hypothesisId: str = Field(default="FE")
    location: str
    message: str
    data: dict[str, Any] = Field(default_factory=dict)
    timestamp: int | None = None


@router.post("/agent-log")
def ingest_agent_log(payload: AgentLogIn):
    agent_log(
        hypothesis_id=payload.hypothesisId,
        location=payload.location,
        message=payload.message,
        data={**payload.data, "client_ts": payload.timestamp},
    )
    return {"ok": True}
