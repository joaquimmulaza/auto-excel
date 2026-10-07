"""POST /jobs, GET /jobs, GET /jobs/{id}"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException, status
from sqlalchemy import func

from backend.app.api.deps import DbDep, UserDep
from backend.app.infra.db.models import AuditLogOrm, ProcessingJobOrm
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.infra.repositories.profiles import ProfileRepository
from backend.app.schemas.job import JobCreateRequest, JobListResponse, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


def _next_job_number(db) -> int:
    current = db.query(func.max(ProcessingJobOrm.job_number)).scalar()
    return int(current or 0) + 1


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreateRequest, current_user: UserDep, db: DbDep):
    profile_repo = ProfileRepository(db)
    profile = profile_repo.get_by_id(payload.profile_id)
    if not profile or not profile.active:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "PROFILE_NOT_FOUND",
                    "message": "Active profile not found",
                    "request_id": "",
                }
            },
        )

    now = datetime.now(timezone.utc)
    options = dict(payload.options or {})
    job = ProcessingJobOrm(
        id=uuid.uuid4(),
        job_number=_next_job_number(db),
        profile_id=payload.profile_id,
        created_by_id=current_user.id,
        status="UPLOADED",
        source_system=payload.source_system,
        description=payload.description,
        options=options,
        created_at=now,
        updated_at=now,
    )
    job_repo = JobRepository(db)
    created = job_repo.create(job)
    job_repo.append_audit_log(
        AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=current_user.id,
            action="JOB_CREATED",
            entity_type="processing_job",
            entity_id=created.id,
            job_id=created.id,
            extra_metadata={
                "profile_id": str(payload.profile_id),
                "dry_run": bool(options.get("dry_run")),
            },
            created_at=now,
        )
    )
    return JobResponse.model_validate(created)


@router.get("", response_model=JobListResponse)
def list_jobs(
    current_user: UserDep,
    db: DbDep,
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    repo = JobRepository(db)
    if current_user.role in ("OPERADOR", "ADMIN"):
        jobs = repo.list_all(status=status_filter, limit=limit, offset=offset)
    else:
        jobs = repo.list_by_user(current_user.id, limit=limit, offset=offset)
    items = [JobResponse.model_validate(j) for j in jobs]
    return JobListResponse(items=items, total=len(items))


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = JobRepository(db)
    job = repo.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": "Job not found",
                    "request_id": "",
                }
            },
        )
    if current_user.role == "COMERCIAL" and job.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Cannot access this job",
                    "request_id": "",
                }
            },
        )
    return JobResponse.model_validate(job)
