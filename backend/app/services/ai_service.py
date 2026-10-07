"""AI Assistive Service — Gemini Integration for Cotarco Commercial Manager.

SECURITY GUARDRAILS (obrigatórios por spec):
1. GEMINI_API_KEY reside APENAS neste módulo (backend); nunca exposta ao frontend.
2. O Gemini NÃO decide preços, stocks ou aprovações — apenas explica, resume e sugere.
3. Todas as respostas seguem schemas Pydantic v2 estrictos.
4. Fallback determinístico é ativado se a chamada ao Gemini falhar.
5. Inputs do utilizador são sanitizados antes de serem incluídos nos prompts.

SDK: google-genai 2.x (from google import genai)
Model: gemini-2.0-flash (rápido, custo-eficiente para assistência contextual)
"""
from __future__ import annotations
import os
from pathlib import Path
from dotenv import load_dotenv

_backend_env = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(_backend_env)
load_dotenv()


import logging
import os
import re
from typing import Any

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Lazy client — inicializado apenas quando GEMINI_API_KEY está presente
# ---------------------------------------------------------------------------

_genai_client = None


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


# ---------------------------------------------------------------------------
# Model constant
# ---------------------------------------------------------------------------

_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

# ---------------------------------------------------------------------------
# Input sanitization
# ---------------------------------------------------------------------------

_SANITIZE_PATTERN = re.compile(r"[<>\"'%;()&+]")


def _sanitize(text: str, max_len: int = 500) -> str:
    """Remove caracteres potencialmente problemáticos em prompts.

    GUARDRAIL: Inputs de utilizador nunca são inseridos crus no prompt.
    Limita comprimento para evitar prompt injection via inputs grandes.
    """
    cleaned = _SANITIZE_PATTERN.sub("", text)
    return cleaned[:max_len]


# ---------------------------------------------------------------------------
# Prompt builders
# ---------------------------------------------------------------------------

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
    ctx_str = ", ".join(f"{k}: {v}" for k, v in list(context.items())[:8])
    return (
        f"Analise o seguinte problema de validação numa tabela comercial e responda "
        f"em JSON estricto com os campos: "
        f"title (str, max 120 chars), "
        f"plain_explanation (str, max 800 chars), "
        f"likely_cause (str, max 400 chars), "
        f"suggested_action (str, max 400 chars, SEM decidir preços ou stocks), "
        f"is_blocker (bool).\n\n"
        f"Idioma da resposta: {language}\n"
        f"Código do erro: {_sanitize(issue_code, 100)}\n"
        f"Mensagem: {_sanitize(issue_message)}\n"
        f"Severidade: {_sanitize(severity, 20)}\n"
        f"Contexto: {_sanitize(ctx_str, 300)}\n"
        f"is_blocker deve ser true se severity for BLOCKER, caso contrário false."
    )


def _build_summary_prompt(
    job_summary: dict[str, Any],
    issues_summary: dict[str, Any],
    profile_name: str,
    language: str,
) -> str:
    return (
        f"Analise o seguinte processamento de tabela comercial e responda em JSON "
        f"estricto com os campos: "
        f"headline (str, max 200 chars), "
        f"highlights (list de 3 a 5 strings, cada max 150 chars), "
        f"attention_items (list de 0 a 5 strings, cada max 150 chars), "
        f"overall_assessment (str, max 400 chars).\n\n"
        f"Idioma da resposta: {language}\n"
        f"Perfil comercial: {_sanitize(profile_name, 100)}\n"
        f"Resumo quantitativo: {job_summary}\n"
        f"Resumo de problemas: {issues_summary}\n"
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
        f"esperadas pelo sistema. Responda em JSON estricto com os campos:\n"
        f"suggestions (list de objetos com: detected_column, suggested_mapping ou null, "
        f"confidence (HIGH|MEDIUM|LOW), rationale max 200 chars),\n"
        f"unmapped_expected (list de strings das colunas esperadas sem correspondência),\n"
        f"disclaimer (string fixa: 'Sugestões geradas por IA. Reveja e confirme antes "
        f"de aplicar o mapeamento.').\n\n"
        f"Idioma da resposta: {language}\n"
        f"Colunas detetadas no ficheiro: {detected_clean}\n"
        f"Colunas esperadas pelo perfil: {expected_clean}\n"
        f"IMPORTANTE: São apenas sugestões. O engine determinístico valida antes de aplicar."
    )


