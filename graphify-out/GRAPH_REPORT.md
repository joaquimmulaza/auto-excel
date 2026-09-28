# Graph Report - up_prices  (2026-09-28)

## Corpus Check
- 132 files · ~80,273 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 5 file(s) not represented in the graph (top: (none) 3, .example 1, .css 1)

## Summary
- 1580 nodes · 2542 edges · 125 communities (96 shown, 29 thin omitted)
- Extraction: 95% EXTRACTED · 5% INFERRED · 0% AMBIGUOUS · INFERRED: 122 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `eca758d5`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- Graphify
- test_normalization.py
- process_price_table
- domain/__init__.py
- app/main.py
- 3. Tabelas
- domain/models.py
- JobTable.tsx
- 🟠 P1 — HIGH (Resolver antes das fases de DB/API)
- engine.py
- ValidationIssue
- v1/processing.py
- CONTEXT.md — Cotarco Commercial Manager
- 4. Requisitos funcionais
- Stack Tecnológica & Regras de Ouro (Tech Stack & Guardrails)
- Suite de Testes Automatizados — TDD First
- 7. Proposed Remediation Steps (DO NOT EXECUTE — Reference Only)
- UI/UX Wireframes + Design System Base
- MASTER ORCHESTRATOR — Cotarco Commercial Manager
- Matriz de Rotas e APIs
- Ordem de execução
- AGENTS.md — Operating Rules for AI Coding Agents
- Implementar
- Fluxos da Aplicação
- 4. Discrepancies Between Rules, Workflows, Setup Docs, and Reality
- Agent Prompt A00 — Bootstrap + Audit
- Agent Prompt A10-A16 — Domain Engine TDD First
- Agent Prompt A50-A55 — Frontend after Stitch Approval
- Stitch Prompt — Design System CCM
- Cotarco Commercial Manager — Project Blueprint
- ADR-0002 — Supabase no MVP
- Referências técnicas consultadas — 23/09/2026
- Agent Prompt A20-A23 — Supabase Schema + Auth + Audit
- Agent Prompt A30-A35 — FastAPI
- Agent Prompt A60-A63 — Gemini Assist
- ADR-0001 — Arquitetura inicial
- Prompt Orchestration
- UI Skills MCP & Workflow Integration
- 01-dashboard.md
- 02-new-job.md
- 03-review-diff.md
- 🟢 P3 — LOW (Housekeeping — antes do MVP Demo)
- Rules Auditor — Audit Report
- Documentation Audit Report — Cotarco Commercial Manager
- Cotarco Commercial Manager — Remediation Cycle 1 Result
- Cotarco Commercial Manager — Remediation Plan
- 🟡 P2 — MEDIUM (Resolver antes das fases de UI)
- 🔴 P0 — CRITICAL (Must resolve before implementation begins)
- fixture
- cn
- app/__init__.py
- v1/profiles.py
- backend/__init__.py
- tests/__init__.py
- JobRepository
- ProfileRepository
- session
- session.py
- Fase 2 — Database & Supabase (Debriefing & Intelligence)
- test_schema.py
- Ficheiros Criados
- test_jobs_api.py
- test_processing_api.py
- _make_job
- limpar_preco
- v1/ai.py
- Detailed Findings
- Detailed Findings
- CATEGORY D — Stack Incompatibilities and Contradictions
- react
- _UserClient
- Actionable Harmonization Roadmap
- CATEGORY A — Dead / Incorrect Glob Paths
- CATEGORY B — Git / Commit Workflow Conflicts
- compilerOptions
- v1/jobs.py
- api.ts
- Fase 6 - E2E Demo e Ajustes da Inteligência Artificial
- package.json
- [id]/page.tsx
- @playwright/test
- ProcessSummary
- ValidationIssueList.tsx
- test_ai_api.py
- dependencies
- conftest.py
- Fase 4 — Frontend & Google Stitch Loop
- normalize_col
- devDependencies
- scripts
- Fase 3 — FastAPI & Endpoints
- next.config.mjs
- next-env.d.ts
- TestSuggestColumns
- JobItemOrm
- schemas/ai.py
- patch
- phase-5-gemini.md
- errors.py
- ping_database
- TestSeedProfilesShape
- AuditLogOrm
- schemas/processing.py
- TestProfilesEndpoint
- alert.tsx
- .test_rate_limit_triggers_429
- tailwind.config.ts
- UUID
- Session
- _bearer
- DbDep
- Depends
- JobRepository
- post
- UserDep

## God Nodes (most connected - your core abstractions)
1. `JobRepository` - 48 edges
2. `cn()` - 42 edges
3. `process_price_table()` - 41 edges
4. `session()` - 39 edges
5. `ProfileRepository` - 27 edges
6. `Stack Tecnológica & Regras de Ouro (Tech Stack & Guardrails)` - 22 edges
7. `react` - 21 edges
8. `ProcessingJobOrm` - 20 edges
9. `3. Tabelas` - 20 edges
10. `PriceRule` - 19 edges

