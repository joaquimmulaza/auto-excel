"""Tests for AI Assistive API endpoints (Fase 5 — Gemini Integration).

Estratégia de testes:
- NUNCA faz chamadas HTTP reais ao Google Gemini.
- Usa unittest.mock.patch para simular respostas do ai_service.
- Testa todos os cenários: sucesso, fallback, RBAC, 404, 429.
- Cobre os 3 endpoints: explain-issue, summary, suggest-columns.

Fixtures: Reutiliza conftest.py (comercial_client, operador_client, seed_db)
"""
from __future__ import annotations

import uuid
from datetime import datetime, timezone
from unittest.mock import patch

import pytest

from backend.app.infra.db.models import ProcessingJobOrm
from backend.tests.test_api.conftest import (
    COMERCIAL_USER_ID,
    OPERADOR_USER_ID,
    TEST_PROFILE_ID,
)

# ---------------------------------------------------------------------------
# Helper to create a job directly in the DB
# ---------------------------------------------------------------------------


def _make_job(db_session, owner_id=None, status="READY_FOR_REVIEW"):
    """Insere um job na DB de teste e retorna o ID."""
    if owner_id is None:
        owner_id = COMERCIAL_USER_ID
    now = datetime.now(timezone.utc)
    job = ProcessingJobOrm(
        id=uuid.uuid4(),
        profile_id=TEST_PROFILE_ID,
        created_by_id=owner_id,
        status=status,
        source_system="TEST",
        description="Test job for AI endpoints",
        options={},
        summary={
            "total": 100,
            "updated": 70,
            "new": 20,
            "ignored": 5,
            "blocked": 5,
        },
        created_at=now,
        updated_at=now,
    )
    db_session.add(job)
    db_session.commit()
    return job.id


# ============================================================================
# Tests: POST /api/v1/jobs/{id}/ai/explain-issue
# ============================================================================


