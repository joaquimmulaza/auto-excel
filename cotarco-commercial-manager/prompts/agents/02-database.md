# Agent Prompt A20-A23 — Supabase Schema + Auth + Audit

## Gate obrigatório (antes de implementar)

1. Ler `context.md`, `agents.md`, `docs/data-architecture.md`, `docs/routes-api.md` (sob `cotarco-commercial-manager/`).
2. Graphify MCP recon em `joaquimmulaza/auto-excel` para modelos/repos existentes e impacto (`query_graph`, `graphify_impact`).
3. Skills só da matriz §11: `security-best-practices` (Backend).
4. TDD / testes de integração antes de cada migration ou use case de repository.
5. Entregar handoff de 9 campos (`agents.md` §7).

## Missão

Criar migrations Supabase/PostgreSQL, roles/auth mapping, storage metadata e audit logging.

## TDD

Antes de cada migration/repository use case, criar testes de integração contra DB de teste ou estratégia de isolamento aprovada.

## Implementar

1. enums;
2. users/profile/rules/templates;
3. jobs/files/items/issues;
4. approval/audit/history;
5. integrations/AI requests;
6. índices;
7. constraints;
8. RLS/policies necessárias;
9. seed mínimo de perfis sem regras inventadas;
10. `.env.example`.

## Guardrails

- nenhum secret;
- migration reversível quando possível;
- não guardar binário em DB;
- não guardar credenciais de integração em plaintext.

## Seed inicial

Somente perfis conhecidos como placeholders configuráveis:

MANO, WOOCOMMERCE, BFA, KERO, SIAC, RESELLERS, OTHER.

Não adicionar fórmulas de parceiros sem requisitos aprovados.

## Entrega

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: A20-A23
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
```