## Surprising Connections (you probably didn't know these)
- `4. Gotcha: `metadata` Reservado pelo SQLAlchemy Declarative` --references--> `AuditLogOrm`  [INFERRED]
  .notebook/phase-2-database.md → backend/app/infra/db/models.py
- `1. `test_commercial_job_submission_and_diff.spec.ts`` --references--> `DiffViewer()`  [INFERRED]
  .notebook/phase-6-e2e-demo.md → frontend/src/components/jobs/DiffViewer.tsx
- `1. SQLite in-memory com múltiplas conexões` --references--> `get_db()`  [INFERRED]
  .notebook/phase-3-api.md → backend/app/api/deps.py
- `Ficheiros Criados` --references--> `get_db()`  [INFERRED]
  .notebook/phase-3-api.md → backend/app/api/deps.py
- `Ficheiros Criados` --references--> `CurrentUser`  [INFERRED]
  .notebook/phase-3-api.md → backend/app/api/deps.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Outputs and Commands** — graphify, graphify_out_graph_html, graphify_out_graph_report_md, graphify_out_graph_json, graphify_query_command, graphify_path_command, graphify_explain_command, graphify_update_command [EXTRACTED 1.00]
- **Graphify Setup Components** — graphify, uv_tool, agents_rules_graphify_md, agents_workflows_graphify_md, git_hooks, gitattributes, graphifyignore [EXTRACTED 1.00]
- **Price and Stock Updater Workflow** — cotarco_samsung_preco_atualizado_xlsx, mano_preco_desatualizado_xlsx, main, mano_preco_atualizado_final_xlsx, log_decisao_samsung_xlsx, deteccao_automatica_cabecalho, mapeamento_tolerante_colunas, saneamento_avancado_dados, regras_negocio_integradas, log_decisao_transparente [EXTRACTED 1.00]

## Communities (125 total, 29 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (45): argparse, Ativação/Inativação, Cotarco-Samsung-preco-atualizado.xlsx, Deteção Automática de Cabeçalho, Filtragem de Segurança, io, Limpeza de Preços, LOG_DECISAO_SAMSUNG.xlsx (+37 more)

### Community 1 - "Graphify"
Cohesion: 0.12
Nodes (16): .agents/rules/graphify.md, .agents/workflows/graphify.md, Git Hooks, .gitattributes, Graphify, graphify explain, graphify-out/graph.html, graphify-out/graph.json (+8 more)

### Community 2 - "test_normalization.py"
Cohesion: 0.15
Nodes (10): calcular_variacao(), Safely calculates relative price variation without division by zero. Returns:…, Sanitizes catalog references deterministically. Retains strictly uppercase…, ultra_clean(), Unit tests for domain normalization and cleaning utilities., Tests for ultra_clean reference sanitization., Tests for calcular_variacao calculation and zero-division protection., TestCalcularVariacao (+2 more)

### Community 3 - "process_price_table"
Cohesion: 0.12
Nodes (10): process_price_table(), Processes source supplier/marketplace table against a target catalog…, Verifies that duplicate references in source records are caught and blocked., TestDuplicateReferences, Engine should not mutate the caller's input lists directly., Core domain processor test suite., TestDomainEngine, create_profile() (+2 more)

### Community 4 - "domain/__init__.py"
Cohesion: 0.14
Nodes (18): Domain layer package for Cotarco Commercial Manager. Exports domain entities,…, Domain normalization and data cleaning utilities for Cotarco Commercial…, calculate_price_variation(), clean_price_value(), evaluate_new_product_eligibility(), evaluate_price_guard(), evaluate_stock_activation(), normalize_reference() (+10 more)

### Community 5 - "app/main.py"
Cohesion: 0.14
Nodes (13): Aggregator for all v1 routes., health_check(), lifespan(), get, FastAPI application entry point for Cotarco Commercial Manager. GUARDRAIL: This…, Eagerly initialise the database on every startup / hot-reload. The session…, FastAPI, fastapi_exceptions (+5 more)

### Community 6 - "3. Tabelas"
Cohesion: 0.07
Nodes (28): 1. Princípios, 2. Modelo lógico, 3. Tabelas, 4. Enums mínimos, 5. Índices importantes, 6. RLS / autorização, 7. Integridade de ficheiros, 8. Retenção (+20 more)

### Community 7 - "domain/models.py"
Cohesion: 0.11
Nodes (33): CommercialProfile, DecisionCode, IssueSeverity, PriceRule, Product, Domain models and contracts for Cotarco Commercial Manager. All models are…, Canonical domain product entity representing a commercial catalog item., Severity levels for validation and business rule issues. (+25 more)

### Community 8 - "JobTable.tsx"
Cohesion: 0.22
Nodes (15): DiffViewer(), FilterType, Badge(), BadgeProps, badgeVariants, Table, TableBody, TableCaption (+7 more)

### Community 9 - "🟠 P1 — HIGH (Resolver antes das fases de DB/API)"
Cohesion: 0.22
Nodes (9): 🟠 P1 — HIGH (Resolver antes das fases de DB/API), REM-011, REM-012, REM-013, REM-014, REM-015, REM-016, REM-017 (+1 more)

