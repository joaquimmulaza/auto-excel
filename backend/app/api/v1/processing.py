"""Validate, summary, items, issues, process, receipt."""
from __future__ import annotations

import uuid

from fastapi import APIRouter, HTTPException, Query, status

from backend.app.api.deps import DbDep, UserDep, require_role
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.schemas.processing import (
    JobItemResponse,
    JobSummaryResponse,
    ValidationIssueResponse,
)
from backend.app.services.job_pipeline import build_receipt, process_job, validate_job
from fastapi import Depends

router = APIRouter(prefix="/jobs", tags=["processing"])


def _get_job_or_404(job_id: uuid.UUID, repo: JobRepository):
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


def _check_access(job, current_user):
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


@router.post("/{job_id}/validate")
def trigger_validate(
    job_id: uuid.UUID,
    current_user: UserDep,
    db: DbDep,
    dry_run: bool | None = Query(default=None),
):
    """Run domain engine against uploaded files and persist preview results."""
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)

    if job.status not in ("UPLOADED", "NEEDS_CORRECTION"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "error": {
                    "code": "INVALID_STATE",
                    "message": f"Cannot validate job in status {job.status}",
                    "request_id": "",
                }
            },
        )
    try:
        result = validate_job(db, job, actor_id=current_user.id, dry_run=dry_run)
    except ValueError as exc:
        code = str(exc)
        status_code = status.HTTP_422_UNPROCESSABLE_ENTITY
        if code == "MISSING_INPUT_FILE":
            status_code = status.HTTP_409_CONFLICT
        raise HTTPException(
            status_code=status_code,
            detail={"error": {"code": code, "message": code, "request_id": ""}},
        ) from exc
    return result


@router.get("/{job_id}/summary", response_model=JobSummaryResponse)
def get_summary(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    issues = repo.list_issues(job_id)
    severity_counts: dict[str, int] = {}
    for issue in issues:
        severity_counts[issue.severity] = severity_counts.get(issue.severity, 0) + 1
    return JobSummaryResponse(
        job_id=job.id,
        status=job.status,
        summary=job.summary,
        issues_by_severity=severity_counts,
    )


@router.get("/{job_id}/items", response_model=list[JobItemResponse])
def get_items(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    items = repo.list_items(job_id)
    return [JobItemResponse.model_validate(i) for i in items]


@router.get("/{job_id}/issues", response_model=list[ValidationIssueResponse])
def get_issues(
    job_id: uuid.UUID,
    current_user: UserDep,
    db: DbDep,
    severity: str | None = None,
):
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    issues = repo.list_issues(job_id, severity=severity)
    return [ValidationIssueResponse.model_validate(i) for i in issues]


@router.post(
    "/{job_id}/process",
    dependencies=[Depends(require_role("OPERADOR", "ADMIN"))],
)
def trigger_process(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    try:
        return process_job(db, job, actor_id=current_user.id)
    except ValueError as exc:
        code = str(exc)
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": code, "message": code, "request_id": ""}},
        ) from exc


@router.get("/{job_id}/receipt")
def get_receipt(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    return build_receipt(job, db)
