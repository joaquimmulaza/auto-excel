"""Profiles CRUD — create/update ADMIN only."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import DbDep, UserDep, require_role
from backend.app.infra.db.models import CommercialProfileOrm
from backend.app.infra.repositories.profiles import ProfileRepository
from backend.app.schemas.profile import (
    ProfileCreateRequest,
    ProfileListResponse,
    ProfileResponse,
    ProfileUpdateRequest,
)

router = APIRouter(prefix="/profiles", tags=["profiles"])

ALLOWED_TYPES = {"STORE", "MARKETPLACE", "PARTNER", "RESELLER", "OTHER", "ECOMMERCE"}


@router.get("", response_model=ProfileListResponse)
def list_profiles(current_user: UserDep, db: DbDep):
    repo = ProfileRepository(db)
    profiles = repo.list_active()
    items = [ProfileResponse.model_validate(p) for p in profiles]
    return ProfileListResponse(items=items, total=len(items))


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = ProfileRepository(db)
    profile = repo.get_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Profile not found",
                    "request_id": "",
                }
            },
        )
    return ProfileResponse.model_validate(profile)


@router.post(
    "",
    response_model=ProfileResponse,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_role("ADMIN"))],
)
def create_profile(payload: ProfileCreateRequest, current_user: UserDep, db: DbDep):
    if payload.type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_TYPE",
                    "message": f"type must be one of {sorted(ALLOWED_TYPES)}",
                    "request_id": "",
                }
            },
        )
    existing = (
        db.query(CommercialProfileOrm)
        .filter(CommercialProfileOrm.code == payload.code.upper())
        .first()
    )
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "PROFILE_EXISTS",
                    "message": "Profile code already exists",
                    "request_id": "",
                }
            },
        )
    now = datetime.now(timezone.utc)
    config = dict(payload.config or {})
    # Normalize config keys for domain adapter
    if "price_guard_threshold_pct" in config and "price_variation_threshold" not in config:
        config["price_variation_threshold"] = float(config["price_guard_threshold_pct"]) / 100.0
    if "new_product_min_stock" in config and "stock_min_activation" not in config:
        config["stock_min_activation"] = config["new_product_min_stock"]
    profile = CommercialProfileOrm(
        id=uuid.uuid4(),
        code=payload.code.upper(),
        name=payload.name,
        type=payload.type,
        description=payload.description,
        active=payload.active,
        config=config,
        rules_version=1,
        created_at=now,
        updated_at=now,
    )
    db.add(profile)
    db.flush()
    return ProfileResponse.model_validate(profile)


@router.patch(
    "/{profile_id}",
    response_model=ProfileResponse,
    dependencies=[Depends(require_role("ADMIN"))],
)
def update_profile(
    profile_id: uuid.UUID,
    payload: ProfileUpdateRequest,
    current_user: UserDep,
    db: DbDep,
):
    repo = ProfileRepository(db)
    profile = repo.get_by_id(profile_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Profile not found",
                    "request_id": "",
                }
            },
        )
    if payload.type is not None and payload.type not in ALLOWED_TYPES:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={
                "error": {
                    "code": "INVALID_TYPE",
                    "message": f"type must be one of {sorted(ALLOWED_TYPES)}",
                    "request_id": "",
                }
            },
        )
    if payload.name is not None:
        profile.name = payload.name
    if payload.type is not None:
        profile.type = payload.type
    if payload.description is not None:
        profile.description = payload.description
    if payload.active is not None:
        profile.active = payload.active
    if payload.config is not None:
        config = dict(payload.config)
        if "price_guard_threshold_pct" in config and "price_variation_threshold" not in config:
            config["price_variation_threshold"] = float(config["price_guard_threshold_pct"]) / 100.0
        if "new_product_min_stock" in config and "stock_min_activation" not in config:
            config["stock_min_activation"] = config["new_product_min_stock"]
        profile.config = config
    if payload.bump_rules_version:
        profile.rules_version = int(profile.rules_version or 1) + 1
    profile.updated_at = datetime.now(timezone.utc)
    db.flush()
    return ProfileResponse.model_validate(profile)