### Community 10 - "engine.py"
Cohesion: 0.12
Nodes (14): Domain processing engine for Cotarco Commercial Manager. Fully deterministic,…, Class wrapper providing a stateless engine processor instance., Executes table processing using the configured CommercialProfile., TableProcessor, JobItemResult, ProcessResult, Detailed evaluation and decision outcome for a single catalog reference item., Aggregate processing output containing items, issues, summary, and final… (+6 more)

### Community 11 - "ValidationIssue"
Cohesion: 0.17
Nodes (11): Structured issue or violation emitted during validation or processing., Indicates whether this issue prevents automated execution., ValidationIssue, 1.1 Bug do Preço Zero (Passo 4 do Legado), 1.2 Sobrescrita Silenciosa de Duplicados (Dicionário Zip), 1.3 Price Guard Hardcoded vs Dinâmico, 1.4 Higienização e Normalização Determinística, 1. Bugs e Gotchas Identificados no Legado & Soluções Aplicadas (+3 more)

### Community 12 - "v1/processing.py"
Cohesion: 0.25
Nodes (17): _check_access(), get_issues(), get_items(), _get_job_or_404(), get_summary(), DbDep, get, JobRepository (+9 more)

### Community 13 - "CONTEXT.md — Cotarco Commercial Manager"
Cohesion: 0.08
Nodes (24): 10. Critério geral de sucesso do MVP, 1. O que estamos a construir, 2. Papéis, 3. Domínio, 4. Motor existente, 5. Regras de negócio conhecidas, 6. IA, 7. Stack alvo (+16 more)

### Community 14 - "4. Requisitos funcionais"
Cohesion: 0.05
Nodes (42): 1. Visão do produto, 2. Objetivos, 3. Personas, 4. Requisitos funcionais, 5. Requisitos não funcionais, 6. Regras ainda pendentes de levantamento de negócio, 7. Fora do escopo do MVP, 8. MVP Definition of Done (+34 more)

### Community 15 - "Stack Tecnológica & Regras de Ouro (Tech Stack & Guardrails)"
Cohesion: 0.09
Nodes (22): 10. Guardrail #8 — Inputs são não confiáveis, 11. Guardrail #9 — Não sobrescrever originais, 12. Guardrail #10 — Auditoria, 13. Guardrail #11 — Erros determinísticos, 14. Guardrail #12 — TDD first, 15. Guardrail #13 — Design by Stitch, implementation by codebase, 16. Guardrail #14 — Feature flags, 17. Guardrail #15 — Observabilidade mínima (+14 more)

### Community 16 - "Suite de Testes Automatizados — TDD First"
Cohesion: 0.06
Nodes (31): 10. CI quality gates, 11. TDD workflow por tarefa, 1. Filosofia, 2. Backend, 3. Testes de casos de uso, 4. API tests, 5. Frontend, 6. E2E com Playwright (+23 more)

### Community 17 - "7. Proposed Remediation Steps (DO NOT EXECUTE — Reference Only)"
Cohesion: 0.04
Nodes (47): 1. Executive Summary, 2.1 Git Status, 2.2 Commit History, 2.3 Total Tracked File Inventory Summary, 2. Current Git Status & Repository Hygiene Overview, 3.1 Scope, 3.2 Packages Tracked, 3.3 Sub-directory Distribution (playwright-core alone spans) (+39 more)

### Community 18 - "UI/UX Wireframes + Design System Base"
Cohesion: 0.11
Nodes (17): 10. Wireframe — Review/Diff, 11. Wireframe — Detalhe de processamento, 12. Estados obrigatórios, 13. Design de tabelas, 14. Acessibilidade, 15. Stitch Workflow, 16. Critérios de aprovação visual, 1. Direção visual (+9 more)

### Community 19 - "MASTER ORCHESTRATOR — Cotarco Commercial Manager"
Cohesion: 0.12
Nodes (16): Comando de encerramento do ciclo, Decisão sobre IA, Fonte de verdade, Handoff format, MASTER ORCHESTRATOR — Cotarco Commercial Manager, Papel, Política de delegação, Política de demonstração (+8 more)

### Community 20 - "Matriz de Rotas e APIs"
Cohesion: 0.12
Nodes (15): 10. Contratos-chave, 11. API adapter para WooCommerce — futuro, 1. Convenções, 2. Rotas Frontend, 3. Auth, 4. Profiles, 5. Jobs, 6. Histórico (+7 more)

### Community 21 - "Ordem de execução"
Cohesion: 0.15
Nodes (12): Backlog Orquestrado — MVP, Fase 0 — Fundação, Fase 1 — Domain Engine, Fase 2 — Database/Auth, Fase 3 — API, Fase 4 — UI/UX Stitch, Fase 5 — Frontend, Fase 6 — Gemini (+4 more)

