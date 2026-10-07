"""Pydantic v2 schemas for CommercialProfile API responses."""
from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


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


class ProfileCreateRequest(BaseModel):
    code: str = Field(min_length=2, max_length=50)
    name: str = Field(min_length=2)
    type: str = Field(description="STORE | MARKETPLACE | PARTNER | RESELLER | OTHER | ECOMMERCE")
    description: str | None = None
    config: dict[str, Any] = Field(default_factory=dict)
    active: bool = True


class ProfileUpdateRequest(BaseModel):
    name: str | None = None
    type: str | None = None
    description: str | None = None
    config: dict[str, Any] | None = None
    active: bool | None = None
    bump_rules_version: bool = False
