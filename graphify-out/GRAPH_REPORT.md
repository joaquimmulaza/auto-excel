# Graph Report - up_prices  (2026-09-25)

## Corpus Check
- 38 files · ~36,593 words
- Verdict: corpus is large enough that graph structure adds value.
- Unclassified: 3 file(s) not represented in the graph (top: (none) 3)

## Summary
- 619 nodes · 591 edges · 50 communities (41 shown, 9 thin omitted)
- Extraction: 100% EXTRACTED · 0% INFERRED · 0% AMBIGUOUS
- Token cost: 0 input · 0 output

## Graph Freshness
- Built from commit: `14e23c87`
- Run `git rev-parse HEAD` and compare to check if the graph is stale.
- Run `graphify update .` after code changes (no API cost).

## Community Hubs (Navigation)
- main.py
- Graphify
- find_column
- avaliar_price_guard
- Regras de Negócio Integradas
- Saneamento Avançado de Dados
- 3. Tabelas
- auto_detect_header
- criar_backup
- limpar_preco
- verificar_idade_ficheiro
- registar_historico
- ultra_clean
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
- CATEGORY D — Stack Incompatibilities and Contradictions
- Documentation Audit Report — Cotarco Commercial Manager
- Cotarco Commercial Manager — Remediation Cycle 1 Result
- Rules Auditor — Audit Report
- 🟡 P2 — MEDIUM (Resolver antes das fases de UI)
- 🔴 P0 — CRITICAL (Must resolve before implementation begins)
- 4.2 File Categories Within `graphify-out/`

## God Nodes (most connected - your core abstractions)
1. `Stack Tecnológica & Regras de Ouro (Tech Stack & Guardrails)` - 22 edges
2. `3. Tabelas` - 20 edges
3. `4. Requisitos funcionais` - 19 edges
4. `UI/UX Wireframes + Design System Base` - 17 edges
5. `MASTER ORCHESTRATOR — Cotarco Commercial Manager` - 15 edges
6. `Graphify` - 13 edges
7. `🟡 P2 — MEDIUM (Resolver antes das fases de UI)` - 12 edges
8. `🟢 P3 — LOW (Housekeeping — antes do MVP Demo)` - 12 edges
9. `Suite de Testes Automatizados — TDD First` - 12 edges
10. `Matriz de Rotas e APIs` - 12 edges

## Surprising Connections (you probably didn't know these)
- `Notebook Index` --references--> `Graphify Knowledge Graph Setup`  [EXTRACTED]
  .notebook/INDEX.md → .notebook/graphify-setup.md

## Import Cycles
- None detected.

## Hyperedges (group relationships)
- **Graphify Outputs and Commands** — graphify, graphify_out_graph_html, graphify_out_graph_report_md, graphify_out_graph_json, graphify_query_command, graphify_path_command, graphify_explain_command, graphify_update_command [EXTRACTED 1.00]
- **Graphify Setup Components** — graphify, uv_tool, agents_rules_graphify_md, agents_workflows_graphify_md, git_hooks, gitattributes, graphifyignore [EXTRACTED 1.00]
- **Price and Stock Updater Workflow** — cotarco_samsung_preco_atualizado_xlsx, mano_preco_desatualizado_xlsx, main, mano_preco_atualizado_final_xlsx, log_decisao_samsung_xlsx, deteccao_automatica_cabecalho, mapeamento_tolerante_colunas, saneamento_avancado_dados, regras_negocio_integradas, log_decisao_transparente [EXTRACTED 1.00]

## Communities (50 total, 9 thin omitted)

### Community 0 - "main.py"
Cohesion: 0.09
Nodes (20): argparse, Cotarco-Samsung-preco-atualizado.xlsx, datetime, Deteção Automática de Cabeçalho, io, LOG_DECISAO_SAMSUNG.xlsx, Log de Decisão Transparente, Mano-preco-atualizado-final.xlsx (+12 more)