# ---------------------------------------------------------------------------
# Core call helper with structured output
# ---------------------------------------------------------------------------


def _call_gemini_json(prompt: str) -> dict[str, Any] | None:
    """Chama o Gemini com response_mime_type JSON.

    Retorna dict parseado ou None se a chamada falhar.
    GUARDRAIL: Nunca propaga excepções ao router — usa fallback.
    """
    try:
        import json
        from google.genai import types  # type: ignore[import-untyped]

        client = _get_client()
        # thinking_budget=0: modelos 2.5+ gastam tokens de thinking e com
        # max_output_tokens baixo truncavam o JSON → fallback "IA indisponível".
        config_kwargs: dict[str, Any] = {
            "system_instruction": _SYSTEM_INSTRUCTIONS,
            "response_mime_type": "application/json",
            "temperature": 0.2,
            "max_output_tokens": 2048,
        }
        if hasattr(types, "ThinkingConfig"):
            config_kwargs["thinking_config"] = types.ThinkingConfig(thinking_budget=0)

        response = client.models.generate_content(
            model=_MODEL,
            contents=prompt,
            config=types.GenerateContentConfig(**config_kwargs),
        )
        raw = response.text
        if not raw:
            logger.warning("Gemini retornou resposta vazia.")
            return None
        return json.loads(raw)
    except Exception as exc:  # noqa: BLE001
        logger.warning("Chamada ao Gemini falhou: %s", exc)
        return None


# ---------------------------------------------------------------------------
# Fallback builders (determinísticos — sem IA)
# ---------------------------------------------------------------------------


def _fallback_explanation(
    issue_code: str, issue_message: str, severity: str
) -> dict[str, Any]:
    """Fallback determinístico para explain-issue quando Gemini está indisponível."""
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
    """Fallback determinístico para summary quando Gemini está indisponível."""
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
        "attention_items": [f"{blocked} bloqueios requerem revisão."] if blocked else [],
        "overall_assessment": (
            "Resumo gerado localmente (assistência de IA temporariamente indisponível)."
        ),
    }


def _fallback_column_mapping(
    detected: list[str], expected: list[str]
) -> dict[str, Any]:
    """Fallback determinístico para suggest-columns quando Gemini está indisponível."""
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


# ---------------------------------------------------------------------------
# Public service functions
# ---------------------------------------------------------------------------


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
        (data_dict, fallback_used): data_dict conforme AnomalyExplanation;
        fallback_used=True se usámos o fallback determinístico.
    """
    cache_key = f"{job_id}:{issue_code}:{language}"
    if job_id and cache_key in _explain_cache:
        return _explain_cache[cache_key], False

    prompt = _build_explain_prompt(
        issue_code, issue_message, severity, context, language
    )
    result = _call_gemini_json(prompt)

    if result and all(
        k in result
        for k in ("title", "plain_explanation", "likely_cause", "suggested_action", "is_blocker")
    ):
        # Enforce is_blocker to match severity (deterministic override)
        result["is_blocker"] = severity == "BLOCKER"
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
    """Gera resumo executivo assistivo de um processamento.

    Returns:
        (data_dict, fallback_used)
    """
    prompt = _build_summary_prompt(job_summary, issues_summary, profile_name, language)
    result = _call_gemini_json(prompt)

    if result and all(
        k in result
        for k in ("headline", "highlights", "overall_assessment")
    ):
        # Garantir que highlights tem no mínimo 1 item
        if not result.get("highlights"):
            result["highlights"] = ["Processamento analisado."]
        result.setdefault("attention_items", [])
        return result, False

    return _fallback_summary(job_summary), True


def suggest_column_mapping(
    detected_columns: list[str],
    expected_columns: list[str],
    language: str = "pt",
) -> tuple[dict[str, Any], bool]:
    """Sugere mapeamento de colunas desconhecidas usando Gemini.

    GUARDRAIL: Retorna apenas sugestões — o engine determinístico
    valida e confirma antes de aplicar qualquer mapeamento.

    Returns:
        (data_dict, fallback_used)
    """
    prompt = _build_column_mapping_prompt(detected_columns, expected_columns, language)
    result = _call_gemini_json(prompt)

    if result and "suggestions" in result:
        result.setdefault("unmapped_expected", [])
        result.setdefault(
            "disclaimer",
            "Sugestões geradas por IA. Reveja e confirme antes de aplicar o mapeamento.",
        )
        return result, False

    return _fallback_column_mapping(detected_columns, expected_columns), True