### Community 22 - "AGENTS.md — Operating Rules for AI Coding Agents"
Cohesion: 0.12
Nodes (16): 0. Ordem obrigatória de leitura, 10. Graphify MCP e CLI — Navegação e Manutenção da Codebase, 11. Matriz de Atribuição de Skills (Isolamento por Escopo), 1. Princípio central, 2. Não fazer, 3. Regras de arquitetura, 4. Regra de alterações, 5. Stitch MCP — protocolo obrigatório para UI (+8 more)

### Community 23 - "Implementar"
Cohesion: 0.18
Nodes (10): 1. Export adapters, 2. WooCommerce, 3. E2E, 4. Segurança, 5. Demo data, 6. Demo script, Agent Prompt A70-A76 — Adapters, E2E, Security, Demo, Definition of Done (+2 more)

### Community 24 - "Fluxos da Aplicação"
Cohesion: 0.20
Nodes (9): 1. Fluxo principal — Comercial, 2. Fluxo do Operador, 3. Fluxo de correção, 4. Fluxo de processamento, 5. Fluxo Gemini, 6. Fluxo de perfil configurável, 7. Fluxo WooCommerce futuro, 8. Fluxo Mano (+1 more)

### Community 25 - "4. Discrepancies Between Rules, Workflows, Setup Docs, and Reality"
Cohesion: 0.06
Nodes (34): 1. Executive Summary, 2.1 Configuration & Setup Files, 2.2 MCP Server Configuration, 2.3 Binary / Runtime, 2.4 Git Hooks, 2.5 `graphify-out/` Directory — Full Inventory, 2. Current Graphify Artifacts Inventory, 3.1 ✅ MUST be in git (commit and track) (+26 more)

### Community 26 - "Agent Prompt A00 — Bootstrap + Audit"
Cohesion: 0.22
Nodes (8): Agent Prompt A00 — Bootstrap + Audit, Contexto, Definition of Done, Entrega, Missão, Não fazer, Tarefas, TDD

### Community 27 - "Agent Prompt A10-A16 — Domain Engine TDD First"
Cohesion: 0.22
Nodes (8): Agent Prompt A10-A16 — Domain Engine TDD First, Compatibilidade, Contrato alvo, Definition of Done, Missão, Ordem, Regra, Regras

### Community 28 - "Agent Prompt A50-A55 — Frontend after Stitch Approval"
Cohesion: 0.25
Nodes (7): Agent Prompt A50-A55 — Frontend after Stitch Approval, Missão, Ordem, Regra, Responsividade, Testes, UX

### Community 29 - "Stitch Prompt — Design System CCM"
Cohesion: 0.25
Nodes (7): Branding obrigatório, Componentes, Contexto, QA, Stitch Prompt — Design System CCM, UX, Validação Pré-Stitch Obrigatória (UI Skills & Enhance-Prompt)

### Community 30 - "Cotarco Commercial Manager — Project Blueprint"
Cohesion: 0.25
Nodes (7): Cotarco Commercial Manager — Project Blueprint, Estado do MVP, Estado inicial conhecido, Fonte de contexto principal, Integrações, Objetivo do repositório, Regra de ouro

### Community 31 - "ADR-0002 — Supabase no MVP"
Cohesion: 0.29
Nodes (6): ADR-0002 — Supabase no MVP, Decisão, Limitações reconhecidas, Mitigação, Motivos, Status

### Community 32 - "Referências técnicas consultadas — 23/09/2026"
Cohesion: 0.29
Nodes (6): Gemini, Google Stitch, Nota, Referências técnicas consultadas — 23/09/2026, Supabase, WooCommerce

### Community 33 - "Agent Prompt A20-A23 — Supabase Schema + Auth + Audit"
Cohesion: 0.29
Nodes (6): Agent Prompt A20-A23 — Supabase Schema + Auth + Audit, Guardrails, Implementar, Missão, Seed inicial, TDD

### Community 34 - "Agent Prompt A30-A35 — FastAPI"
Cohesion: 0.29
Nodes (6): Agent Prompt A30-A35 — FastAPI, Implementar por ordem, Missão, Não implementar, Regra, Testes

### Community 35 - "Agent Prompt A60-A63 — Gemini Assist"
Cohesion: 0.29
Nodes (6): Agent Prompt A60-A63 — Gemini Assist, Contrato, Fallback, Funcionalidades MVP, Guardrails, Missão

### Community 36 - "ADR-0001 — Arquitetura inicial"
Cohesion: 0.33
Nodes (5): ADR-0001 — Arquitetura inicial, Consequências, Contexto, Decisão, Status

### Community 37 - "Prompt Orchestration"
Cohesion: 0.40
Nodes (4): Como usar, Orquestrador principal, Prompt Orchestration, Stitch loop

### Community 38 - "UI Skills MCP & Workflow Integration"
Cohesion: 0.40
Nodes (4): Configuration, Mandatory Gates, Overview, UI Skills MCP & Workflow Integration

### Community 42 - "🟢 P3 — LOW (Housekeeping — antes do MVP Demo)"
Cohesion: 0.17
Nodes (12): 🟢 P3 — LOW (Housekeeping — antes do MVP Demo), REM-030, REM-031, REM-032, REM-033, REM-034, REM-035, REM-036 (+4 more)

