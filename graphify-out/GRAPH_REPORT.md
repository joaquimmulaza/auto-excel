# Graph Report - up_prices  (2026-09-25)

## Corpus Check
- 54 files · ~43,457 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 799 nodes · 976 edges · 55 communities (47 shown, 8 thin omitted)
- Extraction: 96% EXTRACTED · 4% INFERRED · 0% AMBIGUOUS · INFERRED: 40 edges (avg confidence: 0.95)
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `f7da4788`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- Graphify
- normalization.py
- process_price_table
- domain/__init__.py
- engine.py
- 3. Tabelas
- PriceRule
- ProcessSummary
- 🟠 P1 — HIGH (Resolver antes das fases de DB/API)
- CommercialProfile
- 1. Bugs e Gotchas Identificados no Legado & Soluções Aplicadas
- create_profile
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
- ProcessResult
- TestZeroPriceNewProducts
- app/__init__.py
- services/__init__.py
- backend/__init__.py
- tests/__init__.py

## God Nodes (most connected - your core abstractions)
1. `process_price_table()` - 41 edges
2. `Stack Tecnológica & Regras de Ouro (Tech Stack & Guardrails)` - 22 edges
3. `3. Tabelas` - 20 edges
4. `PriceRule` - 19 edges
5. `StockRule` - 19 edges
6. `4. Requisitos funcionais` - 19 edges
7. `IssueSeverity` - 18 edges
8. `CommercialProfile` - 18 edges
9. `UI/UX Wireframes + Design System Base` - 17 edges
10. `DecisionCode` - 16 edges

## Surprising Connections (you probably didn't know these)
- `1.1 Bug do Preço Zero (Passo 4 do Legado)` --references--> `ValidationIssue`  [INFERRED]
  .notebook/phase-1-domain-engine.md → backend/app/domain/models.py
- `1.2 Sobrescrita Silenciosa de Duplicados (Dicionário Zip)` --references--> `ValidationIssue`  [INFERRED]
  .notebook/phase-1-domain-engine.md → backend/app/domain/models.py
- `2. Contratos e Modelos Principais` --references--> `CommercialProfile`  [INFERRED]
  .notebook/phase-1-domain-engine.md → backend/app/domain/models.py
- `2. Contratos e Modelos Principais` --references--> `ProcessResult`  [INFERRED]
  .notebook/phase-1-domain-engine.md → backend/app/domain/models.py
- `2. Contratos e Modelos Principais` --references--> `Product`  [INFERRED]
  .notebook/phase-1-domain-engine.md → backend/app/domain/models.py

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Outputs and Commands** — graphify, graphify_out_graph_html, graphify_out_graph_report_md, graphify_out_graph_json, graphify_query_command, graphify_path_command, graphify_explain_command, graphify_update_command [EXTRACTED 1.00]
- **Graphify Setup Components** — graphify, uv_tool, agents_rules_graphify_md, agents_workflows_graphify_md, git_hooks, gitattributes, graphifyignore [EXTRACTED 1.00]
- **Price and Stock Updater Workflow** — cotarco_samsung_preco_atualizado_xlsx, mano_preco_desatualizado_xlsx, main, mano_preco_atualizado_final_xlsx, log_decisao_samsung_xlsx, deteccao_automatica_cabecalho, mapeamento_tolerante_colunas, saneamento_avancado_dados, regras_negocio_integradas, log_decisao_transparente [EXTRACTED 1.00]

## Communities (55 total, 8 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.05
Nodes (46): argparse, Ativação/Inativação, Cotarco-Samsung-preco-atualizado.xlsx, datetime, Deteção Automática de Cabeçalho, Filtragem de Segurança, io, Limpeza de Preços (+38 more)

### Community 1 - "Graphify"
Cohesion: 0.12
Nodes (16): .agents/rules/graphify.md, .agents/workflows/graphify.md, Git Hooks, .gitattributes, Graphify, graphify explain, graphify-out/graph.html, graphify-out/graph.json (+8 more)

