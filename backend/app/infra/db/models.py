"""SQLAlchemy 2.0 ORM models for Cotarco Commercial Manager.

Mapped to PostgreSQL / Supabase. All tables follow the data-architecture.md
specification:
  - UUIDs as primary keys (server_default=gen_random_uuid())
  - timestamptz for all timestamps
  - JSONB for flexible config fields (PostgreSQL) / JSON for SQLite (tests)
  - Enum types aligned with domain models

GUARDRAIL: This module has zero import from FastAPI, domain, or Pydantic.
           Pure infrastructure layer.

NOTE on type strategy:
  ``_JsonColumn`` resolves to JSONB on PostgreSQL and JSON on SQLite (tests).
  ``_UuidColumn`` resolves to native UUID on PostgreSQL and String(36) on SQLite.
  Production DDL enforces JSONB and UUID types via migration 001_initial_schema.sql.
  This allows the full test suite to run on SQLite in-memory without a live PG.
"""

from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import (
    BigInteger,
    Boolean,
    ForeignKey,
    Index,
    Integer,
    JSON,
    Numeric,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.dialects.postgresql import UUID as PgUUID
from sqlalchemy.types import TypeDecorator, String as SAString
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


# ---------------------------------------------------------------------------
# Dialect-aware custom types
# ---------------------------------------------------------------------------

class _JsonColumn(TypeDecorator):
    """Maps to JSONB on PostgreSQL, native JSON on everything else (SQLite for tests)."""
    impl = JSON
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())


class _UuidColumn(TypeDecorator):
    """Maps to native UUID on PostgreSQL, String(36) on SQLite (tests)."""
    impl = SAString
    cache_ok = True

    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID(as_uuid=True))
        return dialect.type_descriptor(SAString(36))

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        if dialect.name == "postgresql":
            return value
        return str(value)

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        if isinstance(value, uuid.UUID):
            return value
        try:
            return uuid.UUID(str(value))
        except (ValueError, AttributeError):
            return value


# ---------------------------------------------------------------------------
# Base
# ---------------------------------------------------------------------------

class Base(DeclarativeBase):
    """Shared declarative base for all ORM models."""
    pass


# ---------------------------------------------------------------------------
# users
# ---------------------------------------------------------------------------