class TestExplainIssue:
    """Suite para o endpoint explain-issue."""

    @patch("backend.app.api.v1.ai.ai_service.explain_issue")
    def test_explain_issue_success_with_gemini(
        self, mock_explain, comercial_client, db_session
    ):
        """Deve retornar AIResponse com AnomalyExplanation quando Gemini responde."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_explain.return_value = (
            {
                "title": "Variação de preço bloqueada",
                "plain_explanation": "O preço subiu mais de 30% face ao anterior.",
                "likely_cause": "Tabela com valores actualizados incorretamente.",
                "suggested_action": "Verifique o preço na coluna B e corrija.",
                "is_blocker": True,
            },
            False,  # fallback_used=False
        )

        payload = {
            "issue_code": "PRICE_VARIATION_BLOCKED",
            "issue_message": "Variação de 35% excede o limite de 30%",
            "severity": "BLOCKER",
            "context": {"reference": "RS64R53112A", "old_price": 2000, "new_price": 2700},
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/explain-issue", json=payload
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_ai_generated"] is True
        assert body["fallback_used"] is False
        assert body["data"]["title"] == "Variação de preço bloqueada"
        assert body["data"]["is_blocker"] is True

    @patch("backend.app.api.v1.ai.ai_service.explain_issue")
    def test_explain_issue_fallback_when_gemini_fails(
        self, mock_explain, comercial_client, db_session
    ):
        """Deve retornar AIResponse com fallback quando Gemini falha."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_explain.return_value = (
            {
                "title": "Problema detectado: MISSING_COLUMN",
                "plain_explanation": "O sistema detectou um problema do tipo 'MISSING_COLUMN'.",
                "likely_cause": "Verifique os dados da tabela.",
                "suggested_action": "Corrija o valor e reenvie.",
                "is_blocker": False,
            },
            True,  # fallback_used=True
        )

        payload = {
            "issue_code": "MISSING_COLUMN",
            "issue_message": "Coluna 'Referência' não encontrada",
            "severity": "ERROR",
            "context": {},
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/explain-issue", json=payload
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["fallback_used"] is True
        assert body["is_ai_generated"] is True
        assert "title" in body["data"]

    def test_explain_issue_returns_404_for_unknown_job(
        self, comercial_client
    ):
        """Deve retornar 404 para job_id inexistente."""
        fake_id = uuid.uuid4()
        payload = {
            "issue_code": "INVALID_PRICE",
            "issue_message": "Preço inválido",
            "severity": "ERROR",
            "context": {},
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{fake_id}/ai/explain-issue", json=payload
        )
        assert resp.status_code == 404
        assert resp.json()["error"]["code"] == "JOB_NOT_FOUND"

    @patch("backend.app.api.v1.ai.ai_service.explain_issue")
    def test_explain_issue_comercial_cannot_access_other_job(
        self, mock_explain, comercial_client, db_session
    ):
        """COMERCIAL não pode aceder ao job de outro utilizador."""
        # Job criado pelo OPERADOR
        job_id = _make_job(db_session, owner_id=OPERADOR_USER_ID)

        payload = {
            "issue_code": "DUPLICATE_REFERENCE",
            "issue_message": "Referência duplicada",
            "severity": "BLOCKER",
            "context": {},
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/explain-issue", json=payload
        )
        assert resp.status_code == 403

    @patch("backend.app.api.v1.ai.ai_service.explain_issue")
    def test_explain_issue_operador_can_access_any_job(
        self, mock_explain, operador_client, db_session
    ):
        """OPERADOR pode aceder a qualquer job."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_explain.return_value = (
            {
                "title": "Referência duplicada",
                "plain_explanation": "Existe uma referência duplicada na tabela.",
                "likely_cause": "Linha repetida no ficheiro Excel.",
                "suggested_action": "Remova a linha duplicada.",
                "is_blocker": True,
            },
            False,
        )

        payload = {
            "issue_code": "DUPLICATE_REFERENCE",
            "issue_message": "Referência duplicada",
            "severity": "BLOCKER",
            "context": {},
            "language": "pt",
        }
        resp = operador_client.post(
            f"/api/v1/jobs/{job_id}/ai/explain-issue", json=payload
        )
        assert resp.status_code == 200

    def test_explain_issue_returns_422_for_invalid_payload(
        self, comercial_client, db_session
    ):
        """Payload inválido (sem campos obrigatórios) deve retornar 422."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)
        # Envia payload sem issue_code e issue_message
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/explain-issue",
            json={"severity": "ERROR"},
        )
        assert resp.status_code == 422

    def test_explain_issue_returns_422_for_invalid_severity(
        self, comercial_client, db_session
    ):
        """Severity inválido deve retornar 422."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/explain-issue",
            json={
                "issue_code": "TEST",
                "issue_message": "Test",
                "severity": "INVALID_SEVERITY",  # não existe no enum
            },
        )
        assert resp.status_code == 422


# ============================================================================
# Tests: POST /api/v1/jobs/{id}/ai/summary
# ============================================================================


class TestAISummary:
    """Suite para o endpoint de resumo executivo."""

    @patch("backend.app.api.v1.ai.ai_service.generate_summary")
    def test_summary_success_with_gemini(
        self, mock_summary, operador_client, db_session
    ):
        """Deve retornar AIResponse com ExecutiveSummary quando Gemini responde."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_summary.return_value = (
            {
                "headline": "Processamento concluído com 100 referências analisadas.",
                "highlights": [
                    "70 referências atualizadas.",
                    "20 referências novas.",
                    "5 referências bloqueadas.",
                ],
                "attention_items": ["5 bloqueios requerem revisão."],
                "overall_assessment": "Processamento saudável com anomalias menores.",
            },
            False,
        )

        payload = {"language": "pt"}
        resp = operador_client.post(
            f"/api/v1/jobs/{job_id}/ai/summary", json=payload
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_ai_generated"] is True
        assert body["fallback_used"] is False
        assert "headline" in body["data"]
        assert isinstance(body["data"]["highlights"], list)
        assert len(body["data"]["highlights"]) >= 1

    @patch("backend.app.api.v1.ai.ai_service.generate_summary")
    def test_summary_fallback_when_gemini_unavailable(
        self, mock_summary, comercial_client, db_session
    ):
        """Deve usar fallback quando Gemini está indisponível."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_summary.return_value = (
            {
                "headline": "Processamento com 100 referências analisadas.",
                "highlights": ["70 atualizadas.", "20 novas.", "5 bloqueadas."],
                "attention_items": ["5 bloqueios requerem revisão."],
                "overall_assessment": "Resumo gerado localmente.",
            },
            True,  # fallback_used=True
        )

        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/summary", json={"language": "pt"}
        )
        assert resp.status_code == 200
        assert resp.json()["fallback_used"] is True

    def test_summary_returns_404_for_unknown_job(self, operador_client):
        """404 para job inexistente."""
        fake_id = uuid.uuid4()
        resp = operador_client.post(
            f"/api/v1/jobs/{fake_id}/ai/summary", json={"language": "pt"}
        )
        assert resp.status_code == 404

    @patch("backend.app.api.v1.ai.ai_service.generate_summary")
    def test_summary_comercial_cannot_access_other_job(
        self, mock_summary, comercial_client, db_session
    ):
        """COMERCIAL recebe 403 ao tentar aceder ao job de outro utilizador."""
        job_id = _make_job(db_session, owner_id=OPERADOR_USER_ID)

        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/summary", json={"language": "pt"}
        )
        assert resp.status_code == 403


# ============================================================================
# Tests: POST /api/v1/jobs/{id}/ai/suggest-columns
# ============================================================================


class TestSuggestColumns:
    """Suite para o endpoint de sugestão de mapeamento de colunas."""

    @patch("backend.app.api.v1.ai.ai_service.suggest_column_mapping")
    def test_suggest_columns_success(
        self, mock_suggest, comercial_client, db_session
    ):
        """Deve retornar AIResponse com ColumnMapping válido."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_suggest.return_value = (
            {
                "suggestions": [
                    {
                        "detected_column": "Ref Produto",
                        "suggested_mapping": "referencia",
                        "confidence": "HIGH",
                        "rationale": "Nome muito semelhante ao campo esperado.",
                    },
                    {
                        "detected_column": "Preco Final",
                        "suggested_mapping": "preco",
                        "confidence": "HIGH",
                        "rationale": "Campo de preço claramente identificado.",
                    },
                    {
                        "detected_column": "Qtd Disponivel",
                        "suggested_mapping": "stock",
                        "confidence": "MEDIUM",
                        "rationale": "Pode ser o campo de stock.",
                    },
                ],
                "unmapped_expected": [],
                "disclaimer": (
                    "Sugestoes geradas por IA. "
                    "Reveja e confirme antes de aplicar o mapeamento."
                ),
            },
            False,
        )

        payload = {
            "detected_columns": ["Ref Produto", "Preco Final", "Qtd Disponivel"],
            "expected_columns": ["referencia", "preco", "stock"],
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/suggest-columns", json=payload
        )

        assert resp.status_code == 200
        body = resp.json()
        assert body["is_ai_generated"] is True
        assert body["fallback_used"] is False
        data = body["data"]
        assert "suggestions" in data
        assert len(data["suggestions"]) == 3
        assert data["suggestions"][0]["confidence"] == "HIGH"
        assert "disclaimer" in data

    @patch("backend.app.api.v1.ai.ai_service.suggest_column_mapping")
    def test_suggest_columns_fallback(
        self, mock_suggest, comercial_client, db_session
    ):
        """Deve usar fallback quando Gemini falha."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_suggest.return_value = (
            {
                "suggestions": [
                    {
                        "detected_column": "ColA",
                        "suggested_mapping": None,
                        "confidence": "LOW",
                        "rationale": "Mapeamento automático indisponível.",
                    }
                ],
                "unmapped_expected": ["referencia"],
                "disclaimer": "Sugestoes geradas localmente (IA indisponível).",
            },
            True,
        )

        payload = {
            "detected_columns": ["ColA"],
            "expected_columns": ["referencia"],
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/suggest-columns", json=payload
        )
        assert resp.status_code == 200
        body = resp.json()
        assert body["fallback_used"] is True

    def test_suggest_columns_returns_422_for_empty_list(
        self, comercial_client, db_session
    ):
        """Lista vazia de colunas deve retornar 422."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)
        payload = {
            "detected_columns": [],  # min_length=1
            "expected_columns": ["referencia"],
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{job_id}/ai/suggest-columns", json=payload
        )
        assert resp.status_code == 422

    def test_suggest_columns_returns_404_for_unknown_job(
        self, comercial_client
    ):
        """404 para job inexistente."""
        fake_id = uuid.uuid4()
        payload = {
            "detected_columns": ["ColA"],
            "expected_columns": ["referencia"],
            "language": "pt",
        }
        resp = comercial_client.post(
            f"/api/v1/jobs/{fake_id}/ai/suggest-columns", json=payload
        )
        assert resp.status_code == 404

    @patch("backend.app.api.v1.ai.ai_service.suggest_column_mapping")
    def test_suggest_columns_operador_can_access_any_job(
        self, mock_suggest, operador_client, db_session
    ):
        """OPERADOR pode usar suggest-columns em qualquer job."""
        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_suggest.return_value = (
            {
                "suggestions": [],
                "unmapped_expected": ["referencia"],
                "disclaimer": "Sugestoes geradas por IA.",
            },
            False,
        )

        payload = {
            "detected_columns": ["ColA"],
            "expected_columns": ["referencia"],
            "language": "pt",
        }
        resp = operador_client.post(
            f"/api/v1/jobs/{job_id}/ai/suggest-columns", json=payload
        )
        assert resp.status_code == 200