### Community 2 - "normalization.py"
Cohesion: 0.08
Nodes (22): calcular_variacao(), limpar_preco(), normalize_col(), Any, Domain normalization and data cleaning utilities for Cotarco Commercial…, Safely calculates relative price variation without division by zero. Returns:…, Normalizes column names and header text. Removes accents, strips…, Sanitizes catalog references deterministically. Retains strictly uppercase… (+14 more)

### Community 3 - "process_price_table"
Cohesion: 0.11
Nodes (13): _find_field_value(), _find_target_key(), process_price_table(), Any, Processes source supplier/marketplace table against a target catalog…, Executes table processing using the configured CommercialProfile., Finds a field value in a dict using a list of case/accent-insensitive candidate…, Finds the actual key name present in target record matching candidate aliases. (+5 more)

### Community 4 - "domain/__init__.py"
Cohesion: 0.15
Nodes (18): Domain layer package for Cotarco Commercial Manager. Exports domain entities,…, Structured issue or violation emitted during validation or processing., Indicates whether this issue prevents automated execution., ValidationIssue, calculate_price_variation(), clean_price_value(), evaluate_new_product_eligibility(), evaluate_price_guard() (+10 more)

### Community 5 - "engine.py"
Cohesion: 0.19
Nodes (15): Domain processing engine for Cotarco Commercial Manager. Fully deterministic,…, DecisionCode, IssueSeverity, Domain models and contracts for Cotarco Commercial Manager. All models are…, Severity levels for validation and business rule issues., Standardized decision outcome codes for item evaluation., Unit tests for duplicate reference detection in source dataset. Tests Bug 2…, Unit tests for the core domain engine: TableProcessor / process_price_table.… (+7 more)

### Community 6 - "3. Tabelas"
Cohesion: 0.07
Nodes (28): 1. Princípios, 2. Modelo lógico, 3. Tabelas, 4. Enums mínimos, 5. Índices importantes, 6. RLS / autorização, 7. Integridade de ficheiros, 8. Retenção (+20 more)

### Community 7 - "PriceRule"
Cohesion: 0.20
Nodes (14): PriceRule, Configuration rules for price validation and thresholds., Configuration rules for stock management and product activation., StockRule, profile(), fixture, profile(), fixture (+6 more)

### Community 8 - "ProcessSummary"
Cohesion: 0.18
Nodes (9): JobItemResult, ProcessSummary, Product, Canonical domain product entity representing a commercial catalog item., Detailed evaluation and decision outcome for a single catalog reference item., Consolidated quantitative metrics for a catalog processing execution., Total number of blocked items across all blocking rules., Total number of ignored items across all ignore conditions. (+1 more)

### Community 9 - "🟠 P1 — HIGH (Resolver antes das fases de DB/API)"
Cohesion: 0.22
Nodes (9): 🟠 P1 — HIGH (Resolver antes das fases de DB/API), REM-011, REM-012, REM-013, REM-014, REM-015, REM-016, REM-017 (+1 more)

### Community 10 - "CommercialProfile"
Cohesion: 0.25
Nodes (6): Class wrapper providing a stateless engine processor instance., TableProcessor, CommercialProfile, Commercial profile defining destination channel settings and rules., Services layer entry point for table processing., TableProcessor class can be instantiated and executed cleanly.

### Community 11 - "1. Bugs e Gotchas Identificados no Legado & Soluções Aplicadas"
Cohesion: 0.22
Nodes (8): 1.1 Bug do Preço Zero (Passo 4 do Legado), 1.2 Sobrescrita Silenciosa de Duplicados (Dicionário Zip), 1.3 Price Guard Hardcoded vs Dinâmico, 1.4 Higienização e Normalização Determinística, 1. Bugs e Gotchas Identificados no Legado & Soluções Aplicadas, 3. Evidência de Testes TDD, Fase 1 — Extração do Engine de Domínio (Debriefing & Intelligence), Resumo Executivo