### Community 43 - "Rules Auditor — Audit Report"
Cohesion: 0.25
Nodes (8): Autonomy vs. Human Approval Conflict Analysis, Conclusion, Executive Summary, Files Audited, Git / Commit Workflow Conflict Analysis, Legacy / Obsolete Patterns Summary, Recommendations Priority Matrix, Rules Auditor — Audit Report

### Community 44 - "Documentation Audit Report — Cotarco Commercial Manager"
Cohesion: 0.20
Nodes (10): ADR Gap Analysis, Current State, Documentation Audit Report — Cotarco Commercial Manager, Executive Summary, Gaps in Precedence, Inventory of Documentation Audited, Observed Implied Hierarchy, Precedence & Hierarchy Assessment (+2 more)

### Community 45 - "Cotarco Commercial Manager — Remediation Cycle 1 Result"
Cohesion: 0.14
Nodes (13): CHECKS, Cotarco Commercial Manager — Remediation Cycle 1 Result, FILES, Files Modified, Files Untracked from Git Tracking (629 files), FIXED (28 Authorized REM-IDs), GIT, GRAPHIFY (+5 more)

### Community 46 - "Cotarco Commercial Manager — Remediation Plan"
Cohesion: 0.29
Nodes (7): 4 ADRs em Falta (Bloqueantes de Implementação), Classification Legend, Cotarco Commercial Manager — Remediation Plan, Executive Summary, Resumo por Categoria, Risk Distribution, Sugestão de Sequência de Remediação

### Community 47 - "🟡 P2 — MEDIUM (Resolver antes das fases de UI)"
Cohesion: 0.17
Nodes (12): 🟡 P2 — MEDIUM (Resolver antes das fases de UI), REM-019, REM-020, REM-021, REM-022, REM-023, REM-024, REM-025 (+4 more)

### Community 48 - "🔴 P0 — CRITICAL (Must resolve before implementation begins)"
Cohesion: 0.18
Nodes (11): 🔴 P0 — CRITICAL (Must resolve before implementation begins), REM-001, REM-002, REM-003, REM-004, REM-005, REM-006, REM-007 (+3 more)

### Community 49 - "fixture"
Cohesion: 0.31
Nodes (9): db_session(), Seed baseline users and profile before each test., seed_db(), session_factory(), fixture, 1. SQLite in-memory com múltiplas conexões, 3. sessionmaker() como context manager, 4. Legacy main.py intacto (+1 more)

### Community 50 - "cn"
Cohesion: 0.13
Nodes (21): Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle, Input, InputProps (+13 more)

### Community 52 - "v1/profiles.py"
Cohesion: 0.23
Nodes (13): get_profile(), list_profiles(), DbDep, get, UserDep, UUID, GET /profiles, GET /profiles/{id}, List all active commercial profiles. Any authenticated user. (+5 more)

### Community 55 - "JobRepository"
Cohesion: 0.09
Nodes (21): PriceHistoryOrm, Structured validation or business rule violation for a job. Aligned with domain…, Immutable price change record — append-only historical ledger.…, ValidationIssueOrm, JobRepository, Session, UUID, Return all items for a job ordered by normalized reference. (+13 more)

### Community 56 - "ProfileRepository"
Cohesion: 0.08
Nodes (22): CommercialProfileOrm, Commercial profile defining channel / destination / rule-set. ``code`` is the…, ProfileRepository, Session, UUID, Persist a new profile rule., Data access layer for ``commercial_profiles`` and ``profile_rules``., Fetch a profile by its UUID primary key. (+14 more)

### Community 57 - "session"
Cohesion: 0.15
Nodes (14): ProcessingJobOrm, Local representation of an authenticated Supabase user. The ``id`` aligns with…, Core operational entity — one job per submitted price/stock table.…, UserOrm, make_job(), make_user(), Job without a valid profile_id must fail., Provides a transactional session that rolls back after each test. (+6 more)

### Community 58 - "session.py"
Cohesion: 0.10
Nodes (26): create_all_tables(), create_db_engine(), drop_all_tables(), _get_database_url(), get_db_session(), _get_engine(), _get_session_factory(), get_test_engine() (+18 more)

### Community 59 - "Fase 2 — Database & Supabase (Debriefing & Intelligence)"
Cohesion: 0.10
Nodes (17): _JsonColumn, Maps to JSONB on PostgreSQL, native JSON on everything else (SQLite for tests)., Maps to native UUID on PostgreSQL, String(36) on SQLite (tests)., _UuidColumn, 1. Ficheiros Criados, 2. DDL Summary — Tabelas e Chaves Estrangeiras, 3. Gotcha: `_JsonColumn` / `_UuidColumn` Dialect-Aware Types, 4. Gotcha: `metadata` Reservado pelo SQLAlchemy Declarative (+9 more)

