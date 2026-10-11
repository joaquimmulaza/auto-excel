"""AI Assistive Service — Gemini Integration for Cotarco Commercial Manager.

SECURITY GUARDRAILS (obrigatórios por spec):
1. GEMINI_API_KEY reside APENAS neste módulo (backend); nunca exposta ao frontend.
2. O Gemini NÃO decide preços, stocks ou aprovações — apenas explica, resume e sugere.
3. Todas as respostas seguem schemas Pydantic v2 estrictos (structured output).
4. Fallback determinístico é ativado se a chamada ao Gemini falhar ou for inválida.
5. Inputs do utilizador são sanitizados antes de serem incluídos nos prompts.

SDK: google-genai 2.x (from google import genai)
Model default: gemini-3.5-flash-lite
Override: GEMINI_MODEL=gemini-3.6-flash|gemini-3.8-flash
"""
from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

_backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_backend_env)
load_dotenv()

from backend.app.schemas.ai import (  # noqa: E402
    AnomalyExplanation,
    ColumnMapping,
    ExecutiveSummary,
)

logger = logging.getLogger(__name__)

_genai_client = None

TModel = TypeVar("TModel", bound=BaseModel)


def _get_client():
    """Retorna o cliente genai, criando-o na primeira chamada."""
    global _genai_client
    if _genai_client is None:
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise RuntimeError(
                "GEMINI_API_KEY não configurada. "
                "Defina a variável de ambiente no backend (nunca no frontend)."
            )
        from google import genai  # type: ignore[import-untyped]

        _genai_client = genai.Client(api_key=api_key)
    return _genai_client


# Default: gemini-3.5-flash-lite. Override with GEMINI_MODEL=
# gemini-3.6-flash | gemini-3.8-flash (thinking_level may need LOW on 3.8).
_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash-lite")

_SANITIZE_PATTERN = re.compile(r"[<>\"'%;()&+]")


def _sanitize(text: str, max_len: int = 500) -> str:
    """Remove caracteres potencialmente problemáticos em prompts/outputs."""
    cleaned = _SANITIZE_PATTERN.sub("", text)
    return cleaned[:max_len]


def _sanitize_tree(value: Any, max_len: int = 500) -> Any:
    if isinstance(value, str):
        return _sanitize(value, max_len)
    if isinstance(value, list):
        return [_sanitize_tree(v, max_len) for v in value]
    if isinstance(value, dict):
        return {k: _sanitize_tree(v, max_len) for k, v in value.items()}
    return value


_SYSTEM_INSTRUCTIONS = (
    "Você é um assistente interno da Cotarco, especializado em tabelas comerciais "
    "de preços e stock. "
    "NUNCA tome decisões sobre preços, stocks ou aprovações de operações. "
    "Apenas explique, resuma e sugira. "
    "Seja conciso, direto e use linguagem empresarial profissional. "
    "Responda sempre em JSON estruturado conforme o schema solicitado."
)


def _build_explain_prompt(
    issue_code: str,
    issue_message: str,
    severity: str,
    context: dict[str, Any],
    language: str,
) -> str:
    ctx_str = ", ".join(f"{k}: {v}" for k, v in list(context.items())[:12])
    return (
        f"Analise o seguinte problema de validação numa tabela comercial.\n\n"
        f"Idioma da resposta: {language}\n"
        f"Código do erro: {_sanitize(issue_code, 100)}\n"
        f"Mensagem: {_sanitize(issue_message)}\n"
        f"Severidade: {_sanitize(severity, 20)}\n"
        f"Contexto: {_sanitize(ctx_str, 400)}\n"
        f"is_blocker deve ser true se severity for BLOCKER, caso contrário false."
    )