### Community 12 - "create_profile"
Cohesion: 0.39
Nodes (3): create_profile(), Verifies that the price variation threshold is dynamically evaluated from…, TestConfigurablePriceGuard

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
Cohesion: 0.06
Nodes (32): Autonomy vs. Human Approval Conflict Analysis, CATEGORY A — Dead / Incorrect Glob Paths, CATEGORY B — Git / Commit Workflow Conflicts, CATEGORY C — Autonomy vs. Human Approval Gate Conflicts, CATEGORY D — Stack Incompatibilities and Contradictions, CATEGORY E — Legacy / Obsolete / Underspecified Patterns, Conclusion, Detailed Findings (+24 more)

### Community 44 - "Documentation Audit Report — Cotarco Commercial Manager"
Cohesion: 0.07
Nodes (22): Actionable Harmonization Roadmap, ADR Gap Analysis, CATEGORY A — Naming & Terminology Inconsistencies, CATEGORY B — Missing Document Linkage / Dead References, CATEGORY C — Schema / Data Model Ambiguities, CATEGORY D — Duplicate / Drifting Rules, CATEGORY E — Workflow / Flow Gaps, CATEGORY F — Document Precedence Ambiguities (+14 more)

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

### Community 49 - "ProcessResult"
Cohesion: 0.33
Nodes (4): ProcessResult, Aggregate processing output containing items, issues, summary, and final…, Returns True if any blocker issues exist., Returns total evaluated items.

## Knowledge Gaps
- **478 isolated node(s):** `Resumo Executivo`, `1.3 Price Guard Hardcoded vs Dinâmico`, `1.4 Higienização e Normalização Determinística`, `3. Evidência de Testes TDD`, `0. Ordem obrigatória de leitura` (+473 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 590 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **8 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Cotarco Commercial Manager — Remediation Plan` connect `Cotarco Commercial Manager — Remediation Plan` to `🟠 P1 — HIGH (Resolver antes das fases de DB/API)`, `🟢 P3 — LOW (Housekeeping — antes do MVP Demo)`, `Documentation Audit Report — Cotarco Commercial Manager`, `🟡 P2 — MEDIUM (Resolver antes das fases de UI)`, `🔴 P0 — CRITICAL (Must resolve before implementation begins)`?**
  _High betweenness centrality (0.025) - this node is a cross-community bridge._
- **Why does `Git & Artifacts Audit Report` connect `7. Proposed Remediation Steps (DO NOT EXECUTE — Reference Only)` to `Documentation Audit Report — Cotarco Commercial Manager`?**
  _High betweenness centrality (0.024) - this node is a cross-community bridge._
- **Why does `Graphify Audit Report — Cotarco Commercial Manager / up_prices` connect `4. Discrepancies Between Rules, Workflows, Setup Docs, and Reality` to `Documentation Audit Report — Cotarco Commercial Manager`?**
  _High betweenness centrality (0.018) - this node is a cross-community bridge._
- **Are the 3 inferred relationships involving `process_price_table()` (e.g. with `CommercialProfile` and `DecisionCode`) actually correct?**
  _`process_price_table()` has 3 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `PriceRule` (e.g. with `evaluate_new_product_eligibility()` and `evaluate_price_guard()`) actually correct?**
  _`PriceRule` has 7 INFERRED edges - model-reasoned connections that need verification._
- **Are the 7 inferred relationships involving `StockRule` (e.g. with `evaluate_new_product_eligibility()` and `evaluate_stock_activation()`) actually correct?**
  _`StockRule` has 7 INFERRED edges - model-reasoned connections that need verification._
- **What connects `Resumo Executivo`, `1.3 Price Guard Hardcoded vs Dinâmico`, `1.4 Higienização e Normalização Determinística` to the rest of the system?**
  _478 weakly-connected nodes found - possible documentation gaps or missing edges._