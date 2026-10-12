# Agent Prompt A30-A35 — FastAPI

## Gate obrigatório (antes de implementar)

1. Ler `context.md`, `agents.md`, `docs/routes-api.md`, `docs/testing-tdd.md` (sob `cotarco-commercial-manager/`).
2. Graphify MCP recon em `joaquimmulaza/auto-excel`: rotas/use cases existentes (`query_graph`, `graphify_find`, `graphify_tests_for`).
3. Skills da matriz §11 + protocolo §5.3:
   - `.agents/skills/supabase/SKILL.md` (Auth/JWT/SSR, Storage, clients)
   - `.agents/skills/supabase-postgres-best-practices/SKILL.md` (quando a rota toca SQL/repos)
   - `security-best-practices`, `tlc-spec-driven`
4. TDD por endpoint crítico (sucesso + erros).
5. Entregar handoff canónico (`agents.md` §7) incluindo `SUPABASE_SKILLS_USED`.

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

## Entrega

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: A30-A35
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
UI_SKILLS_SELECTED: n/a
SUPABASE_SKILLS_USED: supabase,supabase-postgres-best-practices
```
