# Agent Prompt A70-A76 — Adapters, E2E, Security, Demo

## Gate obrigatório (antes de implementar)

1. Ler todos os docs, especialmente `context.md`, `agents.md`, `docs/application-flows.md`, `docs/testing-tdd.md` (sob `cotarco-commercial-manager/`).
2. Graphify MCP recon em `joaquimmulaza/auto-excel` para adapters, fluxos e testes (`query_graph`, `graphify_tests_for`, `graphify_impact`).
3. Skills só da matriz §11: `playwright-skill`, `core-web-vitals`.
4. E2E + security checks com evidência de terminal.
5. Entregar handoff de 9 campos (`agents.md` §7).

## Missão

Preparar o MVP demonstrável com adapters, fixtures, E2E, segurança e deployment.

## Implementar

### 1. Export adapters

Criar `ExcelExportAdapter` por profile sem inventar regras de parceiros.

### 2. WooCommerce

Criar interface realista e configuração/health check atrás de feature flag.

Não executar escrita em produção sem credenciais/test environment e aprovação humana.

### 3. E2E

Executar os 4 cenários críticos definidos em `docs/testing-tdd.md`.

### 4. Segurança

Verificar:

- secrets;
- upload validation;
- authorization;
- RLS;
- CORS;
- rate limit IA;
- logs;
- error leakage.

### 5. Demo data

Criar dados sintéticos:

- uma tabela válida;
- uma com blockers;
- uma com alterações de preço;
- uma com novos produtos.

### 6. Demo script

Criar uma sequência de 5–10 minutos:

`Comercial upload → validação → correção → Operador review → aprovação → output → histórico → IA`.

## Definition of Done

Tudo documentado, CI verde e MVP reproduzível por outro desenvolvedor.

## Entrega

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: A70-A76
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
```
