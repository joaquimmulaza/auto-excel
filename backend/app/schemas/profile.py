"""Pydantic v2 schemas for CommercialProfile API responses."""
from __future__ import annotations
import uuid
from datetime import datetime
from typing import Any
from pydantic import BaseModel, ConfigDict


class ProfileResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    code: str
    name: str
    type: str
    description: str | None = None
    active: bool
    config: dict[str, Any] = {}
    rules_version: int
    created_at: datetime
    updated_at: datetime


class ProfileListResponse(BaseModel):
    items: list[ProfileResponse]
    total: int
