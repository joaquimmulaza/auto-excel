# Backlog Orquestrado — MVP

## Ordem de execução

A ordem abaixo foi escolhida para reduzir retrabalho e permitir paralelismo controlado.

### Fase 0 — Fundação

**A00** Auditoria do repositório e baseline.  
**A01** Criar arquitetura de pastas e documentação operacional.  
**A02** Configurar CI, lint, typecheck e testes vazios.

### Fase 1 — Domain Engine

**A10** Extrair normalização de referências com TDD.  
**A11** Extrair parser/normalização de preços com TDD.  
**A12** Extrair regras de stock/preço com TDD.  
**A13** Extrair price guard com TDD.  
**A14** Criar `process_price_table()` sem CLI.  
**A15** Criar adapters de input/profile para o cenário atual Samsung→Mano.  
**A16** Paridade com o comportamento conhecido do `auto-excel` através de fixtures.

### Fase 2 — Database/Auth

**A20** Criar schema Supabase + migrations.  
**A21** Auth + roles.  
**A22** Storage + metadata/hash.  
**A23** Audit logs.

### Fase 3 — API

**A30** FastAPI skeleton.  
**A31** Jobs/upload.  
**A32** Validation/preview.  
**A33** Approval/process.  
**A34** History/download.  
**A35** Error handling/idempotency.

### Fase 4 — UI/UX Stitch

**A40** Design system Stitch.  
**A41** Dashboard.  
**A42** Novo processamento.  
**A43** Review/diff.  
**A44** Job detail/history.

### Fase 5 — Frontend

**A50** Next.js shell/auth.  
**A51** Dashboard.  
**A52** Upload flow.  
**A53** Validation/review.  
**A54** Approval/history/download.  
**A55** Loading/error/empty/accessibility.

### Fase 6 — Gemini

**A60** AI service backend.  
**A61** Explain issue.  
**A62** Summary.  
**A63** Suggest column mapping.

### Fase 7 — Integração e Demo

**A70** WooCommerce adapter interface (feature flag off).  
**A71** Export adapters por profile.  
**A72** Fixtures de demonstração.  
**A73** E2E completo.  
**A74** Security hardening.  
**A75** Deploy MVP.  
**A76** Demo script para Diretor/Comercial.

## Paralelismo permitido

Depois da Fase 1, tarefas independentes podem correr em paralelo, desde que não alterem o mesmo contrato sem ADR.

Exemplo:

```text
Backend API ─────┐
                 ├→ Integration QA
Frontend Stitch ─┤
Database ────────┘
```

## Handoff obrigatório

Cada agente entrega obrigatoriamente no formato canónico:

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: <id>
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
```
