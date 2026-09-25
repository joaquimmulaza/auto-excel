# Agent Prompt A60-A63 — Gemini Assist

Leia `context.md`, `agents.md`, `docs/stack-and-guardrails.md` e `docs/routes-api.md`.

## Missão

Adicionar uma camada de assistência Gemini no backend.

## Funcionalidades MVP

1. explicar issue;
2. resumir job;
3. analisar anomalias;
4. sugerir mapeamento de coluna.

## Guardrails

- nunca expor API key ao browser;
- nunca permitir que a resposta altere diretamente o domínio;
- JSON estruturado com schema;
- timeout;
- retry limitado;
- rate limit;
- logs sem conteúdo sensível desnecessário;
- resposta claramente rotulada como IA.

## Contrato

Criar modelos Pydantic para saída. Validar sempre a resposta antes de apresentar.

## Fallback

Quando Gemini estiver indisponível, o sistema continua operacional sem IA.
