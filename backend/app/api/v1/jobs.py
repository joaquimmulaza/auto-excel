"""POST /jobs, GET /jobs, GET /jobs/{id}"""
from __future__ import annotations
import uuid
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, status
from backend.app.api.deps import DbDep, UserDep
from backend.app.infra.db.models import ProcessingJobOrm, AuditLogOrm
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.infra.repositories.profiles import ProfileRepository
from backend.app.schemas.job import JobCreateRequest, JobListResponse, JobResponse

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("", response_model=JobResponse, status_code=status.HTTP_201_CREATED)
def create_job(payload: JobCreateRequest, current_user: UserDep, db: DbDep):
    """Create a new processing job. COMERCIAL+ role."""
    # Validate profile exists and is active
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
    job = ProcessingJobOrm(
        id=uuid.uuid4(),
        profile_id=payload.profile_id,
        created_by_id=current_user.id,
        status="UPLOADED",
        source_system=payload.source_system,
        description=payload.description,
        options=payload.options,
        created_at=now,
        updated_at=now,
    )
    job_repo = JobRepository(db)
    created = job_repo.create(job)

    # Audit log
    audit = AuditLogOrm(
        id=uuid.uuid4(),
        actor_id=current_user.id,
        action="JOB_CREATED",
        entity_type="processing_job",
        entity_id=created.id,
        job_id=created.id,
        extra_metadata={"profile_id": str(payload.profile_id)},
        created_at=now,
    )
    job_repo.append_audit_log(audit)

    return JobResponse.model_validate(created)


@router.get("", response_model=JobListResponse)
def list_jobs(
    current_user: UserDep,
    db: DbDep,
    status_filter: str | None = None,
    limit: int = 50,
    offset: int = 0,
):
    """List jobs. OPERADOR/ADMIN see all; COMERCIAL sees only their own."""
    repo = JobRepository(db)
    if current_user.role in ("OPERADOR", "ADMIN"):
        jobs = repo.list_all(status=status_filter, limit=limit, offset=offset)
    else:
        jobs = repo.list_by_user(current_user.id, limit=limit, offset=offset)
    items = [JobResponse.model_validate(j) for j in jobs]
    return JobListResponse(items=items, total=len(items))


@router.get("/{job_id}", response_model=JobResponse)
def get_job(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    """Get a single job. COMERCIAL can only access their own."""
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
    # RBAC: COMERCIAL can only see their own jobs
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