### Community 1 - "Graphify"
Cohesion: 0.12
Nodes (16): .agents/rules/graphify.md, .agents/workflows/graphify.md, Git Hooks, .gitattributes, Graphify, graphify explain, graphify-out/graph.html, graphify-out/graph.json (+8 more)

### Community 2 - "find_column"
Cohesion: 0.40
Nodes (6): find_column(), map_columns(), normalize_col(), Recebe lista de nomes de colunas já normalizados e uma lista de candidatos.…, Normaliza os nomes das colunas do dataframe e faz o mapeamento para nomes…, Remove acentos, espaços e coloca em maiúsculas.

### Community 3 - "avaliar_price_guard"
Cohesion: 0.50
Nodes (4): avaliar_price_guard(), calcular_variacao(), Calcula a variação percentual entre dois preços., Verifica se a variação de preço excede o limiar configurado. Retorna…

### Community 4 - "Regras de Negócio Integradas"
Cohesion: 0.67
Nodes (3): Ativação/Inativação, Filtragem de Segurança, Regras de Negócio Integradas

### Community 5 - "Saneamento Avançado de Dados"
Cohesion: 0.67
Nodes (3): Limpeza de Preços, Saneamento Avançado de Dados, Ultra Clean

### Community 6 - "3. Tabelas"
Cohesion: 0.07
Nodes (28): 1. Princípios, 2. Modelo lógico, 3. Tabelas, 4. Enums mínimos, 5. Índices importantes, 6. RLS / autorização, 7. Integridade de ficheiros, 8. Retenção (+20 more)

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
Cohesion: 0.05
Nodes (37): 1. Executive Summary, 2.1 Git Status, 2.2 Commit History, 2.3 Total Tracked File Inventory Summary, 2. Current Git Status & Repository Hygiene Overview, 3.1 Scope, 3.2 Packages Tracked, 3.3 Sub-directory Distribution (playwright-core alone spans) (+29 more)

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
Cohesion: 0.17
Nodes (11): 0. Ordem obrigatória de leitura, 1. Princípio central, 2. Não fazer, 3. Regras de arquitetura, 4. Regra de alterações, 5. Stitch MCP — protocolo obrigatório para UI, 6. QA de Stitch, 7. Evidência obrigatória (+3 more)

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
Cohesion: 0.07
Nodes (28): 4 ADRs em Falta (Bloqueantes de Implementação), Classification Legend, Cotarco Commercial Manager — Remediation Plan, Executive Summary, 🟠 P1 — HIGH (Resolver antes das fases de DB/API), 🟢 P3 — LOW (Housekeeping — antes do MVP Demo), REM-011, REM-012 (+20 more)

### Community 43 - "CATEGORY D — Stack Incompatibilities and Contradictions"
Cohesion: 0.08
Nodes (24): CATEGORY A — Dead / Incorrect Glob Paths, CATEGORY B — Git / Commit Workflow Conflicts, CATEGORY C — Autonomy vs. Human Approval Gate Conflicts, CATEGORY D — Stack Incompatibilities and Contradictions, CATEGORY E — Legacy / Obsolete / Underspecified Patterns, Detailed Findings, FIND-001, FIND-002 (+16 more)

### Community 44 - "Documentation Audit Report — Cotarco Commercial Manager"
Cohesion: 0.09
Nodes (22): Actionable Harmonization Roadmap, ADR Gap Analysis, CATEGORY A — Naming & Terminology Inconsistencies, CATEGORY B — Missing Document Linkage / Dead References, CATEGORY C — Schema / Data Model Ambiguities, CATEGORY D — Duplicate / Drifting Rules, CATEGORY E — Workflow / Flow Gaps, CATEGORY F — Document Precedence Ambiguities (+14 more)

### Community 45 - "Cotarco Commercial Manager — Remediation Cycle 1 Result"
Cohesion: 0.14
Nodes (13): CHECKS, Cotarco Commercial Manager — Remediation Cycle 1 Result, FILES, Files Modified, Files Untracked from Git Tracking (629 files), FIXED (28 Authorized REM-IDs), GIT, GRAPHIFY (+5 more)

