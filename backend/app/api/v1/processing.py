"""POST /jobs/{id}/validate, GET /jobs/{id}/summary, GET /jobs/{id}/items, GET /jobs/{id}/issues"""
from __future__ import annotations
import uuid
from fastapi import APIRouter, HTTPException, status
from backend.app.api.deps import DbDep, UserDep
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.schemas.processing import (
    JobItemResponse,
    JobSummaryResponse,
    ValidationIssueResponse,
)

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


@router.post("/{job_id}/validate", status_code=status.HTTP_202_ACCEPTED)
def trigger_validate(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    """Trigger validation of an uploaded job. Changes status to VALIDATING."""
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
    repo.update_status(job_id, "VALIDATING")
    return {"job_id": str(job_id), "status": "VALIDATING", "message": "Validation queued"}


@router.get("/{job_id}/summary", response_model=JobSummaryResponse)
def get_summary(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    """Get processing summary for a job."""
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)

    # Count issues by severity
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
    """Get all item-level results for a job (diff/preview)."""
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
    """Get validation issues for a job, optionally filtered by severity."""
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    issues = repo.list_issues(job_id, severity=severity)
    return [ValidationIssueResponse.model_validate(i) for i in issues]