class UserOrm(Base):
    """Local representation of an authenticated Supabase user.

    The ``id`` aligns with Supabase Auth UID when Supabase Auth is active.
    """
    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(Text, unique=True, nullable=False)
    display_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    # COMERCIAL | OPERADOR | ADMIN
    role: Mapped[str] = mapped_column(
        String(20), nullable=False, server_default="COMERCIAL"
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # relationships
    jobs_created: Mapped[list[ProcessingJobOrm]] = relationship(
        "ProcessingJobOrm",
        foreign_keys="ProcessingJobOrm.created_by_id",
        back_populates="created_by",
    )
    jobs_approved: Mapped[list[ProcessingJobOrm]] = relationship(
        "ProcessingJobOrm",
        foreign_keys="ProcessingJobOrm.approved_by_id",
        back_populates="approved_by",
    )
    audit_logs: Mapped[list[AuditLogOrm]] = relationship(
        "AuditLogOrm", back_populates="actor"
    )


# ---------------------------------------------------------------------------
# commercial_profiles
# ---------------------------------------------------------------------------

class CommercialProfileOrm(Base):
    """Commercial profile defining channel / destination / rule-set.

    ``code`` is the machine identifier (e.g. 'MANO', 'WOOCOMMERCE', 'BFA').
    ``config`` (JSON/JSONB) carries channel-specific options.
    ``rules_version`` tracks the active rule version for reproducibility.
    """
    __tablename__ = "commercial_profiles"

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    code: Mapped[str] = mapped_column(String(50), unique=True, nullable=False)
    name: Mapped[str] = mapped_column(Text, nullable=False)
    # STORE | MARKETPLACE | PARTNER | RESELLER | OTHER
    type: Mapped[str] = mapped_column(String(30), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    # Flexible channel configuration (integration type, feature flags, etc.)
    config: Mapped[dict[str, Any]] = mapped_column(
        _JsonColumn(), nullable=False, server_default="{}"
    )
    rules_version: Mapped[int] = mapped_column(
        Integer, nullable=False, server_default="1"
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # relationships
    profile_rules: Mapped[list[ProfileRuleOrm]] = relationship(
        "ProfileRuleOrm", back_populates="profile", cascade="all, delete-orphan"
    )
    jobs: Mapped[list[ProcessingJobOrm]] = relationship(
        "ProcessingJobOrm", back_populates="profile"
    )
    price_history: Mapped[list[PriceHistoryOrm]] = relationship(
        "PriceHistoryOrm", back_populates="profile"
    )


# ---------------------------------------------------------------------------
# profile_rules
# ---------------------------------------------------------------------------

class ProfileRuleOrm(Base):
    """Versioned rule configuration attached to a commercial profile.

    Unique per (profile_id, version, rule_code) — allows historical replay.
    ``rule_config`` is JSON/JSONB to accommodate any rule shape without schema churn.
    """
    __tablename__ = "profile_rules"
    __table_args__ = (
        UniqueConstraint(
            "profile_id", "version", "rule_code",
            name="uq_profile_rules_profile_version_code",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("commercial_profiles.id", ondelete="CASCADE"),
        nullable=False,
    )
    version: Mapped[int] = mapped_column(Integer, nullable=False)
    rule_code: Mapped[str] = mapped_column(String(100), nullable=False)
    rule_config: Mapped[dict[str, Any]] = mapped_column(_JsonColumn(), nullable=False)
    active: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="true"
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    created_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # relationships
    profile: Mapped[CommercialProfileOrm] = relationship(
        "CommercialProfileOrm", back_populates="profile_rules"
    )


# ---------------------------------------------------------------------------
# processing_jobs
# ---------------------------------------------------------------------------

class ProcessingJobOrm(Base):
    """Core operational entity — one job per submitted price/stock table.

    ``job_number`` is a sequential bigint for human-friendly UX references
    (e.g. "Job #42") while ``id`` (UUID) is used for all internal links.

    Status lifecycle:
      UPLOADED → VALIDATING → READY_FOR_REVIEW | NEEDS_CORRECTION
      → APPROVED → PROCESSING → COMPLETED | FAILED | CANCELLED
    """
    __tablename__ = "processing_jobs"
    __table_args__ = (
        Index("idx_jobs_profile_status", "profile_id", "status"),
        Index("idx_jobs_created_by", "created_by_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_number: Mapped[Optional[int]] = mapped_column(
        BigInteger, nullable=True, unique=True
    )
    profile_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("commercial_profiles.id", ondelete="RESTRICT"),
        nullable=False,
    )
    created_by_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    approved_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    # job_status enum values (enforced by DB CHECK or enum type in production)
    status: Mapped[str] = mapped_column(
        String(30), nullable=False, server_default="UPLOADED"
    )
    source_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    source_system: Mapped[Optional[str]] = mapped_column(
        String(100), nullable=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    options: Mapped[dict[str, Any]] = mapped_column(
        _JsonColumn(), nullable=False, server_default="{}"
    )
    # Populated after processing — quantitative summary
    summary: Mapped[Optional[dict[str, Any]]] = mapped_column(
        _JsonColumn(), nullable=True
    )
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    started_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    completed_at: Mapped[Optional[datetime]] = mapped_column(nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # relationships
    profile: Mapped[CommercialProfileOrm] = relationship(
        "CommercialProfileOrm", back_populates="jobs"
    )
    created_by: Mapped[UserOrm] = relationship(
        "UserOrm",
        foreign_keys=[created_by_id],
        back_populates="jobs_created",
    )
    approved_by: Mapped[Optional[UserOrm]] = relationship(
        "UserOrm",
        foreign_keys=[approved_by_id],
        back_populates="jobs_approved",
    )
    job_files: Mapped[list[JobFileOrm]] = relationship(
        "JobFileOrm", back_populates="job", cascade="all, delete-orphan"
    )
    job_items: Mapped[list[JobItemOrm]] = relationship(
        "JobItemOrm", back_populates="job", cascade="all, delete-orphan"
    )
    validation_issues: Mapped[list[ValidationIssueOrm]] = relationship(
        "ValidationIssueOrm", back_populates="job", cascade="all, delete-orphan"
    )
    approvals: Mapped[list[ApprovalOrm]] = relationship(
        "ApprovalOrm", back_populates="job", cascade="all, delete-orphan"
    )
    price_history: Mapped[list[PriceHistoryOrm]] = relationship(
        "PriceHistoryOrm", back_populates="job"
    )
    audit_logs: Mapped[list[AuditLogOrm]] = relationship(
        "AuditLogOrm", back_populates="job"
    )


# ---------------------------------------------------------------------------
# job_files
# ---------------------------------------------------------------------------

class JobFileOrm(Base):
    """Versioned file record for inputs, outputs, logs, and reports.

    The actual binary lives in Supabase Storage; only metadata is persisted
    here. ``sha256`` enables duplicate detection and integrity verification.
    The original uploaded file is NEVER overwritten (Guardrail #9).
    """
    __tablename__ = "job_files"
    __table_args__ = (
        Index("idx_job_files_job", "job_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("processing_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    # INPUT | OUTPUT | LOG | REPORT
    kind: Mapped[str] = mapped_column(String(20), nullable=False)
    original_name: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    storage_path: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    sha256: Mapped[str] = mapped_column(String(64), nullable=False)
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger, nullable=True)
    mime_type: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    version: Mapped[int] = mapped_column(Integer, nullable=False, server_default="1")
    uploaded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    # relationships
    job: Mapped[ProcessingJobOrm] = relationship(
        "ProcessingJobOrm", back_populates="job_files"
    )


# ---------------------------------------------------------------------------
# job_items
# ---------------------------------------------------------------------------

class JobItemOrm(Base):
    """Per-reference evaluation result from the domain engine.

    Stores both raw and normalized references, pricing deltas, stock deltas,
    and the final decision code. ``details`` (JSON/JSONB) holds auxiliary metrics.
    """
    __tablename__ = "job_items"
    __table_args__ = (
        Index("idx_job_items_job_ref", "job_id", "reference_normalized"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("processing_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    reference_original: Mapped[str] = mapped_column(Text, nullable=False)
    reference_normalized: Mapped[str] = mapped_column(Text, nullable=False)
    old_price: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    new_price: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    old_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    new_stock: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    price_variation_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    decision_code: Mapped[str] = mapped_column(String(60), nullable=False)
    details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        _JsonColumn(), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now(), onupdate=func.now()
    )

    # relationships
    job: Mapped[ProcessingJobOrm] = relationship(
        "ProcessingJobOrm", back_populates="job_items"
    )
    validation_issues: Mapped[list[ValidationIssueOrm]] = relationship(
        "ValidationIssueOrm", back_populates="job_item"
    )


# ---------------------------------------------------------------------------
# validation_issues
# ---------------------------------------------------------------------------

class ValidationIssueOrm(Base):
    """Structured validation or business rule violation for a job.

    Aligned with domain ``ValidationIssue`` Pydantic model.
    ``resolved`` allows the Comercial to acknowledge/fix items.
    """
    __tablename__ = "validation_issues"
    __table_args__ = (
        Index("idx_validation_job_severity", "job_id", "severity"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("processing_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    job_item_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("job_items.id", ondelete="SET NULL"),
        nullable=True,
    )
    # INFO | WARNING | ERROR | BLOCKER
    severity: Mapped[str] = mapped_column(String(20), nullable=False)
    code: Mapped[str] = mapped_column(String(100), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    field: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    row_number: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[dict[str, Any]]] = mapped_column(
        _JsonColumn(), nullable=True
    )
    resolved: Mapped[bool] = mapped_column(
        Boolean, nullable=False, server_default="false"
    )
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    # relationships
    job: Mapped[ProcessingJobOrm] = relationship(
        "ProcessingJobOrm", back_populates="validation_issues"
    )
    job_item: Mapped[Optional[JobItemOrm]] = relationship(
        "JobItemOrm", back_populates="validation_issues"
    )


# ---------------------------------------------------------------------------
# approvals
# ---------------------------------------------------------------------------

class ApprovalOrm(Base):
    """Immutable record of an approval, rejection, or cancellation action.

    Append-only in practice — never updated. Each decision creates a new row.
    """
    __tablename__ = "approvals"

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("processing_jobs.id", ondelete="CASCADE"),
        nullable=False,
    )
    # APPROVED | REJECTED | CANCELLED
    action: Mapped[str] = mapped_column(String(20), nullable=False)
    actor_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    # relationships
    job: Mapped[ProcessingJobOrm] = relationship(
        "ProcessingJobOrm", back_populates="approvals"
    )


# ---------------------------------------------------------------------------
# price_history
# ---------------------------------------------------------------------------

class PriceHistoryOrm(Base):
    """Immutable price change record — append-only historical ledger.

    ``reference_normalized`` is the primary lookup key for price tracking
    across jobs and profiles.
    """
    __tablename__ = "price_history"
    __table_args__ = (
        Index("idx_price_history_ref_date", "reference_normalized", "recorded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    profile_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("commercial_profiles.id", ondelete="SET NULL"),
        nullable=True,
    )
    job_id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        ForeignKey("processing_jobs.id", ondelete="RESTRICT"),
        nullable=False,
    )
    reference_normalized: Mapped[str] = mapped_column(Text, nullable=False)
    old_price: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    new_price: Mapped[Optional[float]] = mapped_column(
        Numeric(14, 2), nullable=True
    )
    variation_pct: Mapped[Optional[float]] = mapped_column(
        Numeric(8, 2), nullable=True
    )
    # UPDATED | NEW | BLOCKED
    change_type: Mapped[str] = mapped_column(String(30), nullable=False)
    recorded_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )
    recorded_by_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # relationships
    profile: Mapped[Optional[CommercialProfileOrm]] = relationship(
        "CommercialProfileOrm", back_populates="price_history"
    )
    job: Mapped[ProcessingJobOrm] = relationship(
        "ProcessingJobOrm", back_populates="price_history"
    )


# ---------------------------------------------------------------------------
# audit_logs  — APPEND-ONLY (enforced by RLS INSERT-only policy)
# ---------------------------------------------------------------------------

class AuditLogOrm(Base):
    """Immutable audit trail for all administrative and critical actions.

    SECURITY: This table MUST only receive INSERT operations.
    No UPDATE or DELETE should ever be permitted (enforced by RLS policy
    in 002_rls_policies.sql and by application convention).

    ``ip_hash`` stores a one-way hash of the client IP — never the raw IP.
    ``extra_metadata`` maps to the 'metadata' DB column (reserved SA name avoided).
    """
    __tablename__ = "audit_logs"
    __table_args__ = (
        Index("idx_audit_entity", "entity_type", "entity_id", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(
        _UuidColumn(),
        primary_key=True,
        default=uuid.uuid4,
    )
    actor_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    action: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(100), nullable=False)
    entity_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(), nullable=True
    )
    job_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        _UuidColumn(),
        ForeignKey("processing_jobs.id", ondelete="SET NULL"),
        nullable=True,
    )
    # NOTE: 'metadata' is reserved in SQLAlchemy Declarative; mapped to DB col 'metadata'
    extra_metadata: Mapped[Optional[dict[str, Any]]] = mapped_column(
        "metadata", _JsonColumn(), nullable=True
    )
    ip_hash: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    user_agent: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        nullable=False, server_default=func.now()
    )

    # relationships
    actor: Mapped[Optional[UserOrm]] = relationship(
        "UserOrm", back_populates="audit_logs"
    )
    job: Mapped[Optional[ProcessingJobOrm]] = relationship(
        "ProcessingJobOrm", back_populates="audit_logs"
    )
