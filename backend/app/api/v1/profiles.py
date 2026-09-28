"""GET /profiles, GET /profiles/{id}"""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, status
from backend.app.api.deps import DbDep, UserDep
from backend.app.infra.repositories.profiles import ProfileRepository
from backend.app.schemas.profile import ProfileListResponse, ProfileResponse

router = APIRouter(prefix="/profiles", tags=["profiles"])


@router.get("", response_model=ProfileListResponse)
def list_profiles(current_user: UserDep, db: DbDep):
    """List all active commercial profiles. Any authenticated user."""
    repo = ProfileRepository(db)
    profiles = repo.list_active()
    items = [ProfileResponse.model_validate(p) for p in profiles]
    return ProfileListResponse(items=items, total=len(items))


@router.get("/{profile_id}", response_model=ProfileResponse)
def get_profile(profile_id: uuid.UUID, current_user: UserDep, db: DbDep):
    """Get a single profile by UUID. Any authenticated user."""
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