### Community 60 - "test_schema.py"
Cohesion: 0.12
Nodes (21): ApprovalOrm, Base, JobFileOrm, ProfileRuleOrm, SQLAlchemy 2.0 ORM models for Cotarco Commercial Manager. Mapped to PostgreSQL…, Versioned rule configuration attached to a commercial profile. Unique per…, Versioned file record for inputs, outputs, logs, and reports. The actual binary…, Immutable record of an approval, rejection, or cancellation action. Append-only… (+13 more)

### Community 61 - "Ficheiros Criados"
Cohesion: 0.18
Nodes (17): require_role(), approve_job(), DbDep, post, UserDep, UUID, POST /jobs/{id}/approve — OPERADOR/ADMIN only., Approve a job for processing. OPERADOR/ADMIN only — COMERCIAL gets HTTP 403. (+9 more)

### Community 62 - "test_jobs_api.py"
Cohesion: 0.15
Nodes (4): Tests for POST /jobs, GET /jobs, GET /jobs/{id} with RBAC., TestCreateJob, TestGetJobById, TestListJobs

### Community 63 - "test_processing_api.py"
Cohesion: 0.15
Nodes (4): Tests for POST /jobs/{id}/validate, GET /jobs/{id}/summary, items, issues., TestItemsAndIssuesEndpoints, TestSummaryEndpoint, TestValidateEndpoint

### Community 64 - "_make_job"
Cohesion: 0.14
Nodes (11): _make_job(), Deve retornar AIResponse com fallback quando Gemini falha., Deve retornar 404 para job_id inexistente., COMERCIAL não pode aceder ao job de outro utilizador., OPERADOR pode aceder a qualquer job., Payload inválido (sem campos obrigatórios) deve retornar 422., Severity inválido deve retornar 422., Insere um job na DB de teste e retorna o ID. (+3 more)

### Community 69 - "limpar_preco"
Cohesion: 0.33
Nodes (4): limpar_preco(), Cleans and parses price value into a rounded 2-decimal float. Robust against: -…, Tests for limpar_preco robust price parser., TestLimparPreco

### Community 70 - "v1/ai.py"
Cohesion: 0.07
Nodes (49): AIResponse, _append_audit(), _check_rate_limit(), explain_issue(), generate_summary(), _get_authorized_job(), Any, DbDep (+41 more)

### Community 71 - "Detailed Findings"
Cohesion: 0.29
Nodes (7): CATEGORY A — Naming & Terminology Inconsistencies, CATEGORY B — Missing Document Linkage / Dead References, CATEGORY C — Schema / Data Model Ambiguities, CATEGORY D — Duplicate / Drifting Rules, CATEGORY E — Workflow / Flow Gaps, CATEGORY F — Document Precedence Ambiguities, Detailed Findings

### Community 72 - "Detailed Findings"
Cohesion: 0.29
Nodes (7): CATEGORY C — Autonomy vs. Human Approval Gate Conflicts, CATEGORY E — Legacy / Obsolete / Underspecified Patterns, Detailed Findings, FIND-009, FIND-010, FIND-017, FIND-018

### Community 73 - "CATEGORY D — Stack Incompatibilities and Contradictions"
Cohesion: 0.29
Nodes (7): CATEGORY D — Stack Incompatibilities and Contradictions, FIND-011, FIND-012, FIND-013, FIND-014, FIND-015, FIND-016

### Community 74 - "react"
Cohesion: 0.13
Nodes (22): frontend_src_app_globals, metadata, DashboardPage(), Providers(), UploadZone(), UploadZoneProps, Header(), UserSwitcher() (+14 more)

### Community 75 - "_UserClient"
Cohesion: 0.18
Nodes (10): CurrentUser, comercial_client(), operador_client(), Install the shared db and user overrides (idempotent — called once per test)., Thin wrapper that sets the ContextVar before each HTTP call., _setup_shared_overrides(), override_get_db(), _UserClient (+2 more)

### Community 77 - "Actionable Harmonization Roadmap"
Cohesion: 0.40
Nodes (5): Actionable Harmonization Roadmap, 🔴 Priority 1 — Critical (fix before any agent begins implementation), 🟠 Priority 2 — Important (fix before Phase 2 Database and Phase 3 API agents begin), 🟡 Priority 3 — Recommended (fix before Phase 5 Frontend and Phase 7 Integration agents begin), 🟢 Priority 4 — Housekeeping (low risk, improve maintainability)

### Community 78 - "CATEGORY A — Dead / Incorrect Glob Paths"
Cohesion: 0.40
Nodes (5): CATEGORY A — Dead / Incorrect Glob Paths, FIND-001, FIND-002, FIND-003, FIND-004

### Community 79 - "CATEGORY B — Git / Commit Workflow Conflicts"
Cohesion: 0.40
Nodes (5): CATEGORY B — Git / Commit Workflow Conflicts, FIND-005, FIND-006, FIND-007, FIND-008

### Community 83 - "compilerOptions"
Cohesion: 0.11
Nodes (18): compilerOptions, allowJs, esModuleInterop, incremental, isolatedModules, jsx, lib, module (+10 more)

