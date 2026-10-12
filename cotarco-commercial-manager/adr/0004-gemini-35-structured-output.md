# ADR 0004 — Gemini 3.5-flash-lite + structured output

## Status

Aceite (2026-10-11)

## Contexto

O serviço usava `gemini-2.5-flash` com `thinking_budget=0` e JSON sem schema,
o que truncava respostas e dificultava validação.

## Decisão

- Default `GEMINI_MODEL=gemini-3.5-flash-lite`.
- Override documentado: `gemini-3.6-flash` | `gemini-3.8-flash`.
- `thinking_level=MINIMAL` (fallback `LOW` / `thinking_budget=0`).
- `response_json_schema` gerado a partir dos schemas Pydantic em `schemas/ai.py`.
- Revalidação Pydantic no serviço; inválido → fallback determinístico.
- Router AI nunca devolve 500 por JSON inválido; enriquece contexto no servidor.
- Sem function calling, embeddings ou envio de Excel completo ao modelo neste passo.

## Consequências

- Frontend consome apenas API (`/ai/summary`, `/ai/suggest-columns`, `/ai/explain-issue`).
- Badge “Assistido por IA” / `fallback_used` obrigatório na UI.
- Motor Python continua autoridade para preços/stock/aprovação.