def _build_summary_prompt(
    job_summary: dict[str, Any],
    issues_summary: dict[str, Any],
    profile_name: str,
    language: str,
) -> str:
    return (
        f"Analise o seguinte processamento de tabela comercial.\n\n"
        f"Idioma da resposta: {language}\n"
        f"Perfil comercial: {_sanitize(profile_name, 100)}\n"
        f"Resumo quantitativo: {_sanitize_tree(job_summary)}\n"
        f"Resumo de problemas: {_sanitize_tree(issues_summary)}\n"
        f"IMPORTANTE: Não tome decisões de negócio. Apenas resuma e contextualize."
    )


def _build_column_mapping_prompt(
    detected: list[str],
    expected: list[str],
    language: str,
) -> str:
    detected_clean = [_sanitize(c, 80) for c in detected[:50]]
    expected_clean = [_sanitize(c, 80) for c in expected[:50]]
    return (
        f"Sugira o mapeamento de colunas entre o ficheiro recebido e as colunas "
        f"esperadas pelo sistema.\n\n"
        f"Idioma da resposta: {language}\n"
        f"Colunas detetadas no ficheiro: {detected_clean}\n"
        f"Colunas esperadas pelo perfil: {expected_clean}\n"
        f"IMPORTANTE: São apenas sugestões. O engine determinístico valida antes de aplicar."
    )


def _thinking_config(types_mod: Any) -> Any | None:
    """Prefer thinking_level=MINIMAL; fall back to LOW or thinking_budget=0."""
    if not hasattr(types_mod, "ThinkingConfig"):
        return None
    level_enum = getattr(types_mod, "ThinkingLevel", None)
    if level_enum is not None:
        for name in ("MINIMAL", "LOW"):
            level = getattr(level_enum, name, None)
            if level is not None:
                try:
                    return types_mod.ThinkingConfig(thinking_level=level)
                except Exception:  # noqa: BLE001
                    continue
    try:
        return types_mod.ThinkingConfig(thinking_budget=0)
    except Exception:  # noqa: BLE001
        return None


def _schema_for_model(model: type[BaseModel]) -> dict[str, Any]:
    return model.model_json_schema()


def _call_gemini_json(
    prompt: str,
    *,
    response_model: type[BaseModel] | None = None,
) -> dict[str, Any] | None:
    """Chama o Gemini com JSON structured output.

    Retorna dict parseado ou None se a chamada falhar.
    GUARDRAIL: Nunca propaga excepções ao router — usa fallback.
    """
    try:
        import json

        from google.genai import types  # type: ignore[import-untyped]

        client = _get_client()
        config_kwargs: dict[str, Any] = {
            "system_instruction": _SYSTEM_INSTRUCTIONS,
            "response_mime_type": "application/json",
            "temperature": 0.2,
            "max_output_tokens": 2048,
        }
        thinking = _thinking_config(types)
        if thinking is not None:
            config_kwargs["thinking_config"] = thinking
        if response_model is not None:
            config_kwargs["response_json_schema"] = _schema_for_model(response_model)

        response = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        raw = response.text
        if not raw:
            logger.warning("Gemini retornou resposta vazia.")
            return None
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            logger.warning("Gemini retornou JSON não-object.")
            return None
        return parsed
    except Exception as exc:  # noqa: BLE001
        logger.warning("Chamada ao Gemini falhou: %s", exc)
        return None


def _validate_or_none(
    model: type[TModel], data: dict[str, Any] | None
) -> dict[str, Any] | None:
    if not data:
        return None
    try:
        return model.model_validate(data).model_dump()
    except ValidationError as exc:
        logger.warning("Resposta Gemini inválida vs %s: %s", model.__name__, exc)
        return None


def _fallback_explanation(
    issue_code: str, issue_message: str, severity: str
) -> dict[str, Any]:
    is_blocker = severity == "BLOCKER"
    return {
        "title": f"Problema detectado: {issue_code}",
        "plain_explanation": (
            f"O sistema detectou um problema do tipo '{issue_code}'. "
            f"Detalhes: {issue_message}"
        ),
        "likely_cause": (
            "Verifique os dados da tabela para a referência/campo indicados."
        ),
        "suggested_action": (
            "Corrija o valor na tabela e reenvie o ficheiro para nova validação."
        ),
        "is_blocker": is_blocker,
    }


