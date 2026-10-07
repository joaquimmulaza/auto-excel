"""Orchestrates validation and final processing for a job."""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any

from sqlalchemy.orm import Session

from backend.app.domain.engine import process_price_table
from backend.app.domain.models import DecisionCode, ProcessResult
from backend.app.infra.db.models import (
    AuditLogOrm,
    JobFileOrm,
    JobItemOrm,
    PriceHistoryOrm,
    ProcessingJobOrm,
    ValidationIssueOrm,
)
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.infra.repositories.profiles import ProfileRepository
from backend.app.services.excel_io import (
    read_excel_records,
    write_decision_log,
    write_excel_bytes,
)
from backend.app.services.profile_adapter import orm_profile_to_domain
from backend.app.services.observability import log_event
from backend.app.services.storage import read_bytes, store_bytes


def _decision_label(code: str) -> str:
    mapping = {
        DecisionCode.UPDATE.value: "UPDATE",
        DecisionCode.NEW_PRODUCT.value: "NEW",
        DecisionCode.IGNORED_EXISTS.value: "IGNORED",
        DecisionCode.IGNORED_STOCK.value: "IGNORED",
        DecisionCode.IGNORED_EMPTY_REF.value: "IGNORED",
        DecisionCode.IGNORED_ZERO_PRICE.value: "IGNORED",
        DecisionCode.BLOCKED_PRICE_VARIATION.value: "BLOCKED",
        DecisionCode.BLOCKED_DUPLICATE_REF.value: "BLOCKED",
        DecisionCode.BLOCKED_ZERO_PRICE.value: "BLOCKED",
        DecisionCode.DUPLICATE_REFERENCE.value: "BLOCKED",
        DecisionCode.ZERO_PRICE_REJECTED.value: "BLOCKED",
        DecisionCode.BLOQUEADO_VARIACAO_EXCESSIVA.value: "BLOCKED",
    }
    return mapping.get(code, code.split("_")[0] if "_" in code else code)


def _summary_dict(result: ProcessResult) -> dict[str, Any]:
    s = result.summary
    return {
        "total": s.total_source_rows,
        "updated": s.updated,
        "new": s.new_added,
        "ignored": s.total_ignored,
        "blocked": s.total_blocked,
        "ignored_stock": s.ignored_stock,
        "ignored_exists": s.ignored_exists,
        "ignored_zero_price": s.ignored_zero_price,
        "blocked_price_variation": s.blocked_price_variation,
        "blocked_duplicates": s.blocked_duplicates,
        "blocked_zero_price": s.blocked_zero_price,
        "total_issues": s.total_issues,
        "total_target_rows": s.total_target_rows,
    }


def _latest_accepted_prices(
    repo: JobRepository, profile_id: uuid.UUID, references: list[str]
) -> dict[str, float]:
    """Last accepted price from history overrides catalog cell when present."""
    out: dict[str, float] = {}
    for ref in references:
        history = repo.list_price_history(ref, limit=1)
        for entry in history:
            if entry.profile_id == profile_id and entry.change_type in ("UPDATED", "NEW"):
                if entry.new_price is not None:
                    out[ref] = float(entry.new_price)
                break
    return out


def _apply_price_history(
    catalog: list[dict[str, Any]],
    history_prices: dict[str, float],
) -> list[dict[str, Any]]:
    if not history_prices:
        return catalog
    enriched = []
    for row in catalog:
        copy = dict(row)
        # Try common id keys
        for key in ("internal_identifier", "referencia", "REF", "sku", "reference"):
            raw = copy.get(key)
            if raw is None:
                continue
            from backend.app.domain.normalization import ultra_clean

            norm = ultra_clean(raw)
            if norm in history_prices:
                if "original_price" in copy:
                    copy["original_price"] = history_prices[norm]
                elif "price" in copy:
                    copy["price"] = history_prices[norm]
                copy["_price_from_history"] = True
            break
        enriched.append(copy)
    return enriched


def get_file(db: Session, job_id: uuid.UUID, kind: str) -> JobFileOrm | None:
    return (
        db.query(JobFileOrm)
        .filter(JobFileOrm.job_id == job_id, JobFileOrm.kind == kind)
        .order_by(JobFileOrm.created_at.desc())
        .first()
    )


