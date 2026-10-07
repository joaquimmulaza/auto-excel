"""Price history and exception queue endpoints."""
from __future__ import annotations

from fastapi import APIRouter, Depends, Query

from backend.app.api.deps import DbDep, UserDep, require_role
from backend.app.infra.db.models import JobItemOrm, ProcessingJobOrm
from backend.app.infra.repositories.jobs import JobRepository

router = APIRouter(tags=["history"])


@router.get(
    "/history/prices",
    dependencies=[Depends(require_role("OPERADOR", "ADMIN"))],
)
def list_price_history(
    current_user: UserDep,
    db: DbDep,
    reference: str = Query(..., min_length=1),
    limit: int = Query(50, ge=1, le=200),
):
    repo = JobRepository(db)
    rows = repo.list_price_history(reference.upper().replace(" ", ""), limit=limit)
    return {
        "items": [
            {
                "id": str(r.id),
                "profile_id": str(r.profile_id),
                "job_id": str(r.job_id) if r.job_id else None,
                "reference_normalized": r.reference_normalized,
                "old_price": r.old_price,
                "new_price": r.new_price,
                "variation_pct": r.variation_pct,
                "change_type": r.change_type,
                "recorded_at": r.recorded_at.isoformat() if r.recorded_at else None,
            }
            for r in rows
        ]
    }


@router.get(
    "/exceptions",
    dependencies=[Depends(require_role("OPERADOR", "ADMIN"))],
)
def list_exceptions(
    current_user: UserDep,
    db: DbDep,
    limit: int = Query(100, ge=1, le=500),
):
    """Operator exception queue: blocked items across open jobs."""
    rows = (
        db.query(JobItemOrm, ProcessingJobOrm)
        .join(ProcessingJobOrm, ProcessingJobOrm.id == JobItemOrm.job_id)
        .filter(JobItemOrm.decision == "BLOCKED")
        .filter(
            ProcessingJobOrm.status.in_(
                ("READY_FOR_REVIEW", "NEEDS_CORRECTION", "APPROVED", "UPLOADED", "VALIDATING")
            )
        )
        .order_by(JobItemOrm.created_at.desc())
        .limit(limit)
        .all()
    )
    items = []
    for item, job in rows:
        value = None
        if item.new_price is not None and item.new_stock is not None:
            value = float(item.new_price) * int(item.new_stock)
        elif item.new_price is not None:
            value = float(item.new_price)
        items.append(
            {
                "job_id": str(job.id),
                "job_number": job.job_number,
                "job_status": job.status,
                "description": job.description,
                "item_id": str(item.id),
                "reference_original": item.reference_original,
                "reference_normalized": item.reference_normalized,
                "old_price": item.old_price,
                "new_price": item.new_price,
                "price_variation_pct": item.price_variation_pct,
                "decision_code": item.decision_code,
                "decision": item.decision,
                "estimated_value": value,
                "details": item.details,
            }
        )
    # Sort by abs variation then value
    items.sort(
        key=lambda x: (
            -(abs(x["price_variation_pct"]) if x["price_variation_pct"] is not None else 0),
            -(x["estimated_value"] or 0),
        )
    )
    return {"items": items, "total": len(items)}
