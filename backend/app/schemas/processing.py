"""Pydantic v2 schemas for job items, issues, and summaries."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class JobItemResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    reference_original: str
    reference_normalized: str
    old_price: float | None = None
    new_price: float | None = None
    old_stock: int | None = None
    new_stock: int | None = None
    price_variation_pct: float | None = None
    decision: str
    decision_code: str
    details: dict[str, Any] | None = None
    created_at: datetime


class ValidationIssueResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    job_id: uuid.UUID
    severity: str
    code: str
    message: str
    field: str | None = None
    row_number: int | None = None
    details: dict[str, Any] | None = None
    resolved: bool
    created_at: datetime


class JobSummaryResponse(BaseModel):
    job_id: uuid.UUID
    status: str
    summary: dict[str, Any] | None = None
    issues_by_severity: dict[str, int] = {}
