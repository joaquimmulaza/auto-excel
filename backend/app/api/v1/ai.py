"""AI Assistive endpoints for Cotarco Commercial Manager.

Rota base: /api/v1/jobs/{job_id}/ai/

Endpoints:
  POST /jobs/{id}/ai/explain-issue   — explica anomalia de validação
  POST /jobs/{id}/ai/summary         — resumo executivo do processamento
  POST /jobs/{id}/ai/suggest-columns — sugere mapeamento de colunas

GUARDRAILS obrigatórios:
1. Todos os endpoints requerem autenticação (UserDep).
2. RBAC: suggest-columns requer COMERCIAL+; os outros são autenticados+autorizado.
3. O utilizador só pode chamar endpoints do próprio job (COMERCIAL);
   OPERADOR/ADMIN podem aceder qualquer job.
4. Rate limit por utilizador: máximo 20 chamadas/minuto (simplificado com in-memory).
5. Logs de audit gerados para cada chamada de IA.
6. Gemini nunca decide preços, stocks ou aprovações.
"""
from __future__ import annotations

import logging
import time
import uuid
from collections import defaultdict
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, HTTPException, status

from backend.app.api.deps import DbDep, UserDep
from backend.app.infra.db.models import AuditLogOrm
from backend.app.infra.repositories.jobs import JobRepository
from backend.app.schemas.ai import (
    AIResponse,
    AnomalyExplanation,
    ColumnMapping,
    ColumnSuggestion,
    ExecutiveSummary,
    ExplainIssueRequest,
    SuggestColumnsRequest,
    SummaryRequest,
)
from backend.app.services import ai_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/jobs", tags=["ai"])

# ---------------------------------------------------------------------------
# Simple in-memory rate limiter (per user, per minute)
# In production, replace with Redis-backed sliding window.
# ---------------------------------------------------------------------------

_rate_store: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT = 12  # max calls per user per minute (15 RPM Free Tier limit)
_RATE_WINDOW = 60.0  # seconds


def _check_rate_limit(user_id: uuid.UUID) -> None:
    """Raises 429 if user exceeds rate limit.

    GUARDRAIL: Limitar chamadas por utilizador para proteger quota da API Gemini.
    """
    key = str(user_id)
    now = time.monotonic()
    window_start = now - _RATE_WINDOW
    # Prune old entries
    _rate_store[key] = [t for t in _rate_store[key] if t > window_start]
    if len(_rate_store[key]) >= _RATE_LIMIT:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail={
                "error": {
                    "code": "AI_RATE_LIMIT_EXCEEDED",
                    "message": f"Limite de {_RATE_LIMIT} pedidos de IA por minuto atingido.",
                    "request_id": "",
                }
            },
        )
    _rate_store[key].append(now)


# ---------------------------------------------------------------------------
# Helper: load and authorize job
# ---------------------------------------------------------------------------


def _get_authorized_job(job_id: uuid.UUID, current_user, db):
    """Obtém o job e verifica autorização.

    RBAC:
    - OPERADOR/ADMIN: acesso a qualquer job
    - COMERCIAL: apenas ao próprio job
    """
    repo = JobRepository(db)
    job = repo.get_by_id(job_id)
    if not job:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": {
                    "code": "JOB_NOT_FOUND",
                    "message": "Processamento não encontrado.",
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
                    "message": "Sem autorização para aceder a este processamento.",
                    "request_id": "",
                }
            },
        )
    return job, repo


def _append_audit(
    repo: JobRepository,
    actor_id: uuid.UUID,
    job_id: uuid.UUID,
    action: str,
    metadata: dict[str, Any],
) -> None:
    """Regista chamada de IA no audit log."""
    try:
        audit = AuditLogOrm(
            id=uuid.uuid4(),
            actor_id=actor_id,
            action=action,
            entity_type="processing_job",
            entity_id=job_id,
            job_id=job_id,
            extra_metadata=metadata,
            created_at=datetime.now(timezone.utc),
        )
        repo.append_audit_log(audit)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Falha ao registar audit log de IA: %s", exc)


# ---------------------------------------------------------------------------
# POST /jobs/{job_id}/ai/explain-issue
# ---------------------------------------------------------------------------


@router.post(
    "/{job_id}/ai/explain-issue",
    response_model=AIResponse,
    summary="Explicar anomalia de validação com IA assistiva",
    description=(
        "Usa o Gemini para explicar em linguagem natural uma anomalia de validação. "
        "**A resposta é apenas assistiva — nunca substitui regras determinísticas.**"
    ),
)
def explain_issue(
    job_id: uuid.UUID,
    payload: ExplainIssueRequest,
    current_user: UserDep,
    db: DbDep,
) -> AIResponse:
    """POST /jobs/{job_id}/ai/explain-issue"""
    _check_rate_limit(current_user.id)
    job, repo = _get_authorized_job(job_id, current_user, db)

    data_dict, fallback_used = ai_service.explain_issue(
        issue_code=payload.issue_code,
        issue_message=payload.issue_message,
        severity=payload.severity.value,
        context=payload.context,
        language=payload.language,
        job_id=str(job_id),
    )

    _append_audit(
        repo,
        actor_id=current_user.id,
        job_id=job_id,
        action="AI_EXPLAIN_ISSUE",
        metadata={
            "issue_code": payload.issue_code,
            "severity": payload.severity.value,
            "fallback_used": fallback_used,
        },
    )

    explanation = AnomalyExplanation.model_validate(data_dict)
    return AIResponse(
        is_ai_generated=True,
        fallback_used=fallback_used,
        data=explanation,
    )