### Community 46 - "Rules Auditor — Audit Report"
Cohesion: 0.15
Nodes (8): Autonomy vs. Human Approval Conflict Analysis, Conclusion, Executive Summary, Files Audited, Git / Commit Workflow Conflict Analysis, Legacy / Obsolete Patterns Summary, Recommendations Priority Matrix, Rules Auditor — Audit Report

### Community 47 - "🟡 P2 — MEDIUM (Resolver antes das fases de UI)"
Cohesion: 0.17
Nodes (12): 🟡 P2 — MEDIUM (Resolver antes das fases de UI), REM-019, REM-020, REM-021, REM-022, REM-023, REM-024, REM-025 (+4 more)

### Community 48 - "🔴 P0 — CRITICAL (Must resolve before implementation begins)"
Cohesion: 0.18
Nodes (11): 🔴 P0 — CRITICAL (Must resolve before implementation begins), REM-001, REM-002, REM-003, REM-004, REM-005, REM-006, REM-007 (+3 more)

### Community 49 - "4.2 File Categories Within `graphify-out/`"
Cohesion: 0.20
Nodes (10): 4.1 Overview, 4.2.1 Internal Marker / State Files (Hidden, Should NOT be tracked), 4.2.2 AST Cache Files — 30 files (Should NOT be tracked), 4.2.3 Semantic Cache Files — 34 files (Should NOT be tracked), 4.2.4 Human-Readable Generated Outputs (Debatable — possibly keep one, not dated duplicates), 4.2.5 Dated Snapshot Directory (Redundant with root-level files), 4.2 File Categories Within `graphify-out/`, 4.3 What `.graphifyignore` Currently Does (+2 more)

## Knowledge Gaps
- **471 isolated node(s):** `Executive Summary`, `Inventory of Documentation Audited`, `CATEGORY A — Naming & Terminology Inconsistencies`, `CATEGORY B — Missing Document Linkage / Dead References`, `CATEGORY C — Schema / Data Model Ambiguities` (+466 more)
  These have ≤1 connection - possible missing edges or undocumented components. (Counts symbols only; 520 node(s) total have ≤1 connection when file, concept and rationale nodes are included.)
- **9 thin communities (<3 nodes) omitted from report** — run `graphify query` to explore isolated nodes.

## Suggested Questions
_Questions this graph is uniquely positioned to answer:_

- **Why does `Cotarco Commercial Manager — Remediation Plan` connect `🟢 P3 — LOW (Housekeeping — antes do MVP Demo)` to `🔴 P0 — CRITICAL (Must resolve before implementation begins)`, `Rules Auditor — Audit Report`, `🟡 P2 — MEDIUM (Resolver antes das fases de UI)`?**
  _High betweenness centrality (0.042) - this node is a cross-community bridge._
- **Why does `Git & Artifacts Audit Report` connect `7. Proposed Remediation Steps (DO NOT EXECUTE — Reference Only)` to `4.2 File Categories Within `graphify-out/``, `Rules Auditor — Audit Report`?**
  _High betweenness centrality (0.039) - this node is a cross-community bridge._
- **Why does `Graphify Audit Report — Cotarco Commercial Manager / up_prices` connect `4. Discrepancies Between Rules, Workflows, Setup Docs, and Reality` to `Rules Auditor — Audit Report`?**
  _High betweenness centrality (0.029) - this node is a cross-community bridge._
- **What connects `Executive Summary`, `Inventory of Documentation Audited`, `CATEGORY A — Naming & Terminology Inconsistencies` to the rest of the system?**
  _471 weakly-connected nodes found - possible documentation gaps or missing edges._
- **Should `main.py` be split into smaller, more focused modules?**
  _Cohesion score 0.09090909090909091 - nodes in this community are weakly interconnected._
- **Should `Graphify` be split into smaller, more focused modules?**
  _Cohesion score 0.125 - nodes in this community are weakly interconnected._
- **Should `3. Tabelas` be split into smaller, more focused modules?**
  _Cohesion score 0.06896551724137931 - nodes in this community are weakly interconnected._