# ============================================================================
# Tests: Rate Limiting
# ============================================================================


class TestRateLimit:
    """Testa o rate limit de chamadas de IA por utilizador."""

    @patch("backend.app.api.v1.ai.ai_service.explain_issue")
    def test_rate_limit_triggers_429(
        self, mock_explain, comercial_client, db_session
    ):
        """Após 20 chamadas num minuto, deve retornar 429."""
        # Reset rate store para este utilizador antes do teste
        from backend.app.api.v1.ai import _rate_store
        _rate_store[str(COMERCIAL_USER_ID)].clear()

        job_id = _make_job(db_session, owner_id=COMERCIAL_USER_ID)

        mock_explain.return_value = (
            {
                "title": "Test",
                "plain_explanation": "Test",
                "likely_cause": "Test",
                "suggested_action": "Test",
                "is_blocker": False,
            },
            False,
        )

        payload = {
            "issue_code": "TEST",
            "issue_message": "Test",
            "severity": "INFO",
            "context": {},
            "language": "pt",
        }

        last_resp = None
        for i in range(21):
            last_resp = comercial_client.post(
                f"/api/v1/jobs/{job_id}/ai/explain-issue", json=payload
            )
            if last_resp.status_code == 429:
                break

        assert last_resp is not None
        assert last_resp.status_code == 429
        assert last_resp.json()["error"]["code"] == "AI_RATE_LIMIT_EXCEEDED"

        # Cleanup rate store
        _rate_store[str(COMERCIAL_USER_ID)].clear()