def validate_job(
    db: Session,
    job: ProcessingJobOrm,
    *,
    actor_id: uuid.UUID,
    dry_run: bool | None = None,
) -> dict[str, Any]:
    repo = JobRepository(db)
    profiles = ProfileRepository(db)
    profile_orm = profiles.get_by_id(job.profile_id)
    if not profile_orm or not profile_orm.active:
        raise ValueError("PROFILE_NOT_FOUND")

    source_file = get_file(db, job.id, "INPUT")
    if not source_file:
        raise ValueError("MISSING_INPUT_FILE")

    catalog_file = get_file(db, job.id, "CATALOG")
    source_records = read_excel_records(read_bytes(source_file.storage_path))
    catalog_records = (
        read_excel_records(read_bytes(catalog_file.storage_path)) if catalog_file else []
    )

    domain_profile = orm_profile_to_domain(profile_orm)

    # Enrich catalog with last accepted prices
    from backend.app.domain.normalization import ultra_clean

    refs = []
    for row in catalog_records:
        for key in ("internal_identifier", "referencia", "REF", "sku", "reference"):
            if row.get(key) is not None:
                refs.append(ultra_clean(row[key]))
                break
    history_prices = _latest_accepted_prices(repo, job.profile_id, refs)
    catalog_records = _apply_price_history(catalog_records, history_prices)

    is_dry_run = dry_run if dry_run is not None else bool((job.options or {}).get("dry_run"))
    options = dict(job.options or {})
    options["dry_run"] = is_dry_run
    job.options = options

    job.status = "VALIDATING"
    db.flush()
    log_event("VALIDATION_STARTED", job_id=job.id)

    # Clear previous validation artefacts
    db.query(JobItemOrm).filter(JobItemOrm.job_id == job.id).delete()
    db.query(ValidationIssueOrm).filter(ValidationIssueOrm.job_id == job.id).delete()
    db.flush()

    result = process_price_table(source_records, catalog_records, domain_profile)
    now = datetime.now(timezone.utc)

    item_rows: list[JobItemOrm] = []
    for item in result.items:
        code = (
            item.decision_code.value
            if hasattr(item.decision_code, "value")
            else str(item.decision_code)
        )
        details = dict(item.details or {})
        if item.reference_normalized in history_prices:
            details["compared_to_last_accepted_price"] = history_prices[item.reference_normalized]
        item_rows.append(
            JobItemOrm(
                id=uuid.uuid4(),
                job_id=job.id,
                reference_original=item.reference_original,
                reference_normalized=item.reference_normalized,
                old_price=item.old_price,
                new_price=item.new_price,
                old_stock=item.old_stock,
                new_stock=item.new_stock,
                price_variation_pct=item.price_variation_pct,
                decision=_decision_label(code),
                decision_code=code,
                details=details,
                created_at=now,
                updated_at=now,
            )
        )
    if item_rows:
        repo.bulk_insert_items(item_rows)

    issue_rows: list[ValidationIssueOrm] = []
    for issue in result.issues:
        issue_rows.append(
            ValidationIssueOrm(
                id=uuid.uuid4(),
                job_id=job.id,
                severity=issue.severity.value if hasattr(issue.severity, "value") else str(issue.severity),
                code=issue.code,
                message=issue.message,
                field=issue.field,
                row_number=issue.row_number,
                details=issue.details or {},
                resolved=False,
                created_at=now,
            )
        )
    if issue_rows:
        repo.bulk_insert_issues(issue_rows)

    summary = _summary_dict(result)
    summary["dry_run"] = is_dry_run
    summary["rules_version"] = profile_orm.rules_version
    summary["profile_code"] = profile_orm.code
    summary["source_sha256"] = source_file.sha256
    if catalog_file:
        summary["catalog_sha256"] = catalog_file.sha256
    job.summary = summary

    # Persist a preview output snapshot for later process (not final export path)
    preview = store_bytes(
        job_id=job.id,
        kind="REPORT",
        original_name="preview_output.xlsx",
        content=write_excel_bytes(result.output_records),
    )
    db.add(
        JobFileOrm(
            id=uuid.uuid4(),
            job_id=job.id,
            kind="REPORT",
            original_name=preview["original_name"],
            storage_path=preview["storage_path"],
            sha256=preview["sha256"],
            size_bytes=preview["size_bytes"],
            mime_type=preview["mime_type"],
            version=1,
            uploaded_by_id=actor_id,
            created_at=now,
        )
    )

    # Cache output records path marker in options for process step
    options["preview_sha256"] = preview["sha256"]
    job.options = options

    if result.has_blockers:
        job.status = "NEEDS_CORRECTION"
    else:
        job.status = "READY_FOR_REVIEW"

    repo.append_audit_log(
        AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=actor_id,
            action="JOB_VALIDATED",
            entity_type="processing_job",
            entity_id=job.id,
            job_id=job.id,
            extra_metadata={
                "status": job.status,
                "dry_run": is_dry_run,
                "summary": summary,
            },
            created_at=now,
        )
    )
    db.flush()
    return {"job_id": str(job.id), "status": job.status, "summary": summary, "dry_run": is_dry_run}


