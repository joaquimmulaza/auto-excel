"""Pydantic v2 schemas for Gemini AI Assistive endpoints.

GUARDRAIL (Regra de Ouro 1): Gemini é ASSISTIVO.
- Nenhum schema aqui define preços, stocks ou decisões de negócio.
- Respostas de IA são claramente marcadas como assistivas (is_ai_generated=True).
- Modelos são read-only pelo frontend; never write-back to domain.

GUARDRAIL (Regra de Ouro 3): Todos os outputs seguem schemas Pydantic v2 estrictos.
Qualquer resposta da API Gemini que não corresponda aos schemas resulta em fallback
determinístico — nunca em crash nem em resposta não estruturada ao cliente.
"""
from __future__ import annotations

from enum import Enum
from typing import Any

from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class IssueSeverity(str, Enum):
    """Espelho do severity do domínio para o contexto de IA."""
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    BLOCKER = "BLOCKER"


# ---------------------------------------------------------------------------
# Input schemas (request bodies)
# ---------------------------------------------------------------------------


class ExplainIssueRequest(BaseModel):
    """Payload para POST /jobs/{id}/ai/explain-issue.

    O frontend envia o código de erro e informações de contexto;
    o backend enriquece com dados do job antes de chamar o Gemini.
    """

    issue_code: str = Field(
        ...,
        description="Código determinístico do erro (ex: PRICE_VARIATION_BLOCKED).",
        examples=["PRICE_VARIATION_BLOCKED"],
    )
    issue_message: str = Field(
        ...,
        description="Mensagem original do erro de validação.",
        max_length=500,
    )
    severity: IssueSeverity = Field(
        ...,
        description="Severidade do problema.",
    )
    context: dict[str, Any] = Field(
        default_factory=dict,
        description="Contexto adicional (referência, valores anteriores/novos, etc.).",
    )
    language: str = Field(
        default="pt",
        description="Idioma preferido da resposta (ISO 639-1).",
        pattern=r"^[a-z]{2}$",
    )


class SummaryRequest(BaseModel):
    """Payload para POST /jobs/{id}/ai/summary.

    Envia os dados quantitativos do job para que o Gemini gere
    um resumo executivo em linguagem natural.
    """

    language: str = Field(
        default="pt",
        description="Idioma preferido da resposta (ISO 639-1).",
        pattern=r"^[a-z]{2}$",
    )


class SuggestColumnsRequest(BaseModel):
    """Payload para POST /jobs/{id}/ai/suggest-columns.

    Envia cabeçalhos desconhecidos para que o Gemini sugira
    o mapeamento para as colunas esperadas pelo perfil.

    GUARDRAIL: A sugestão é apenas sugestão — o mapeamento final
    é validado deterministicamente pelo engine antes de ser aplicado.
    """

    detected_columns: list[str] = Field(
        ...,
        description="Cabeçalhos detetados no ficheiro submetido.",
        min_length=1,
        max_length=50,
    )
    expected_columns: list[str] = Field(
        ...,
        description="Colunas esperadas pelo perfil comercial.",
        min_length=1,
        max_length=50,
    )
    language: str = Field(
        default="pt",
        description="Idioma preferido da resposta (ISO 639-1).",
        pattern=r"^[a-z]{2}$",
    )


# ---------------------------------------------------------------------------
# AI output schemas (structured outputs from Gemini)
# ---------------------------------------------------------------------------


class AnomalyExplanation(BaseModel):
    """Explicação assistiva de uma anomalia/erro de validação.

    Gerado pelo Gemini em resposta ao endpoint explain-issue.
    Nunca contém uma decisão de negócio — apenas contextualização.
    """

    title: str = Field(
        ...,
        description="Título curto e claro do problema.",
        max_length=120,
    )
    plain_explanation: str = Field(
        ...,
        description="Explicação em linguagem não técnica para o utilizador Comercial.",
        max_length=800,
    )
    likely_cause: str = Field(
        ...,
        description="Causa provável do problema com base no código de erro.",
        max_length=400,
    )
    suggested_action: str = Field(
        ...,
        description=(
            "Ação sugerida para resolver o problema. "
            "NUNCA inclui decisão de preço ou stock."
        ),
        max_length=400,
    )
    is_blocker: bool = Field(
        ...,
        description="True quando o severity original é BLOCKER.",
    )


class ExecutiveSummary(BaseModel):
    """Resumo executivo assistivo de um processamento.

    Gerado pelo Gemini com base nos dados quantitativos do job.
    Deve contextualizar os números, não os substituir.
    """

    headline: str = Field(
        ...,
        description="Frase de abertura com o resultado geral do processamento.",
        max_length=200,
    )
    highlights: list[str] = Field(
        ...,
        description="3–5 pontos-chave sobre o processamento.",
        min_length=1,
        max_length=5,
    )
    attention_items: list[str] = Field(
        default_factory=list,
        description="Itens que merecem atenção do Operador (sem decisão de negócio).",
        max_length=5,
    )
    overall_assessment: str = Field(
        ...,
        description=(
            "Avaliação qualitativa do estado do processamento. "
            "Ex: 'Processamento saudável com anomalias menores.'"
        ),
        max_length=400,
    )


class ColumnSuggestion(BaseModel):
    """Sugestão de mapeamento para uma coluna desconhecida."""

    detected_column: str = Field(..., description="Nome da coluna detetada no ficheiro.")
    suggested_mapping: str | None = Field(
        None,
        description="Nome da coluna esperada mais provável. None se sem correspondência.",
    )
    confidence: str = Field(
        ...,
        description="Nível de confiança: HIGH | MEDIUM | LOW.",
        pattern=r"^(HIGH|MEDIUM|LOW)$",
    )
    rationale: str = Field(
        ...,
        description="Breve justificação da sugestão.",
        max_length=200,
    )


class ColumnMapping(BaseModel):
    """Resultado completo de sugestão de mapeamento de colunas.

    GUARDRAIL: Sugestões são apenas sugestões. O engine determinístico
    valida e confirma qualquer mapeamento antes de processar.
    """

    suggestions: list[ColumnSuggestion] = Field(
        ...,
        description="Lista de sugestões por coluna detetada.",
    )
    unmapped_expected: list[str] = Field(
        default_factory=list,
        description="Colunas esperadas sem correspondência detetada.",
    )
    disclaimer: str = Field(
        default=(
            "Sugestões geradas por IA. "
            "Reveja e confirme antes de aplicar o mapeamento."
        ),
        description="Aviso obrigatório de que a sugestão é assistiva.",
    )


# ---------------------------------------------------------------------------
# Generic AI response wrapper
# ---------------------------------------------------------------------------


class AIResponse(BaseModel):
    """Envelope genérico para todas as respostas de IA assistiva.

    O campo ``is_ai_generated`` DEVE sempre ser True nos endpoints de IA —
    é o sinal para o frontend exibir o badge 'Assistido por IA'.
    ``fallback_used`` indica que o Gemini não respondeu e foi usado
    um fallback determinístico.
    """

    is_ai_generated: bool = Field(
        default=True,
        description="Sempre True — sinaliza ao frontend que é conteúdo de IA.",
    )
    fallback_used: bool = Field(
        default=False,
        description="True quando a resposta de IA falhou e usámos o fallback local.",
    )
    data: AnomalyExplanation | ExecutiveSummary | ColumnMapping = Field(
        ...,
        description="Payload estruturado específico do endpoint.",
    )

    model_config = {"arbitrary_types_allowed": True}
