"""Local login / me endpoints."""
from __future__ import annotations

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, EmailStr, Field

from backend.app.api.deps import DbDep, UserDep
from backend.app.infra.db.models import UserOrm
from backend.app.services.auth_tokens import (
    create_access_token,
    hash_password,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


class LoginRequest(BaseModel):
    email: EmailStr
    password: str = Field(min_length=4)


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: dict


class MeResponse(BaseModel):
    id: str
    email: str
    name: str | None
    role: str


@router.post("/login", response_model=LoginResponse)
def login(payload: LoginRequest, db: DbDep):
    user = db.query(UserOrm).filter(UserOrm.email == payload.email.lower()).first()
    if not user or not user.is_active or not verify_password(payload.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error": {
                    "code": "INVALID_CREDENTIALS",
                    "message": "Email or password incorrect",
                    "request_id": "",
                }
            },
        )
    token = create_access_token(user_id=user.id, email=user.email, role=user.role)
    return LoginResponse(
        access_token=token,
        user={
            "id": str(user.id),
            "email": user.email,
            "name": user.display_name,
            "role": user.role,
        },
    )


@router.get("/me", response_model=MeResponse)
def me(current_user: UserDep, db: DbDep):
    user = db.get(UserOrm, current_user.id)
    return MeResponse(
        id=str(current_user.id),
        email=current_user.email,
        name=user.display_name if user else None,
        role=current_user.role,
    )


def ensure_demo_users(db) -> None:
    """Seed default users with passwords if missing (local/dev)."""
    import uuid
    from datetime import datetime, timezone

    seeds = [
        (
            uuid.UUID("00000000-0000-0000-0000-000000000001"),
            "joaquim.silva@cotarco.ao",
            "Joaquim Silva",
            "COMERCIAL",
            "comercial123",
        ),
        (
            uuid.UUID("00000000-0000-0000-0000-000000000002"),
            "antonio.ferreira@cotarco.ao",
            "António Ferreira",
            "OPERADOR",
            "operador123",
        ),
        (
            uuid.UUID("00000000-0000-0000-0000-000000000003"),
            "admin@cotarco.ao",
            "Administrador Geral",
            "ADMIN",
            "admin123",
        ),
    ]
    now = datetime.now(timezone.utc)
    for uid, email, name, role, password in seeds:
        existing = db.get(UserOrm, uid)
        if existing:
            if not existing.password_hash:
                existing.password_hash = hash_password(password)
            continue
        db.merge(
            UserOrm(
                id=uid,
                email=email,
                display_name=name,
                role=role,
                password_hash=hash_password(password),
                is_active=True,
                created_at=now,
                updated_at=now,
            )
        )
    db.flush()
