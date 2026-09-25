# Agent Prompt A30-A35 — FastAPI

Leia `context.md`, `agents.md`, `docs/routes-api.md`, `docs/testing-tdd.md`.

## Missão

Criar a API REST `/api/v1` que orquestra os casos de uso do domain engine.

## Implementar por ordem

1. FastAPI app + settings;
2. auth middleware/dependencies;
3. profiles;
4. jobs;
5. upload/storage;
6. validation/summary/items/issues;
7. approval/process;
8. history/download;
9. audit;
10. error envelope;
11. idempotency.

## Regra

A rota não contém lógica de negócio complexa. Rota → use case → domain/service → repository/adapter.

## Testes

Para cada endpoint crítico:

- sucesso;
- 401;
- 403;
- 404;
- 409;
- 422;
- falha de dependency.

## Não implementar

WooCommerce mutation real, Mano API, Gemini real. Criar interfaces/mocks apenas quando a etapa exigir.