# ============================================================================
# Tests: Schema validation (unit)
# ============================================================================


class TestAISchemas:
    """Testes unitários puros dos schemas Pydantic (sem HTTP)."""

    def test_anomaly_explanation_validates_correctly(self):
        """AnomalyExplanation deve validar dados corretos."""
        from backend.app.schemas.ai import AnomalyExplanation

        data = {
            "title": "Preço inválido",
            "plain_explanation": "O preço introduzido não é um número válido.",
            "likely_cause": "Formato de número incorreto na célula.",
            "suggested_action": "Corrija para um valor numérico sem letras.",
            "is_blocker": False,
        }
        obj = AnomalyExplanation.model_validate(data)
        assert obj.title == "Preço inválido"
        assert obj.is_blocker is False

    def test_executive_summary_requires_highlights(self):
        """ExecutiveSummary deve falhar se highlights estiver vazio."""
        from backend.app.schemas.ai import ExecutiveSummary
        import pydantic

        with pytest.raises(pydantic.ValidationError):
            ExecutiveSummary.model_validate(
                {
                    "headline": "Test",
                    "highlights": [],  # min_length=1
                    "overall_assessment": "Test",
                }
            )

    def test_column_suggestion_confidence_validation(self):
        """ColumnSuggestion deve rejeitar confidence inválido."""
        from backend.app.schemas.ai import ColumnSuggestion
        import pydantic

        with pytest.raises(pydantic.ValidationError):
            ColumnSuggestion(
                detected_column="ColA",
                suggested_mapping="ref",
                confidence="VERY_HIGH",  # inválido — só HIGH|MEDIUM|LOW
                rationale="Test",
            )

    def test_ai_response_wrapper_structure(self):
        """AIResponse deve encapsular corretamente o payload de IA."""
        from backend.app.schemas.ai import AIResponse, AnomalyExplanation

        explanation = AnomalyExplanation(
            title="Teste",
            plain_explanation="Explicação teste.",
            likely_cause="Causa teste.",
            suggested_action="Ação teste.",
            is_blocker=True,
        )
        response = AIResponse(
            is_ai_generated=True,
            fallback_used=False,
            data=explanation,
        )
        assert response.is_ai_generated is True
        assert response.fallback_used is False
        assert response.data.title == "Teste"

    def test_explain_issue_request_sanitizes_language(self):
        """Linguagem inválida deve ser rejeitada pelo schema."""
        from backend.app.schemas.ai import ExplainIssueRequest
        import pydantic

        with pytest.raises(pydantic.ValidationError):
            ExplainIssueRequest(
                issue_code="TEST",
                issue_message="Test",
                severity="INFO",
                language="INVALID_LANG",  # pattern ^[a-z]{2}$ falha
            )