### Community 84 - "v1/jobs.py"
Cohesion: 0.21
Nodes (13): create_job(), get_job(), list_jobs(), DbDep, get, post, UserDep, UUID (+5 more)

### Community 85 - "api.ts"
Cohesion: 0.14
Nodes (20): DiffViewerProps, JobTableProps, DEMO_ISSUES, DEMO_ITEMS, DEMO_JOBS, DEMO_PROFILES, AIAnomalyExplanation, AIExplainIssueRequest (+12 more)

### Community 86 - "Fase 6 - E2E Demo e Ajustes da Inteligência Artificial"
Cohesion: 0.22
Nodes (8): 1. `test_commercial_job_submission_and_diff.spec.ts`, 2. `test_operator_approval_workflow.spec.ts`, 3. `test_accessibility_and_responsive_audit.spec.ts`, Ajustes da Inteligência Artificial, Declaração de Prontidão (MVP Completion Statement), Fase 6 - E2E Demo e Ajustes da Inteligência Artificial, Resumo Executivo, Testes End-to-End (E2E) com Playwright

### Community 87 - "package.json"
Cohesion: 0.13
Nodes (14): name, private, version, autoprefixer, clsx, postcss, react-dom, tailwind-merge (+6 more)

### Community 88 - "[id]/page.tsx"
Cohesion: 0.29
Nodes (13): JobDetailPage(), NewJobPage(), JobTable(), approveJob(), createJob(), fetchJob(), fetchJobIssues(), fetchJobItems() (+5 more)

### Community 90 - "ProcessSummary"
Cohesion: 0.33
Nodes (4): ProcessSummary, Consolidated quantitative metrics for a catalog processing execution., Total number of blocked items across all blocking rules., Total number of ignored items across all ignore conditions.

### Community 91 - "ValidationIssueList.tsx"
Cohesion: 0.26
Nodes (11): ValidationIssueList(), ValidationIssueListProps, Dialog(), DialogContent(), DialogDescription, DialogFooter(), DialogHeader(), DialogProps (+3 more)

### Community 92 - "test_ai_api.py"
Cohesion: 0.12
Nodes (17): AIResponse, AnomalyExplanation, ColumnSuggestion, ExplainIssueRequest, Explicação assistiva de uma anomalia/erro de validação. Gerado pelo Gemini em…, Sugestão de mapeamento para uma coluna desconhecida., Envelope genérico para todas as respostas de IA assistiva. O campo…, Payload para POST /jobs/{id}/ai/explain-issue. O frontend envia o código de… (+9 more)

### Community 93 - "dependencies"
Cohesion: 0.18
Nodes (11): dependencies, class-variance-authority, clsx, lucide-react, next, react, react-dom, tailwind-merge (+3 more)

### Community 94 - "conftest.py"
Cohesion: 0.15
Nodes (14): get_current_user(), get_db(), _get_session_factory(), DbDep, Test fixtures for API layer — Phase 3. Strategy: - Uses FastAPI TestClient with…, Tests for POST /jobs/{id}/approve — RBAC critical. CRITICAL: COMERCIAL must…, Tests for GET /api/v1/profiles and GET /api/v1/profiles/{id}., contextvars (+6 more)

### Community 95 - "Fase 4 — Frontend & Google Stitch Loop"
Cohesion: 0.25
Nodes (7): 1. Visão Geral, 2. Orquestração de Subagentes & Portões de Qualidade, 3. Stitch MCP Loop & Ecrãs Criados, 4. Tokens Corporativos e Design Engineering, 5. Ficheiros Criados no Frontend, 6. Validação e Qualidade (Evidências de Execução), Fase 4 — Frontend & Google Stitch Loop

### Community 96 - "normalize_col"
Cohesion: 0.19
Nodes (10): _find_field_value(), _find_target_key(), Any, Finds a field value in a dict using a list of case/accent-insensitive candidate…, Finds the actual key name present in target record matching candidate aliases., normalize_col(), Any, Normalizes column names and header text. Removes accents, strips… (+2 more)

### Community 97 - "devDependencies"
Cohesion: 0.22
Nodes (9): devDependencies, autoprefixer, @playwright/test, postcss, tailwindcss, @types/node, @types/react, @types/react-dom (+1 more)

### Community 98 - "scripts"
Cohesion: 0.33
Nodes (6): scripts, build, dev, lint, start, typecheck

### Community 99 - "Fase 3 — FastAPI & Endpoints"
Cohesion: 0.15
Nodes (8): RBAC EVIDENCE: COMERCIAL role is forbidden from approving jobs., Operador can call approve but job is in UPLOADED state → 409 INVALID_STATE., Operador can approve a job that is READY_FOR_REVIEW., TestApprovalRBAC, Contagem Final de Testes, Endpoints Implementados, Fase 3 — FastAPI & Endpoints, RBAC EVIDENCE

### Community 103 - "TestSuggestColumns"
Cohesion: 0.17
Nodes (7): Suite para o endpoint de sugestão de mapeamento de colunas., Deve retornar AIResponse com ColumnMapping válido., Deve usar fallback quando Gemini falha., Lista vazia de colunas deve retornar 422., 404 para job inexistente., OPERADOR pode usar suggest-columns em qualquer job., TestSuggestColumns

