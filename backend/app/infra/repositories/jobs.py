"""Repository for ProcessingJob data access.

Provides typed, testable query methods for ``processing_jobs``,
``job_items``, ``validation_issues``, ``approvals``, and ``price_history``.

GUARDRAIL: No business logic here. Status transitions, price guards, and
           approval flows live in the domain / service layer.
"""

from __future__ import annotations

import uuid
from typing import Optional

from sqlalchemy.orm import Session

from backend.app.infra.db.models import (
    AuditLogOrm,
    ApprovalOrm,
    JobItemOrm,
    PriceHistoryOrm,
    ProcessingJobOrm,
    ValidationIssueOrm,
)


class JobRepository:
    """Data access layer for processing jobs and related child entities."""

    def __init__(self, session: Session) -> None:
        self._session = session

    # ------------------------------------------------------------------
    # processing_jobs
    # ------------------------------------------------------------------

    def get_by_id(self, job_id: uuid.UUID) -> Optional[ProcessingJobOrm]:
        """Fetch a job by UUID."""
        return self._session.get(ProcessingJobOrm, job_id)

    def list_by_user(
        self,
        user_id: uuid.UUID,
        *,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProcessingJobOrm]:
        """Return jobs created by a specific user (Comercial view)."""
        return (
            self._session.query(ProcessingJobOrm)
            .filter(ProcessingJobOrm.created_by_id == user_id)
            .order_by(ProcessingJobOrm.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def list_all(
        self,
        *,
        status: str | None = None,
        profile_id: uuid.UUID | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> list[ProcessingJobOrm]:
        """Return all jobs — Operador / Admin view.

        Optional filters: status, profile_id.
        """
        q = self._session.query(ProcessingJobOrm)
        if status:
            q = q.filter(ProcessingJobOrm.status == status)
        if profile_id:
            q = q.filter(ProcessingJobOrm.profile_id == profile_id)
        return (
            q.order_by(ProcessingJobOrm.created_at.desc())
            .limit(limit)
            .offset(offset)
            .all()
        )

    def create(self, job: ProcessingJobOrm) -> ProcessingJobOrm:
        """Persist a new job and return the attached instance."""
        self._session.add(job)
        self._session.flush()
        return job

    def update_status(self, job_id: uuid.UUID, status: str) -> bool:
        """Update job status only. Returns True if job was found."""
        job = self.get_by_id(job_id)
        if not job:
            return False
        job.status = status
        self._session.flush()
        return True

    # ------------------------------------------------------------------
    # job_items
    # ------------------------------------------------------------------

    def bulk_insert_items(self, items: list[JobItemOrm]) -> None:
        """Bulk-insert job item rows without individual flushes."""
        self._session.bulk_save_objects(items)

    def list_items(self, job_id: uuid.UUID) -> list[JobItemOrm]:
        """Return all items for a job ordered by normalized reference."""
        return (
            self._session.query(JobItemOrm)
            .filter(JobItemOrm.job_id == job_id)
            .order_by(JobItemOrm.reference_normalized)
            .all()
        )

    # ------------------------------------------------------------------
    # validation_issues
    # ------------------------------------------------------------------

    def bulk_insert_issues(self, issues: list[ValidationIssueOrm]) -> None:
        """Bulk-insert validation issue rows."""
        self._session.bulk_save_objects(issues)

    def list_issues(
        self,
        job_id: uuid.UUID,
        *,
        severity: str | None = None,
    ) -> list[ValidationIssueOrm]:
        """Return validation issues for a job, optionally filtered by severity."""
        q = self._session.query(ValidationIssueOrm).filter(
            ValidationIssueOrm.job_id == job_id
        )
        if severity:
            q = q.filter(ValidationIssueOrm.severity == severity)
        return q.order_by(ValidationIssueOrm.severity, ValidationIssueOrm.row_number).all()

    # ------------------------------------------------------------------
    # approvals
    # ------------------------------------------------------------------

    def add_approval(self, approval: ApprovalOrm) -> ApprovalOrm:
        """Record an approval/rejection action — append only."""
        self._session.add(approval)
        self._session.flush()
        return approval

    def list_approvals(self, job_id: uuid.UUID) -> list[ApprovalOrm]:
        """Return all approval records for a job in chronological order."""
        return (
            self._session.query(ApprovalOrm)
            .filter(ApprovalOrm.job_id == job_id)
            .order_by(ApprovalOrm.created_at)
            .all()
        )

    # ------------------------------------------------------------------
    # price_history
    # ------------------------------------------------------------------

    def record_price_history(self, entry: PriceHistoryOrm) -> PriceHistoryOrm:
        """Append a price history record — never update existing rows."""
        self._session.add(entry)
        self._session.flush()
        return entry

    def list_price_history(
        self,
        reference_normalized: str,
        *,
        limit: int = 100,
    ) -> list[PriceHistoryOrm]:
        """Return price history for a reference, newest first."""
        return (
            self._session.query(PriceHistoryOrm)
            .filter(PriceHistoryOrm.reference_normalized == reference_normalized)
            .order_by(PriceHistoryOrm.recorded_at.desc())
            .limit(limit)
            .all()
        )

    # ------------------------------------------------------------------
    # audit_logs (append-only — SECURITY CRITICAL)
    # ------------------------------------------------------------------

    def append_audit_log(self, log: AuditLogOrm) -> AuditLogOrm:
        """Insert an audit log entry — NEVER update or delete.

        Application code must only ever INSERT to audit_logs.
        The RLS policy in 002_rls_policies.sql enforces this at DB level too.
        """
        self._session.add(log)
        self._session.flush()
        return log
