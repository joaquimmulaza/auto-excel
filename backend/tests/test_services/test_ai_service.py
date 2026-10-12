"""Unit tests for Gemini AI service hardening (Prompt E + Prompt B)."""
from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from backend.app.schemas.ai import (
    AnomalyExplanation,
    ColumnMapping,
    ExecutiveSummary,
)
from backend.app.services import ai_service


@pytest.fixture(autouse=True)
def _clear_explain_cache():
    ai_service._explain_cache.clear()
    yield
    ai_service._explain_cache.clear()


def test_call_gemini_uses_structured_schema_and_minimal_thinking():
    fake_response = MagicMock()
    fake_response.text = (
        '{"title":"t","plain_explanation":"p","likely_cause":"c",'
        '"suggested_action":"a","is_blocker":true}'
    )
    client = MagicMock()
    client.models.generate_content.return_value = fake_response

    with (
        patch.object(ai_service, "_get_client", return_value=client),
        patch.object(ai_service, "_MODEL", "gemini-3.5-flash-lite"),
    ):
        result = ai_service._call_gemini_json(
            "prompt",
            response_model=AnomalyExplanation,
        )

    assert result is not None
    assert result["title"] == "t"
    kwargs = client.models.generate_content.call_args.kwargs
    assert kwargs["model"] == "gemini-3.5-flash-lite"
    config = kwargs["config"]
    assert config.response_mime_type == "application/json"
    assert config.response_json_schema is not None
    thinking = config.thinking_config
    assert thinking is not None
    assert str(thinking.thinking_level).endswith("MINIMAL") or (
        getattr(thinking.thinking_level, "value", "") == "MINIMAL"
    )


def test_call_gemini_invalid_json_returns_none():
    fake_response = MagicMock()
    fake_response.text = "not-json"
    client = MagicMock()
    client.models.generate_content.return_value = fake_response
    with patch.object(ai_service, "_get_client", return_value=client):
        assert ai_service._call_gemini_json("p", response_model=AnomalyExplanation) is None


def test_explain_issue_revalidates_with_pydantic_and_falls_back():
    with patch.object(
        ai_service,
        "_call_gemini_json",
        return_value={"title": "only-title"},  # invalid vs AnomalyExplanation
    ):
        data, fallback = ai_service.explain_issue(
            issue_code="PRICE_VARIATION_BLOCKED",
            issue_message="variação alta",
            severity="BLOCKER",
            context={"reference": "SKU-1"},
        )
    assert fallback is True
    AnomalyExplanation.model_validate(data)


def test_explain_issue_success_sanitizes_and_overrides_blocker():
    with patch.object(
        ai_service,
        "_call_gemini_json",
        return_value={
            "title": "Ok",
            "plain_explanation": "Explicação",
            "likely_cause": "Causa",
            "suggested_action": "Ação",
            "is_blocker": False,  # must be overridden for BLOCKER
        },
    ):
        data, fallback = ai_service.explain_issue(
            issue_code="PRICE_VARIATION_BLOCKED",
            issue_message="msg",
            severity="BLOCKER",
            context={},
        )
    assert fallback is False
    assert data["is_blocker"] is True


def test_generate_summary_sanitizes_strings():
    with patch.object(
        ai_service,
        "_call_gemini_json",
        return_value={
            "headline": "<script>hack</script>Resumo",
            "highlights": ["ok"],
            "attention_items": [],
            "overall_assessment": "bom",
        },
    ):
        data, fallback = ai_service.generate_summary(
            job_summary={"total": 1, "updated": 0, "new": 0, "blocked": 0},
            issues_summary={},
            profile_name="Loja",
        )
    assert fallback is False
    assert "<" not in data["headline"]
    ExecutiveSummary.model_validate(data)


def test_suggest_columns_invalid_payload_falls_back():
    with patch.object(
        ai_service,
        "_call_gemini_json",
        return_value={"suggestions": [{"detected_column": "A"}]},  # incomplete
    ):
        data, fallback = ai_service.suggest_column_mapping(
            detected_columns=["A"],
            expected_columns=["REF"],
        )
    assert fallback is True
    ColumnMapping.model_validate(data)


def test_default_model_is_flash_lite():
    assert "3.5-flash-lite" in ai_service._MODEL or ai_service._MODEL.endswith(
        "flash-lite"
    )