def _fallback_summary(job_summary: dict[str, Any]) -> dict[str, Any]:
    total = job_summary.get("total", 0)
    updated = job_summary.get("updated", 0)
    new = job_summary.get("new", 0)
    blocked = job_summary.get("blocked", 0)
    return {
        "headline": f"Processamento com {total} referências analisadas.",
        "highlights": [
            f"{updated} referências atualizadas.",
            f"{new} referências novas.",
            f"{blocked} referências bloqueadas.",
        ],
        "attention_items": (
            [f"{blocked} bloqueios requerem revisão."] if blocked else []
        ),
        "overall_assessment": (
            "Resumo gerado localmente (assistência de IA temporariamente indisponível)."
        ),
    }


def _fallback_column_mapping(
    detected: list[str], expected: list[str]
) -> dict[str, Any]:
    suggestions = [
        {
            "detected_column": col,
            "suggested_mapping": None,
            "confidence": "LOW",
            "rationale": "Mapeamento automático indisponível. Reveja manualmente.",
        }
        for col in detected
    ]
    return {
        "suggestions": suggestions,
        "unmapped_expected": expected,
        "disclaimer": (
            "Sugestões geradas localmente (IA indisponível). "
            "Reveja e confirme antes de aplicar o mapeamento."
        ),
    }


_explain_cache: dict[str, dict[str, Any]] = {}


def explain_issue(
    issue_code: str,
    issue_message: str,
    severity: str,
    context: dict[str, Any],
    language: str = "pt",
    job_id: str = "",
) -> tuple[dict[str, Any], bool]:
    """Explica uma anomalia de validação usando Gemini.

    Returns:
        (data_dict, fallback_used)
    """
    cache_key = f"{job_id}:{issue_code}:{language}"
    if job_id and cache_key in _explain_cache:
        return _explain_cache[cache_key], False

    prompt = _build_explain_prompt(
        issue_code, issue_message, severity, context, language
    )
    raw = _call_gemini_json(prompt, response_model=AnomalyExplanation)
    result = _validate_or_none(AnomalyExplanation, raw)

    if result:
        result["is_blocker"] = severity == "BLOCKER"
        result = _sanitize_tree(result)
        if job_id:
            _explain_cache[cache_key] = result
        return result, False

    return _fallback_explanation(issue_code, issue_message, severity), True


def generate_summary(
    job_summary: dict[str, Any],
    issues_summary: dict[str, Any],
    profile_name: str,
    language: str = "pt",
) -> tuple[dict[str, Any], bool]:
    """Gera resumo executivo assistivo de um processamento."""
    prompt = _build_summary_prompt(job_summary, issues_summary, profile_name, language)
    raw = _call_gemini_json(prompt, response_model=ExecutiveSummary)
    result = _validate_or_none(ExecutiveSummary, raw)

    if result:
        if not result.get("highlights"):
            result["highlights"] = ["Processamento analisado."]
        result.setdefault("attention_items", [])
        return _sanitize_tree(result), False

    return _fallback_summary(job_summary), True


def suggest_column_mapping(
    detected_columns: list[str],
    expected_columns: list[str],
    language: str = "pt",
) -> tuple[dict[str, Any], bool]:
    """Sugere mapeamento de colunas desconhecidas usando Gemini.

    GUARDRAIL: Retorna apenas sugestões — o engine determinístico
    valida e confirma antes de aplicar qualquer mapeamento.
    """
    prompt = _build_column_mapping_prompt(
        detected_columns, expected_columns, language
    )
    raw = _call_gemini_json(prompt, response_model=ColumnMapping)
    result = _validate_or_none(ColumnMapping, raw)

    if result:
        result.setdefault("unmapped_expected", [])
        result.setdefault(
            "disclaimer",
            "Sugestões geradas por IA. Reveja e confirme antes de aplicar o mapeamento.",
        )
        return _sanitize_tree(result), False

    return _fallback_column_mapping(detected_columns, expected_columns), True
