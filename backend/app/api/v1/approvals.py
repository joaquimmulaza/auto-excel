"""Approve / reject job — OPERADOR/ADMIN only."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status

from backend.app.api.deps import DbDep, UserDep, require_role
from backend.app.infra.db.models import ApprovalOrm, AuditLogOrm
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.schemas.job import ApprovalRequest, ApprovalResponse

router = APIRouter(prefix="/jobs", tags=["approvals"])


def _get_job(repo: JobRepository, job_id: uuid.UUID):
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
    return job


@router.post(
    "/{job_id}/approve",
    response_model=ApprovalResponse,
    dependencies=[Depends(require_role("OPERADOR", "ADMIN"))],
)
def approve_job(
    job_id: uuid.UUID,
    payload: ApprovalRequest,
    current_user: UserDep,
    db: DbDep,
):
    repo = JobRepository(db)
    job = _get_job(repo, job_id)

    if job.status != "READY_FOR_REVIEW":
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_STATE",
                    "message": f"Cannot approve job in status {job.status}",
                    "request_id": "",
                }
            },
        )
    if (job.options or {}).get("dry_run"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "DRY_RUN_CANNOT_APPROVE",
                    "message": "Dry-run jobs cannot be approved for processing",
                    "request_id": "",
                }
            },
        )

    now = datetime.now(timezone.utc)
    approval = ApprovalOrm(
        id=uuid.uuid4(),
        job_id=job_id,
        action="APPROVED",
        actor_id=current_user.id,
        comment=payload.comment,
        created_at=now,
    )
    result = repo.add_approval(approval)
    repo.update_status(job_id, "APPROVED")
    job.approved_by_id = current_user.id
    repo.append_audit_log(
        AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=current_user.id,
            action="JOB_APPROVED",
            entity_type="processing_job",
            entity_id=job_id,
            job_id=job_id,
            extra_metadata={"comment": payload.comment},
            created_at=now,
        )
    )
    return ApprovalResponse.model_validate(result)


@router.post(
    "/{job_id}/reject",
    response_model=ApprovalResponse,
    dependencies=[Depends(require_role("OPERADOR", "ADMIN"))],
)
def reject_job(
    job_id: uuid.UUID,
    payload: ApprovalRequest,
    current_user: UserDep,
    db: DbDep,
):
    repo = JobRepository(db)
    job = _get_job(repo, job_id)
    if job.status not in ("READY_FOR_REVIEW", "NEEDS_CORRECTION"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_STATE",
                    "message": f"Cannot reject job in status {job.status}",
                    "request_id": "",
                }
            },
        )
    now = datetime.now(timezone.utc)
    approval = ApprovalOrm(
        id=uuid.uuid4(),
        job_id=job_id,
        action="REJECTED",
        actor_id=current_user.id,
        comment=payload.comment,
        created_at=now,
    )
    result = repo.add_approval(approval)
    repo.update_status(job_id, "CANCELLED")
    repo.append_audit_log(
        AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=current_user.id,
            action="JOB_REJECTED",
            entity_type="processing_job",
            entity_id=job_id,
            job_id=job_id,
            extra_metadata={"comment": payload.comment},
            created_at=now,
        )
    )
    return ApprovalResponse.model_validate(result)
