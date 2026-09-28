"""Pydantic v2 schemas for ProcessingJob API."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict, Field


# ---- Request schemas ----


class JobCreateRequest(BaseModel):
    profile_id: uuid.UUID
    source_system: str | None = None
    description: str | None = None
    options: dict[str, Any] = Field(default_factory=dict)


class ApprovalRequest(BaseModel):
    comment: str | None = None


# ---- Response schemas ----


class JobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_number: int | None = None
    profile_id: uuid.UUID
    created_by_id: uuid.UUID
    approved_by_id: uuid.UUID | None = None
    status: str
    source_system: str | None = None
    description: str | None = None
    options: dict[str, Any] = {}
    summary: dict[str, Any] | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime


class JobListResponse(BaseModel):
    items: list[JobResponse]
    total: int


class ApprovalResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    action: str
    actor_id: uuid.UUID
    comment: str | None = None
    created_at: datetime
