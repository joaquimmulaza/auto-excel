"""Upload and download job files."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from fastapi.responses import Response

from backend.app.api.deps import DbDep, UserDep
from backend.app.infra.db.models import AuditLogOrm, JobFileOrm
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.services.storage import read_bytes, store_bytes

router = APIRouter(prefix="/jobs", tags=["files"])

ALLOWED_KINDS = {"INPUT", "CATALOG"}
MAX_BYTES = 25 * 1024 * 1024


def _get_job_or_404(job_id: uuid.UUID, repo: JobRepository):
    job = repo.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "JOB_NOT_FOUND", "message": "Job not found", "request_id": ""}},
        )
    return job


def _check_access(job, current_user):
    if current_user.role == "COMERCIAL" and job.created_by_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": {"code": "FORBIDDEN", "message": "Cannot access this job", "request_id": ""}},
        )


@router.post("/{job_id}/files", status_code=status.HTTP_201_CREATED)
async def upload_file(
    job_id: uuid.UUID,
    current_user: UserDep,
    db: DbDep,
    kind: str = "INPUT",
    file: UploadFile = File(...),
):
    kind = kind.upper()
    if kind not in ALLOWED_KINDS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "INVALID_KIND", "message": f"kind must be one of {sorted(ALLOWED_KINDS)}", "request_id": ""}},
        )
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    if job.status not in ("UPLOADED", "NEEDS_CORRECTION"):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": {"code": "INVALID_STATE", "message": f"Cannot upload in status {job.status}", "request_id": ""}},
        )

    filename = file.filename or "upload.xlsx"
    if not filename.lower().endswith((".xlsx", ".xls")):
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "INVALID_EXTENSION", "message": "Only .xlsx/.xls allowed", "request_id": ""}},
        )
    content = await file.read()
    if len(content) > MAX_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail={"error": {"code": "FILE_TOO_LARGE", "message": "Max 25MB", "request_id": ""}},
        )
    if not content:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail={"error": {"code": "EMPTY_FILE", "message": "File is empty", "request_id": ""}},
        )

    meta = store_bytes(job_id=job_id, kind=kind, original_name=filename, content=content)
    now = datetime.now(timezone.utc)
    # Replace previous file of same kind
    db.query(JobFileOrm).filter(JobFileOrm.job_id == job_id, JobFileOrm.kind == kind).delete()
    row = JobFileOrm(
        id=uuid.uuid4(),
        job_id=job_id,
        kind=kind,
        original_name=meta["original_name"],
        storage_path=meta["storage_path"],
        sha256=meta["sha256"],
        size_bytes=meta["size_bytes"],
        mime_type=meta["mime_type"],
        version=1,
        uploaded_by_id=current_user.id,
        created_at=now,
    )
    db.add(row)
    if kind == "INPUT":
        job.source_name = meta["original_name"]
    repo.append_audit_log(
        AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=current_user.id,
            action="FILE_UPLOADED",
            entity_type="job_file",
            entity_id=row.id,
            job_id=job_id,
            extra_metadata={"kind": kind, "sha256": meta["sha256"]},
            created_at=now,
        )
    )
    db.flush()
    return {
        "id": str(row.id),
        "job_id": str(job_id),
        "kind": kind,
        "original_name": row.original_name,
        "sha256": row.sha256,
        "size_bytes": row.size_bytes,
    }


@router.get("/{job_id}/files")
def list_files(job_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    rows = (
        db.query(JobFileOrm)
        .filter(JobFileOrm.job_id == job_id)
        .order_by(JobFileOrm.created_at.asc())
        .all()
    )
    return {
        "items": [
            {
                "id": str(f.id),
                "kind": f.kind,
                "original_name": f.original_name,
                "sha256": f.sha256,
                "size_bytes": f.size_bytes,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in rows
        ]
    }


@router.get("/{job_id}/files/{file_id}/download")
def download_file(job_id: uuid.UUID, file_id: uuid.UUID, current_user: UserDep, db: DbDep):
    repo = JobRepository(db)
    job = _get_job_or_404(job_id, repo)
    _check_access(job, current_user)
    row = db.get(JobFileOrm, file_id)
    if not row or row.job_id != job_id:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_NOT_FOUND", "message": "File not found", "request_id": ""}},
        )
    try:
        content = read_bytes(row.storage_path)
    except FileNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": {"code": "FILE_MISSING_ON_DISK", "message": "File missing on storage", "request_id": ""}},
        )
    return Response(
        content=content,
        media_type=row.mime_type or "application/octet-stream",
        headers={"Content-Disposition": f'attachment; filename="{row.original_name}"'},
    )