def process_job(
    db: Session,
    job: ProcessingJobOrm,
    *,
    actor_id: uuid.UUID,
) -> dict[str, Any]:
    if job.status != "APPROVED":
        raise ValueError("INVALID_STATE")
    if (job.options or {}).get("dry_run"):
        raise ValueError("DRY_RUN_CANNOT_PROCESS")

    repo = JobRepository(db)
    now = datetime.now(timezone.utc)
    job.status = "PROCESSING"
    job.started_at = now
    db.flush()
    log_event("PROCESSING_STARTED", job_id=job.id, actor_id=actor_id)

    report = get_file(db, job.id, "REPORT")
    items = repo.list_items(job.id)
    if not report:
        raise ValueError("MISSING_PREVIEW")

    output_records = read_excel_records(read_bytes(report.storage_path))
    output_meta = store_bytes(
        job_id=job.id,
        kind="OUTPUT",
        original_name="Mano-preco-atualizado-final.xlsx",
        content=write_excel_bytes(output_records),
    )
    log_meta = store_bytes(
        job_id=job.id,
        kind="LOG",
        original_name="LOG_DECISAO.xlsx",
        content=write_decision_log(
            [
                {
                    "reference_original": i.reference_original,
                    "reference_normalized": i.reference_normalized,
                    "old_price": i.old_price,
                    "new_price": i.new_price,
                    "old_stock": i.old_stock,
                    "new_stock": i.new_stock,
                    "price_variation_pct": i.price_variation_pct,
                    "decision": i.decision,
                    "decision_code": i.decision_code,
                }
                for i in items
            ]
        ),
    )

    for kind, meta in (("OUTPUT", output_meta), ("LOG", log_meta)):
        db.add(
            JobFileOrm(
                id=uuid.uuid4(),
                job_id=job.id,
                kind=kind,
                original_name=meta["original_name"],
                storage_path=meta["storage_path"],
                sha256=meta["sha256"],
                size_bytes=meta["size_bytes"],
                mime_type=meta["mime_type"],
                version=1,
                uploaded_by_id=actor_id,
                created_at=now,
            )
        )

    for item in items:
        if item.decision in ("UPDATE", "NEW") and item.new_price is not None:
            repo.record_price_history(
                PriceHistoryOrm(
                    id=uuid.uuid4(),
                    profile_id=job.profile_id,
                    job_id=job.id,
                    reference_normalized=item.reference_normalized,
                    old_price=item.old_price,
                    new_price=item.new_price,
                    variation_pct=item.price_variation_pct,
                    change_type="NEW" if item.decision == "NEW" else "UPDATED",
                    recorded_at=now,
                    recorded_by_id=actor_id,
                )
            )

    summary = dict(job.summary or {})
    summary["output_sha256"] = output_meta["sha256"]
    summary["log_sha256"] = log_meta["sha256"]
    summary["processed_by"] = str(actor_id)
    summary["processed_at"] = now.isoformat()
    job.summary = summary
    job.status = "COMPLETED"
    job.completed_at = now
    log_event("PROCESSING_COMPLETED", job_id=job.id, actor_id=actor_id)

    repo.append_audit_log(
        AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=actor_id,
            action="JOB_PROCESSED",
            entity_type="processing_job",
            entity_id=job.id,
            job_id=job.id,
            extra_metadata={"output_sha256": output_meta["sha256"]},
            created_at=now,
        )
    )
    db.flush()
    return {
        "job_id": str(job.id),
        "status": job.status,
        "output_sha256": output_meta["sha256"],
        "log_sha256": log_meta["sha256"],
        "summary": summary,
    }


def build_receipt(job: ProcessingJobOrm, db: Session) -> dict[str, Any]:
    files = (
        db.query(JobFileOrm)
        .filter(JobFileOrm.job_id == job.id)
        .order_by(JobFileOrm.created_at.asc())
        .all()
    )
    return {
        "job_id": str(job.id),
        "job_number": job.job_number,
        "status": job.status,
        "profile_id": str(job.profile_id),
        "created_by_id": str(job.created_by_id),
        "approved_by_id": str(job.approved_by_id) if job.approved_by_id else None,
        "source_system": job.source_system,
        "description": job.description,
        "summary": job.summary or {},
        "options": job.options or {},
        "files": [
            {
                "id": str(f.id),
                "kind": f.kind,
                "original_name": f.original_name,
                "sha256": f.sha256,
                "size_bytes": f.size_bytes,
                "created_at": f.created_at.isoformat() if f.created_at else None,
            }
            for f in files
        ],
        "created_at": job.created_at.isoformat() if job.created_at else None,
        "updated_at": job.updated_at.isoformat() if job.updated_at else None,
        "completed_at": job.completed_at.isoformat() if job.completed_at else None,
    }
