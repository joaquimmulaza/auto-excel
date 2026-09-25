# Agent Prompt A20-A23 — Supabase Schema + Auth + Audit

Leia `context.md`, `agents.md`, `docs/data-architecture.md`, `docs/routes-api.md`.

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