### Community 104 - "JobItemOrm"
Cohesion: 0.24
Nodes (7): JobItemOrm, Per-reference evaluation result from the domain engine. Stores both raw and…, Bulk-insert job item rows without individual flushes., Blocked items with BLOCKED_PRICE_VARIATION code are stored correctly., Deleting a job cascades to job_items., TestJobItemOrm, TestReferentialIntegrity

### Community 105 - "schemas/ai.py"
Cohesion: 0.18
Nodes (10): ColumnMapping, ExecutiveSummary, Pydantic v2 schemas for Gemini AI Assistive endpoints. GUARDRAIL (Regra de Ouro…, Resumo executivo assistivo de um processamento. Gerado pelo Gemini com base nos…, Resultado completo de sugestão de mapeamento de colunas. GUARDRAIL: Sugestões…, Payload para POST /jobs/{id}/ai/summary. Envia os dados quantitativos do job…, Payload para POST /jobs/{id}/ai/suggest-columns. Envia cabeçalhos desconhecidos…, SuggestColumnsRequest (+2 more)

### Community 106 - "patch"
Cohesion: 0.22
Nodes (7): Suite para o endpoint de resumo executivo., Deve retornar AIResponse com ExecutiveSummary quando Gemini responde., Deve usar fallback quando Gemini está indisponível., 404 para job inexistente., COMERCIAL recebe 403 ao tentar aceder ao job de outro utilizador., TestAISummary, patch

### Community 108 - "errors.py"
Cohesion: 0.29
Nodes (8): http_exception_handler(), make_error_body(), Standardized HTTP error handlers., validation_exception_handler(), Any, UTF8JSONResponse, JSONResponse, Request

### Community 109 - "ping_database"
Cohesion: 0.25
Nodes (6): ping_database(), Verify database connectivity. Returns True if reachable., ping_database returns True for a live engine., ping_database returns False for an unreachable database., All expected tables exist after create_all_tables., TestEngineConnectivity

### Community 110 - "TestSeedProfilesShape"
Cohesion: 0.22
Nodes (5): Validates that the expected seed profiles can be created and configured., MANO profile config must have stock_min=3 and variation=30%., BFA must have a 10% threshold (not the default 30%)., WooCommerce live push starts disabled (Guardrail #14)., TestSeedProfilesShape

### Community 111 - "AuditLogOrm"
Cohesion: 0.32
Nodes (5): AuditLogOrm, Immutable audit trail for all administrative and critical actions. SECURITY:…, Insert an audit log entry — NEVER update or delete. Application code must only…, System-generated audit logs have no actor_id (nullable)., TestAuditLogOrm

### Community 112 - "schemas/processing.py"
Cohesion: 0.47
Nodes (5): JobItemResponse, JobSummaryResponse, BaseModel, Pydantic v2 schemas for job items, issues, and summaries., ValidationIssueResponse

### Community 114 - "alert.tsx"
Cohesion: 0.40
Nodes (5): Alert, AlertDescription, AlertTitle, alertVariants, class-variance-authority

### Community 115 - ".test_rate_limit_triggers_429"
Cohesion: 0.50
Nodes (3): Testa o rate limit de chamadas de IA por utilizador., Após 20 chamadas num minuto, deve retornar 429., TestRateLimit

## Knowledge Gaps
- **576 isolated node(s):** `UploadZoneProps`, `ButtonProps`, `SelectProps`, `FilterType`, `BadgeProps` (+571 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 940 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **29 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `JobRepository` connect `JobRepository` to `JobItemOrm`, `AuditLogOrm`, `v1/jobs.py`, `session`, `Fase 2 — Database & Supabase (Debriefing & Intelligence)`, `test_schema.py`, `Ficheiros Criados`?**
  _High betweenness centrality (0.016) - this node is a cross-community bridge._
- **Why does `ProcessingJobOrm` connect `session` to `_make_job`, `JobItemOrm`, `v1/jobs.py`, `JobRepository`, `test_schema.py`?**
  _High betweenness centrality (0.014) - this node is a cross-community bridge._
- **Are the 14 inferred relationships involving `JobRepository` (e.g. with `ApprovalOrm` and `AuditLogOrm`) actually correct?**
  _`JobRepository` has 14 INFERRED edges - model-reasoned connections that need verification._
- **Are the 3 inferred relationships involving `process_price_table()` (e.g. with `CommercialProfile` and `DecisionCode`) actually correct?**
  _`process_price_table()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 5 inferred relationships involving `ProfileRepository` (e.g. with `CommercialProfileOrm` and `ProfileRuleOrm`) actually correct?**
  _`ProfileRepository` has 5 INFERRED edges - model-reasoned connections that need verification._
- **What connects `UploadZoneProps`, `ButtonProps`, `SelectProps` to the rest of the system?**
  _576 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.04521276595744681 - nodes in this community are weakly interconnected._