# ---------------------------------------------------------------------------
# POST /jobs/{job_id}/ai/summary
# ---------------------------------------------------------------------------


@router.post(
    "/{job_id}/ai/summary",
    response_model=AIResponse,
    summary="Resumo executivo assistivo do processamento",
    description=(
        "Gera um resumo em linguagem natural do estado do processamento. "
        "**A resposta é apenas assistiva — não substitui os dados quantitativos.**"
    ),
)
def generate_summary(
    job_id: uuid.UUID,
    payload: SummaryRequest,
    current_user: UserDep,
    db: DbDep,
) -> AIResponse:
    """POST /jobs/{job_id}/ai/summary"""
    _check_rate_limit(current_user.id)
    job, repo = _get_authorized_job(job_id, current_user, db)

    # Build context from job data
    job_summary: dict[str, Any] = job.summary or {}
    profile_name = getattr(job, "profile", None)
    profile_name_str = (
        profile_name.name if profile_name else "Perfil desconhecido"
    )
    issues_summary: dict[str, Any] = {
        "status": job.status,
        "error_message": job.error_message or "",
    }

    data_dict, fallback_used = ai_service.generate_summary(
        job_summary=job_summary,
        issues_summary=issues_summary,
        profile_name=profile_name_str,
        language=payload.language,
    )

    _append_audit(
        repo,
        actor_id=current_user.id,
        job_id=job_id,
        action="AI_SUMMARY",
        metadata={
            "job_status": job.status,
            "fallback_used": fallback_used,
        },
    )

    summary = ExecutiveSummary.model_validate(data_dict)
    return AIResponse(
        is_ai_generated=True,
        fallback_used=fallback_used,
        data=summary,
    )


# ---------------------------------------------------------------------------
# POST /jobs/{job_id}/ai/suggest-columns
# ---------------------------------------------------------------------------


@router.post(
    "/{job_id}/ai/suggest-columns",
    response_model=AIResponse,
    summary="Sugerir mapeamento de colunas com IA assistiva",
    description=(
        "Usa o Gemini para sugerir como mapear colunas desconhecidas do ficheiro "
        "às colunas esperadas pelo perfil comercial. "
        "**Sugestões são apenas orientativas — o engine valida antes de aplicar.**"
    ),
)
def suggest_columns(
    job_id: uuid.UUID,
    payload: SuggestColumnsRequest,
    current_user: UserDep,
    db: DbDep,
) -> AIResponse:
    """POST /jobs/{job_id}/ai/suggest-columns"""
    _check_rate_limit(current_user.id)
    job, repo = _get_authorized_job(job_id, current_user, db)

    # RBAC: suggest-columns requer COMERCIAL+ (todos os autenticados já têm acesso)
    # Esta verificação extra bloqueia apenas chamadas de sistema sem papel reconhecido
    if current_user.role not in ("COMERCIAL", "OPERADOR", "ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={
                "error": {
                    "code": "FORBIDDEN",
                    "message": "Papel não autorizado para sugestão de colunas.",
                    "request_id": "",
                }
            },
        )

    data_dict, fallback_used = ai_service.suggest_column_mapping(
        detected_columns=payload.detected_columns,
        expected_columns=payload.expected_columns,
        language=payload.language,
    )

    _append_audit(
        repo,
        actor_id=current_user.id,
        job_id=job_id,
        action="AI_SUGGEST_COLUMNS",
        metadata={
            "detected_count": len(payload.detected_columns),
            "expected_count": len(payload.expected_columns),
            "fallback_used": fallback_used,
        },
    )

    # Build ColumnMapping from data_dict
    suggestions_data = data_dict.get("suggestions", [])
    suggestions = [
        ColumnSuggestion(
            detected_column=s.get("detected_column", ""),
            suggested_mapping=s.get("suggested_mapping"),
            confidence=s.get("confidence", "LOW"),
            rationale=s.get("rationale", ""),
        )
        for s in suggestions_data
    ]
    mapping = ColumnMapping(
        suggestions=suggestions,
        unmapped_expected=data_dict.get("unmapped_expected", []),
        disclaimer=data_dict.get(
            "disclaimer",
            "Sugestoes geradas por IA. Reveja e confirme antes de aplicar o mapeamento.",
        ),
    )

    return AIResponse(
        is_ai_generated=True,
        fallback_used=fallback_used,
        data=mapping,
    )
