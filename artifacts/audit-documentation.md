# Documentation Audit Report — Cotarco Commercial Manager

**Auditor:** Documentation Auditor Agent (Subagent 4)
**Audit Date:** 2026-09-25
**Mode:** READ-ONLY — no existing files were modified
**Status:** COMPLETE

---

## Executive Summary

The Cotarco Commercial Manager documentation corpus is **fundamentally sound** in its intent and architecture direction. The stack decision (Next.js + FastAPI + Supabase + Gemini assistive) is coherent, consistently repeated, and never seriously contradicted across documents. The guiding principles—TDD-first, domain-first, adapter isolation, no hardcoded partner rules, AI as assistant not authority—are uniform and correctly enforced throughout all 27 files audited.

However, the audit identified **19 concrete findings** across six categories:

| Category | Count | Highest Severity |
|---|---|---|
| Naming / Terminology Inconsistency | 5 | MEDIUM |
| Missing Document Linkage / Dead References | 3 | HIGH |
| Ambiguous Table Naming (schema) | 3 | HIGH |
| Duplicate / Drifting Rules | 3 | LOW–MEDIUM |
| Workflow / Flow Gap | 2 | MEDIUM |
| Precedence Ambiguity | 3 | MEDIUM |

No findings involve the stack being contradicted internally, no legacy monolithic auto-excel design being presented as the new architecture, and no secrets-in-code violations detected at the documentation level.

The primary risks are: (1) a schema table naming mismatch between `data-architecture.md` and `requirements.md` that could confuse implementors; (2) a broken file path reference in `stitch/00-design-system.md` pointing outside the project; (3) a silent gap in the documented reading order (agents.md omits `docs/data-architecture.md` and `docs/application-flows.md`); (4) the `output_files` table indecision left unresolved in `data-architecture.md`. These should be resolved before implementation begins.

---

## Inventory of Documentation Audited

| # | File | Type | Lines | Last Known Version |
|---|---|---|---|---|
| 1 | `context.md` | Product context (mandatory) | 235 | 2026-09-25 (implicit) |
| 2 | `agents.md` | Agent operating rules | 123 | 2026-09-25 (implicit) |
| 3 | `README.md` | Project blueprint / index | 58 | 2026-09-25 (implicit) |
| 4 | `docs/requirements.md` | Functional & non-functional requirements | 243 | v1.0, 23/09/2026 |
| 5 | `docs/data-architecture.md` | DB schema & data principles | 336 | 2026-09-25 (implicit) |
| 6 | `docs/application-flows.md` | UX/process flows | 188 | 2026-09-25 (implicit) |
| 7 | `docs/routes-api.md` | Frontend routes & API endpoints | 195 | 2026-09-25 (implicit) |
| 8 | `docs/stack-and-guardrails.md` | Tech stack & guardrails | 211 | 2026-09-25 (implicit) |
| 9 | `docs/ui-wireframes-and-design-system.md` | UX/wireframes/design system | 225 | 2026-09-25 (implicit) |
| 10 | `docs/testing-tdd.md` | Testing strategy | 264 | 2026-09-25 (implicit) |
| 11 | `docs/mvp-backlog.md` | Implementation backlog order | 97 | 2026-09-25 (implicit) |
| 12 | `docs/references.md` | External technical references | 36 | 23/09/2026 |
| 13 | `adr/0001-architecture.md` | ADR: initial architecture | 38 | Accepted 23/09/2026 |
| 14 | `adr/0002-supabase-free.md` | ADR: Supabase for MVP | 30 | Accepted (implicit date) |
| 15 | `prompts/README.md` | Prompt orchestration guide | 50 | 2026-09-25 (implicit) |
| 16 | `prompts/MASTER_ORCHESTRATOR.md` | Master orchestrator prompt | 205 | 2026-09-25 (implicit) |
| 17 | `prompts/agents/00-bootstrap-audit.md` | Agent A00 prompt | 43 | 2026-09-25 (implicit) |
| 18 | `prompts/agents/01-domain-tdd.md` | Agent A10-A16 prompt | 61 | 2026-09-25 (implicit) |
| 19 | `prompts/agents/02-database.md` | Agent A20-A23 prompt | 40 | 2026-09-25 (implicit) |
| 20 | `prompts/agents/03-api.md` | Agent A30-A35 prompt | 42 | 2026-09-25 (implicit) |
| 21 | `prompts/agents/04-frontend.md` | Agent A50-A55 prompt | 40 | 2026-09-25 (implicit) |
| 22 | `prompts/agents/05-gemini.md` | Agent A60-A63 prompt | 34 | 2026-09-25 (implicit) |
| 23 | `prompts/agents/06-integrations-and-demo.md` | Agent A70-A76 prompt | 56 | 2026-09-25 (implicit) |
| 24 | `prompts/stitch/00-design-system.md` | Stitch design system prompt | 60 | 2026-09-25 (implicit) |
| 25 | `prompts/stitch/01-dashboard.md` | Stitch dashboard prompt | 25 | 2026-09-25 (implicit) |
| 26 | `prompts/stitch/02-new-job.md` | Stitch new job prompt | 20 | 2026-09-25 (implicit) |
| 27 | `prompts/stitch/03-review-diff.md` | Stitch review/diff prompt | 54 | 2026-09-25 (implicit) |

**Total files audited:** 27
**Directories covered:** root, `docs/`, `adr/`, `prompts/agents/`, `prompts/stitch/`

---

## Detailed Findings

---

### CATEGORY A — Naming & Terminology Inconsistencies

---

**Finding A-01**
| Field | Detail |
|---|---|
| **ID** | A-01 |
| **Documents & Sections** | `data-architecture.md` §3 (`commercial_profiles` table) vs. `docs/mvp-backlog.md` backlog items A15, `application-flows.md` §6 (`Profile`), `requirements.md` §2 (RF-002), `agents.md` §3 |
| **Nature** | The database table is named `commercial_profiles` in `data-architecture.md`. Everywhere else in the documentation corpus—`context.md`, `requirements.md`, `application-flows.md`, `agents.md`, `prompts/`—the entity is referred to simply as `Profile`, `commercial profile`, or `perfil de tabela`. The database prompt `02-database.md` seeds using codes `MANO, WOOCOMMERCE, BFA, KERO, SIAC, RESELLERS, OTHER`, but `requirements.md` §RF-002 lists `Loja Online, Marketplace Mano, BFA, Kero, SIAC, Revendedores, Outros`. |
| **Severity** | MEDIUM |
| **Impact** | Implementors reading `data-architecture.md` will use `commercial_profiles` for migrations, but conceptual docs call it simply `profiles`. The seed in `02-database.md` uses code `WOOCOMMERCE` while conceptual docs call it `Loja Online` (which maps to WooCommerce). This dual naming is not destructive but requires a mapping table or clarifying note to prevent confusion. |
| **Recommended Fix** | In `data-architecture.md`, add a one-sentence note: *"The table `commercial_profiles` maps to the product concept 'perfil de tabela'. The route namespace `/profiles` in `routes-api.md` aligns with the abbreviated form."* In `02-database.md`, annotate the seed entries: `WOOCOMMERCE` → *(Loja Online)*, `MANO` → *(Marketplace Mano)*. |
| **Risk Level** | LOW (confusion risk, not correctness risk) |

---

**Finding A-02**
| Field | Detail |
|---|---|
| **ID** | A-02 |
| **Documents & Sections** | `context.md` §2 (roles: `COMERCIAL`, `OPERADOR`, `ADMIN`) vs. `data-architecture.md` §4 enum `user_role` vs. `requirements.md` §3 (personas P1, P2, P3) vs. `routes-api.md` §2 (table notation `Comercial+`, `Operador+`) |
| **Nature** | Roles are named consistently in most places as `COMERCIAL`, `OPERADOR`, `ADMIN`. However, `routes-api.md` uses the shorthand `Comercial+` and `Operador+` without defining what the `+` means. The `+` notation implicitly means "this role or higher", but this convention is nowhere defined. A developer might misread `Comercial+` as "Comercial and above" or as a literal role named `Comercial+`. |
| **Severity** | LOW |
| **Impact** | Potential authorization implementation bug if the `+` convention is not understood. |
| **Recommended Fix** | Add a legend to `routes-api.md` §1 (Conventions): *"Role notation: `ROLE+` means that role and any role with equal or greater privilege (e.g., `COMERCIAL+` = COMERCIAL, OPERADOR, ADMIN)."* |
| **Risk Level** | LOW |

---

**Finding A-03**
| Field | Detail |
|---|---|
| **ID** | A-03 |
| **Documents & Sections** | `context.md` §2, `requirements.md` §3 vs. `routes-api.md` §2 (`/historico`), `application-flows.md`, `testing-tdd.md` §3 |
| **Nature** | The third role is called `ADMIN` in `context.md`, `data-architecture.md` enum, and `requirements.md`, but `routes-api.md` §2 uses `Admin` (title-case) inconsistently in the access column while also using `ADMIN` (uppercase) in §4, §8. Two capitalizations of the same role exist in the same document. |
| **Severity** | LOW |
| **Impact** | Minor readability issue; no functional risk if developers follow the enum. |
| **Recommended Fix** | Standardize `routes-api.md` to use `ADMIN` in all role references to match the PostgreSQL enum definition. |
| **Risk Level** | NEGLIGIBLE |

---

**Finding A-04**
| Field | Detail |
|---|---|
| **ID** | A-04 |
| **Documents & Sections** | `requirements.md` §4 RF-009 (job states) vs. `data-architecture.md` §4 enum `job_status` vs. `application-flows.md` §1 (flow diagram) vs. `testing-tdd.md` §3 (`ValidateJob`) |
| **Nature** | Job state names are **consistent** across all documents (`UPLOADED`, `VALIDATING`, `READY_FOR_REVIEW`, `NEEDS_CORRECTION`, `APPROVED`, `PROCESSING`, `COMPLETED`, `FAILED`, `CANCELLED`). **However**, the `approvals` table in `data-architecture.md` §3 defines `action text` values as `APPROVED`, `REJECTED`, `CANCELLED`—while the `processing_jobs.status` enum does not have a `REJECTED` state. The flow shows `Aprovar / rejeitar` as an Operator action, meaning `REJECTED` maps to what job status? Presumably `NEEDS_CORRECTION` or a missing `REJECTED` status. |
| **Severity** | HIGH |
| **Impact** | The approval action `REJECTED` has no corresponding `job_status` value. An implementor will need to decide whether rejection sends the job back to `NEEDS_CORRECTION` (as implied by the flow diagram) or introduces a new state. This silent gap can lead to inconsistent implementations across backend/frontend agents. |
| **Recommended Fix** | In `data-architecture.md` §4, add a note under `job_status`: *"When an Operator rejects a job (`approvals.action = REJECTED`), the job transitions to `NEEDS_CORRECTION`. There is no separate `REJECTED` terminal state."* Alternatively, add `REJECTED` to the `job_status` enum if that is the intended behavior—and document the distinction from `NEEDS_CORRECTION`. |
| **Risk Level** | MEDIUM-HIGH |

---

**Finding A-05**
| Field | Detail |
|---|---|
| **ID** | A-05 |
| **Documents & Sections** | `data-architecture.md` §3 (`job_files.kind` values: `INPUT`, `OUTPUT`, `LOG`, `REPORT`) vs. `application-flows.md` §4 (`Generate outputs`) vs. `data-architecture.md` §3 (`output_files`) |
| **Nature** | `job_files.kind` has a value `OUTPUT`, yet a separate table `output_files` is defined. The architecture note states: *"Pode ser mantida separada de `job_files` se necessário para metadata específica; no MVP `job_files` pode ser suficiente. Se ambas existirem, evitar duplicação de source of truth."* This leaves the decision unresolved—`output_files` might or might not be created during implementation. If both are created, there is a genuine source-of-truth conflict. |
| **Severity** | MEDIUM |
| **Impact** | Two agents (Database and API) could make incompatible decisions about `output_files`. One agent might skip it; another might create it. Without a decision, a schema drift will occur. |
| **Recommended Fix** | Make a definitive decision: either (a) drop `output_files` from the schema description and use `job_files` with `kind = OUTPUT` for MVP, or (b) keep `output_files` and remove the `OUTPUT` kind from `job_files`. Document this as ADR-0003. |
| **Risk Level** | MEDIUM |

---

### CATEGORY B — Missing Document Linkage / Dead References

---

**Finding B-01**
| Field | Detail |
|---|---|
| **ID** | B-01 |
| **Documents & Sections** | `agents.md` §0 (mandatory reading order) |
| **Nature** | The mandatory reading order in `agents.md` lists: (1) `context.md`, (2) `agents.md`, (3) `docs/requirements.md`, (4) `docs/stack-and-guardrails.md`, (5) `docs/testing-tdd.md`, (6) task-specific doc. **Missing from this list:** `docs/data-architecture.md`, `docs/application-flows.md`, `docs/routes-api.md`, and `docs/ui-wireframes-and-design-system.md`. The `README.md` lists 10 documents as the "fonte de contexto principal", but `agents.md` only mandates 5. |
| **Severity** | HIGH |
| **Impact** | An agent following only `agents.md §0` would begin implementation without reading the data schema, application flows, API routes, or UI system. All agent prompts reference these documents individually, but the authoritative "mandatory read" list in `agents.md` is incomplete and inconsistent with `README.md`. |
| **Recommended Fix** | Expand `agents.md §0` reading order to include all documents listed in `README.md §Fonte de contexto principal`. At minimum, add `docs/data-architecture.md` and `docs/application-flows.md` as mandatory reads before any implementation task begins. |
| **Risk Level** | HIGH |

---

**Finding B-02**
| Field | Detail |
|---|---|
| **ID** | B-02 |
| **Documents & Sections** | `prompts/stitch/00-design-system.md` §Validação Pré-Stitch (line 13) |
| **Nature** | The prompt contains a hardcoded absolute Windows file path: `file:///c:/Users/MARKETING DESIGNER01/Downloads/up_prices/.agents/skills/enhance-prompt/SKILL.md`. This path (a) references a location outside the `cotarco-commercial-manager/` project directory, (b) contains a machine-specific absolute path that will not resolve on any other machine or CI environment, and (c) references a `.agents/skills/` directory that is not documented anywhere in the project. |
| **Severity** | HIGH |
| **Impact** | Any agent or developer reading this prompt on a different machine will encounter a broken reference. The skill is never described in any project document, making it impossible to verify what it does or substitute it. This is also a potential external dependency not tracked in the project. |
| **Recommended Fix** | (1) Replace the absolute path with a project-relative reference or remove the link entirely, using plain text to describe what `enhance-prompt` does. (2) If `enhance-prompt` is a legitimate dependency, document it in `docs/stack-and-guardrails.md` or `README.md` and add it to the repository or reference it with a stable URL. (3) Do not embed machine-specific absolute paths in any project document. |
| **Risk Level** | HIGH |

---

**Finding B-03**
| Field | Detail |
|---|---|
| **ID** | B-03 |
| **Documents & Sections** | `prompts/agents/00-bootstrap-audit.md` task 3: *"Criar a estrutura inicial proposta em `docs/`"* |
| **Nature** | The bootstrap audit prompt instructs the agent to *create* the `docs/` structure as a task outcome, but `docs/` already exists and contains all 8 documentation files. This creates a logical paradox: the A00 agent is instructed to create documentation that already exists. This is a vestigial instruction from when the documentation did not yet exist. |
| **Severity** | LOW |
| **Impact** | A00 agent may attempt to create or overwrite existing `docs/` files, causing data loss or confusion. The instruction is now stale. |
| **Recommended Fix** | Update `00-bootstrap-audit.md` task 3 to: *"Review and validate the existing `docs/` structure against the current repository state; identify any missing, outdated, or contradictory documentation."* |
| **Risk Level** | MEDIUM |

---

### CATEGORY C — Schema / Data Model Ambiguities

---

**Finding C-01**
| Field | Detail |
|---|---|
| **ID** | C-01 |
| **Documents & Sections** | `data-architecture.md` §2 (ERD) vs. §3 (`profiles` table definition) |
| **Nature** | The ER diagram uses the entity name `profiles`, but the table definition in §3 is named `commercial_profiles`. The ERD relationship line reads `profiles ||--o{ profile_rules : has`, but the schema heading is `### commercial_profiles`. These two sections of the same document contradict each other. |
| **Severity** | HIGH |
| **Impact** | Implementors will be unsure which table name to use for migrations. One agent creating migrations may choose `profiles`, another may choose `commercial_profiles`. This is a direct implementation risk. |
| **Recommended Fix** | Align ERD and table definition. Recommended canonical name: `commercial_profiles` (matches the route namespace `/profiles` at the API level which is abbreviated for UX). Update the ERD to `commercial_profiles ||--o{ profile_rules : has`. Add a note: *"API route `/profiles` is an abbreviated path; the underlying table is `commercial_profiles`."* |
| **Risk Level** | HIGH |

---

**Finding C-02**
| Field | Detail |
|---|---|
| **ID** | C-02 |
| **Documents & Sections** | `data-architecture.md` §3 (`processing_jobs` table) vs. `requirements.md` RF-003 |
| **Nature** | `processing_jobs` has `source_name text` and `source_system text` fields. `requirements.md` RF-003 says *"indicar descrição/opcional"*, while `routes-api.md` §10 shows the `POST /jobs` contract with `source_system` (e.g., `"SAMSUNG"`) and `description`. However, there is no `description` field in `processing_jobs`. The wireframe in `ui-wireframes-and-design-system.md` §9 shows a "Descrição (opcional)" field in the new job form. This field is in the UI wireframe and API contract but not in the DB schema. |
| **Severity** | MEDIUM |
| **Impact** | The frontend form and API contract assume a `description` field on the job, but `data-architecture.md` does not include one. An implementor may add it ad-hoc to the schema, or may omit it, breaking the API contract. |
| **Recommended Fix** | Add `description text nullable` to `processing_jobs` in `data-architecture.md`. |
| **Risk Level** | MEDIUM |

---

**Finding C-03**
| Field | Detail |
|---|---|
| **ID** | C-03 |
| **Documents & Sections** | `data-architecture.md` §3 (`users` table) vs. Supabase Auth integration |
| **Nature** | The `users` table has `id uuid pk` with the note *"alinhado com identidade do Auth quando possível"*. The phrase "quando possível" (when possible) introduces ambiguity. Supabase Auth creates users in `auth.users`; the application's `users` table is a local mirror. The sync strategy (trigger, foreign key, or manual sync) is never specified. ADR-0002 does not address this. |
| **Severity** | MEDIUM |
| **Impact** | Without a defined sync strategy, two different implementors may create incompatible solutions: one using `auth.uid()` directly via RLS, another creating a manual sync trigger, leading to divergent data models. |
| **Recommended Fix** | Add to `data-architecture.md` or ADR-0002: *"The `users.id` must equal `auth.users.id` from Supabase Auth. A database trigger on `auth.users` INSERT/UPDATE is the recommended sync mechanism. Alternatively, the application creates the `users` row on first authenticated request. Choose and document one approach."* |
| **Risk Level** | MEDIUM |

---

### CATEGORY D — Duplicate / Drifting Rules

---

**Finding D-01**
| Field | Detail |
|---|---|
| **ID** | D-01 |
| **Documents & Sections** | Stitch workflow defined in: `agents.md §5`, `agents.md §6`, `stack-and-guardrails.md §15`, `ui-wireframes-and-design-system.md §15`, `prompts/MASTER_ORCHESTRATOR.md §Stitch Loop`, `prompts/README.md §Stitch loop` |
| **Nature** | The Stitch QA/iteration loop is described **6 times** across 6 different documents. The "maximum 3 cycles" rule is stated in `agents.md §5`, `MASTER_ORCHESTRATOR.md`, and `prompts/README.md`. The QA criteria are in `agents.md §6` and `stack-and-guardrails.md §15`. The workflow steps appear in `ui-wireframes-and-design-system.md §15`, `prompts/README.md`, and `MASTER_ORCHESTRATOR.md`. These are broadly consistent today, but as one document evolves (e.g., the 3-cycle limit is changed), the others will drift. |
| **Severity** | LOW–MEDIUM |
| **Impact** | Documentation drift risk: updating the Stitch rules in one place creates silent inconsistencies in the others. |
| **Recommended Fix** | Designate `agents.md §5-6` as the single authoritative source for Stitch operating rules. All other documents should reference it: *"See `agents.md §5 — Stitch MCP Protocol` for the complete Stitch workflow and QA criteria."* Remove the repeated content from `ui-wireframes-and-design-system.md §15` and `MASTER_ORCHESTRATOR.md §Stitch Loop` or reduce them to a short summary + link. |
| **Risk Level** | LOW |

---

**Finding D-02**
| Field | Detail |
|---|---|
| **ID** | D-02 |
| **Documents & Sections** | Gemini guardrails defined in: `context.md §6`, `agents.md §2` ("Não chamar Gemini diretamente do browser"), `stack-and-guardrails.md §5 (Guardrail #3)`, `MASTER_ORCHESTRATOR.md §Decisão sobre IA`, `prompts/agents/05-gemini.md §Guardrails` |
| **Nature** | The Gemini restrictions (no price decisions, no approvals, no external mutations, no browser-side calls) are repeated in 5 documents. The lists are slightly different each time. `context.md §6` is the most complete; `stack-and-guardrails.md §5` adds "call external integration directly" which `context.md` does not list. `prompts/agents/05-gemini.md` adds "timeout, retry, rate limit, logs without sensitive content, labeled as AI" which are operational details not present in the conceptual guardrail. |
| **Severity** | LOW |
| **Impact** | The variations between lists are additive (no contradictions), but adding new rules to one list and not the others creates an incomplete picture in each individual document. |
| **Recommended Fix** | Consolidate the authoritative Gemini rule list into `context.md §6` and `stack-and-guardrails.md §5 (Guardrail #3)`. Other documents should reference: *"Gemini usage rules: see `context.md §6` and `stack-and-guardrails.md Guardrail #3`."* |
| **Risk Level** | NEGLIGIBLE |

---

**Finding D-03**
| Field | Detail |
|---|---|
| **ID** | D-03 |
| **Documents & Sections** | Handoff format defined in: `agents.md §7`, `mvp-backlog.md §Handoff obrigatório`, `MASTER_ORCHESTRATOR.md §Handoff format` |
| **Nature** | The agent handoff format is defined three times. `agents.md §7` lists 6 fields (summary, tests, result, risks, files, pending decision). `mvp-backlog.md §Handoff` lists 5 fields (DONE, TESTS, FILES, RISKS, NEXT). `MASTER_ORCHESTRATOR.md §Handoff format` lists 9 fields (STATUS, TASK, SUMMARY, FILES, TESTS, QA, RISKS, DOCS_UPDATED, NEXT). These are meaningfully different—the Orchestrator format is the most complete, but it is unclear which format an agent must follow. |
| **Severity** | MEDIUM |
| **Impact** | An agent following `agents.md §7` will produce a handoff missing STATUS, TASK, QA, and DOCS_UPDATED fields. The Orchestrator expecting the 9-field format will receive incomplete information and may misinterpret progress. |
| **Recommended Fix** | Designate `MASTER_ORCHESTRATOR.md §Handoff format` as the canonical handoff format. Update `agents.md §7` and `mvp-backlog.md §Handoff` to reference the MASTER_ORCHESTRATOR format, or reproduce the 9-field format identically. Add a mandatory `QA` field to `agents.md §7` at minimum. |
| **Risk Level** | MEDIUM |

---

### CATEGORY E — Workflow / Flow Gaps

---

**Finding E-01**
| Field | Detail |
|---|---|
| **ID** | E-01 |
| **Documents & Sections** | `application-flows.md` §1 (main flow) vs. `requirements.md` RF-010 (correction/reupload) vs. `testing-tdd.md §3` (`ValidateJob`) |
| **Nature** | The main flow in `application-flows.md §1` shows a branch: if blockers exist → `NEEDS_CORRECTION` → "Corrigir/reupload" → (back to validação implied). However, `requirements.md` RF-010 states: *"criando nova versão do ficheiro dentro do mesmo job **ou** novo job conforme decisão de produto"*. This "or new job" option is absent from `application-flows.md` and from `testing-tdd.md`. The flow also does not show what happens to the existing `job_files` version when a re-upload occurs, though `application-flows.md §3` (correction flow) does clarify not to delete the previous version. |
| **Severity** | MEDIUM |
| **Impact** | The unresolved "same job vs. new job for re-submission" creates a product decision gap. Frontend and Backend agents will need to resolve this independently, risking incompatible implementations. |
| **Recommended Fix** | Make a definitive product decision and document it: *"Re-upload always creates a new file version within the same job (job_files.version increments). A new job is created only by the user explicitly choosing 'Novo processamento'."* Update `application-flows.md §3` and `requirements.md` RF-010 to reflect this decision. Record in an ADR if the decision has architectural impact. |
| **Risk Level** | MEDIUM |

---

**Finding E-02**
| Field | Detail |
|---|---|
| **ID** | E-02 |
| **Documents & Sections** | `routes-api.md §5` (`POST /jobs/{id}/reopen`) vs. `application-flows.md` (no reopen flow) vs. `data-architecture.md §4` (`job_status` enum) |
| **Nature** | `routes-api.md` defines `POST /jobs/{id}/reopen` (Operador+) but there is no corresponding flow in `application-flows.md` showing when/how a job is "reopened." The `job_status` enum has no `REOPENED` state. It is unclear what state transition `reopen` causes. This endpoint exists in the API design without a corresponding domain concept or flow. |
| **Severity** | MEDIUM |
| **Impact** | The `reopen` endpoint will be implemented without a defined state machine transition, leading to undefined behavior (e.g., does it reset to `UPLOADED`? `NEEDS_CORRECTION`? `READY_FOR_REVIEW`?). |
| **Recommended Fix** | Either (a) define the `reopen` semantics: what state it transitions from (e.g., `COMPLETED` or `FAILED`) and to (e.g., `NEEDS_CORRECTION` or `APPROVED`), and add the flow to `application-flows.md`; or (b) remove the endpoint from `routes-api.md` until the use case is defined. |
| **Risk Level** | MEDIUM |

---

### CATEGORY F — Document Precedence Ambiguities

---

**Finding F-01**
| Field | Detail |
|---|---|
| **ID** | F-01 |
| **Documents & Sections** | `README.md §Fonte de contexto principal` vs. `agents.md §0` vs. `MASTER_ORCHESTRATOR.md §Fonte de verdade` |
| **Nature** | Three documents attempt to define the hierarchy of truth, with slight differences: `README.md` lists 10 documents (does not include ADRs). `agents.md §0` mandates 5 documents before implementation. `MASTER_ORCHESTRATOR.md §Fonte de verdade` lists 10 documents (identical to README but includes the ADR implication in the contradiction resolution note: *"Se existir contradição, parar, registrar e resolver/documentar antes de implementar"*). None of these documents explicitly states which document wins when two documents contradict each other (e.g., if `requirements.md` says X and `data-architecture.md` says Y). |
| **Severity** | MEDIUM |
| **Impact** | Without a clear precedence chain, agents facing a contradiction (like finding A-04 or C-01 above) must guess which document to follow, potentially making inconsistent choices. |
| **Recommended Fix** | Add a **Document Hierarchy** section to `context.md` (as the topmost mandatory document) and to `README.md`. Define: |
| | 1. `context.md` (highest authority — product vision, domain, business rules) |
| | 2. ADRs (accepted decisions override older doc wording) |
| | 3. `docs/requirements.md` (functional requirements) |
| | 4. `docs/data-architecture.md` (schema canonical) |
| | 5. `docs/routes-api.md` (API contracts) |
| | 6. `docs/application-flows.md` (flows) |
| | 7. `docs/stack-and-guardrails.md` (implementation guardrails) |
| | 8. `agents.md` (agent operating rules) |
| | 9. `prompts/` (execution guidance, non-authoritative) |
| **Risk Level** | MEDIUM |

---

**Finding F-02**
| Field | Detail |
|---|---|
| **ID** | F-02 |
| **Documents & Sections** | `adr/0002-supabase-free.md` vs. `docs/stack-and-guardrails.md §21` vs. `docs/references.md §Supabase` |
| **Nature** | The Supabase Free tier limitations and quotas are documented in three places: ADR-0002 (qualitative), `stack-and-guardrails.md §21` (quantitative snapshot: 500 MB, 1 GB storage, 50k MAU, 5 GB egress, pause after 1 week), and `references.md §Supabase` (same quantitative snapshot). All three consistently label these as snapshots. **However**, ADR-0002 does not include the quantitative figures, making it incomplete as a decision record. If quotas change, developers may update `stack-and-guardrails.md` but forget to update `references.md` or vice versa. |
| **Severity** | LOW |
| **Impact** | Minor drift risk. No contradiction today, but two documents contain identical data that will need parallel updates. |
| **Recommended Fix** | Keep the quantitative Supabase snapshot in `references.md` only (as its purpose is to record external reference data). In `stack-and-guardrails.md §21` and `ADR-0002`, reference `docs/references.md §Supabase` for the current snapshot rather than duplicating the numbers. |
| **Risk Level** | LOW |

---

**Finding F-03**
| Field | Detail |
|---|---|
| **ID** | F-03 |
| **Documents & Sections** | `context.md §9` vs. `requirements.md §6` (pending business rules) |
| **Nature** | Both `context.md §9` and `requirements.md §6` list business rules that are unknown and must not be invented. The two lists are similar but not identical. `context.md §9` mentions: BFA, Kero, SIAC partner rules; registering decisions in `docs/requirements.md` or ADR. `requirements.md §6` has a more complete list (10 bullet points). Neither document explicitly states what the agent must do if a rule is required to progress but is not yet validated (block? use placeholder? log risk?). |
| **Severity** | LOW |
| **Impact** | The gap between "what is unknown" and "what to do when you need it" is not addressed. `MASTER_ORCHESTRATOR.md §Quando bloquear` fills this gap, but it is in the prompt layer, not in the authoritative docs. |
| **Recommended Fix** | Add to `context.md §9` and/or `requirements.md §6`: *"When a rule is required for implementation and has not been validated, the agent must: (1) stop the task, (2) document the required rule as a BLOCKED item in the handoff, (3) record a placeholder in the relevant document, (4) not invent the rule."* This moves the blocking policy from the prompt layer into the authoritative documentation. |
| **Risk Level** | LOW |

---

## Summary Table of All Findings

| ID | Category | Document(s) | Severity | Risk Level |
|---|---|---|---|---|
| A-01 | Naming | `data-architecture.md`, `02-database.md`, `requirements.md` | MEDIUM | LOW |
| A-02 | Naming | `routes-api.md` | LOW | LOW |
| A-03 | Naming | `routes-api.md` | LOW | NEGLIGIBLE |
| **A-04** | **Naming/Schema** | **`data-architecture.md`, `application-flows.md`** | **HIGH** | **MEDIUM-HIGH** |
| **A-05** | **Schema** | **`data-architecture.md`** | **MEDIUM** | **MEDIUM** |
| **B-01** | **Missing Linkage** | **`agents.md §0`** | **HIGH** | **HIGH** |
| **B-02** | **Dead Reference** | **`stitch/00-design-system.md`** | **HIGH** | **HIGH** |
| B-03 | Stale Instruction | `00-bootstrap-audit.md` | LOW | MEDIUM |
| **C-01** | **Schema Naming** | **`data-architecture.md` ERD vs §3** | **HIGH** | **HIGH** |
| **C-02** | **Schema Gap** | **`data-architecture.md`, `routes-api.md`** | **MEDIUM** | **MEDIUM** |
| C-03 | Schema Ambiguity | `data-architecture.md`, ADR-0002 | MEDIUM | MEDIUM |
| D-01 | Duplication | 6 documents | LOW | LOW |
| D-02 | Duplication | 5 documents | LOW | NEGLIGIBLE |
| **D-03** | **Duplication/Conflict** | **`agents.md`, `mvp-backlog.md`, `MASTER_ORCHESTRATOR.md`** | **MEDIUM** | **MEDIUM** |
| **E-01** | **Flow Gap** | **`application-flows.md`, `requirements.md` RF-010** | **MEDIUM** | **MEDIUM** |
| **E-02** | **Flow Gap** | **`routes-api.md`, `application-flows.md`** | **MEDIUM** | **MEDIUM** |
| **F-01** | **Precedence** | **`README.md`, `agents.md`, `MASTER_ORCHESTRATOR.md`** | **MEDIUM** | **MEDIUM** |
| F-02 | Precedence | `adr/0002-supabase-free.md`, `stack-and-guardrails.md`, `references.md` | LOW | LOW |
| F-03 | Precedence | `context.md §9`, `requirements.md §6` | LOW | LOW |

**Critical / High severity findings (action required before implementation):** A-04, B-01, B-02, C-01

---

## Precedence & Hierarchy Assessment

### Current State

No document currently defines a formal precedence hierarchy. Three documents (`README.md`, `agents.md`, `MASTER_ORCHESTRATOR.md`) each attempt to define the reading order, producing a de-facto implied hierarchy that is incomplete and inconsistent (see Finding F-01).

### Observed Implied Hierarchy

Based on cross-document analysis, the effective (but undocumented) hierarchy is:

```
context.md          ← Topmost authority (product vision, domain rules)
     ↓
ADRs (adr/)         ← Accepted decisions supersede doc wording
     ↓
docs/requirements.md ← Functional requirements
     ↓
docs/data-architecture.md ← Schema canonical source of truth
     ↓
docs/routes-api.md  ← API contracts
     ↓
docs/application-flows.md ← Flows
     ↓
docs/stack-and-guardrails.md ← Implementation guardrails
     ↓
agents.md           ← Agent operating rules
     ↓
prompts/            ← Execution guidance (non-authoritative)
```

### Gaps in Precedence

1. **No conflict resolution rule:** No document states what an agent must do when two documents in the hierarchy contradict each other. Only `MASTER_ORCHESTRATOR.md` implicitly requires stopping and resolving first.
2. **ADRs have no authority flag:** The ADRs are not referenced in any mandatory reading list. An agent following `agents.md §0` would never read ADR-0001 or ADR-0002 unless the specific task prompt directed it there.
3. **Prompts can override docs silently:** An agent prompt (`03-api.md`, `04-frontend.md`) could specify a behavior not in the authoritative docs, and the agent would have no explicit signal that the prompt is non-authoritative.

---

## Actionable Harmonization Roadmap

The following roadmap is ordered by priority and estimated effort. All items are documentation-only changes; no code or schema changes are implied.

### 🔴 Priority 1 — Critical (fix before any agent begins implementation)

| # | Action | Files to Update | Effort |
|---|---|---|---|
| H-01 | **Resolve ERD vs. table name conflict** (Finding C-01): Align `commercial_profiles` in both ERD and table definition in `data-architecture.md`. | `docs/data-architecture.md` | 15 min |
| H-02 | **Add `REJECTED` → state transition mapping** (Finding A-04): Clarify that `approvals.action = REJECTED` transitions job to `NEEDS_CORRECTION` or add `REJECTED` to `job_status` enum. Record decision in ADR-0003. | `docs/data-architecture.md`, `adr/ADR-0003` (new) | 30 min |
| H-03 | **Fix broken absolute path** (Finding B-02): Remove or replace the machine-specific Windows path in `prompts/stitch/00-design-system.md`. Document `enhance-prompt` dependency in `README.md` or remove reference. | `prompts/stitch/00-design-system.md` | 10 min |
| H-04 | **Expand `agents.md §0` mandatory reading list** (Finding B-01): Add `docs/data-architecture.md`, `docs/application-flows.md`, `docs/routes-api.md`, `docs/ui-wireframes-and-design-system.md` to the mandatory pre-implementation reading. | `agents.md` | 10 min |

### 🟠 Priority 2 — Important (fix before Phase 2 Database and Phase 3 API agents begin)

| # | Action | Files to Update | Effort |
|---|---|---|---|
| H-05 | **Resolve `output_files` vs `job_files` ambiguity** (Finding A-05): Make a definitive decision and document it. Recommended: use `job_files` with `kind = OUTPUT` for MVP and explicitly deprecate the `output_files` table definition. | `docs/data-architecture.md` | 20 min |
| H-06 | **Add `description` field to `processing_jobs`** (Finding C-02): Align schema with the API contract and UI wireframe. | `docs/data-architecture.md` | 10 min |
| H-07 | **Define Supabase Auth sync strategy** (Finding C-03): Choose and document the `users` / `auth.users` sync mechanism. Update `data-architecture.md` and ADR-0002. | `docs/data-architecture.md`, `adr/0002-supabase-free.md` | 20 min |
| H-08 | **Unify handoff format** (Finding D-03): Standardize to the 9-field MASTER_ORCHESTRATOR format. Update `agents.md §7` and `mvp-backlog.md §Handoff` to match exactly. | `agents.md`, `docs/mvp-backlog.md` | 15 min |
| H-09 | **Define `reopen` semantics** (Finding E-02): Either add a flow to `application-flows.md` for job reopening, or remove the endpoint from `routes-api.md`. | `docs/application-flows.md` or `docs/routes-api.md` | 20 min |

### 🟡 Priority 3 — Recommended (fix before Phase 5 Frontend and Phase 7 Integration agents begin)

| # | Action | Files to Update | Effort |
|---|---|---|---|
| H-10 | **Resolve re-upload decision** (Finding E-01): Document whether re-submission creates a new file version in the same job or a new job. Update `application-flows.md §3` and `requirements.md` RF-010. | `docs/application-flows.md`, `docs/requirements.md` | 20 min |
| H-11 | **Add Document Hierarchy section** (Finding F-01): Add a formal precedence declaration to `context.md` and `README.md`. | `context.md`, `README.md` | 25 min |
| H-12 | **Add role notation legend** (Finding A-02): Add `+` notation explanation to `routes-api.md §1`. | `docs/routes-api.md` | 5 min |
| H-13 | **Annotate seed profile codes** (Finding A-01): Add mapping comments in `02-database.md` seed section (`WOOCOMMERCE` → Loja Online, `MANO` → Marketplace Mano). | `prompts/agents/02-database.md` | 10 min |

### 🟢 Priority 4 — Housekeeping (low risk, improve maintainability)

| # | Action | Files to Update | Effort |
|---|---|---|---|
| H-14 | **Consolidate Stitch workflow** (Finding D-01): Remove duplicate Stitch workflow descriptions from `ui-wireframes-and-design-system.md §15`, `MASTER_ORCHESTRATOR.md §Stitch Loop`, `stack-and-guardrails.md §15`. Keep full version in `agents.md §5-6`. | Multiple | 30 min |
| H-15 | **Consolidate Gemini guardrails** (Finding D-02): Keep full authoritative list in `context.md §6` + `stack-and-guardrails.md Guardrail #3`. Reduce other occurrences to references. | Multiple | 20 min |
| H-16 | **Add ADRs to mandatory reading** (Finding F-01): Reference `adr/` in `agents.md §0` and `README.md §Fonte de contexto principal`. | `agents.md`, `README.md` | 5 min |
| H-17 | **Update stale bootstrap instruction** (Finding B-03): Revise `00-bootstrap-audit.md` task 3 to reflect that `docs/` already exists. | `prompts/agents/00-bootstrap-audit.md` | 5 min |
| H-18 | **Normalize `Admin` vs `ADMIN`** (Finding A-03): Standardize to `ADMIN` throughout `routes-api.md`. | `docs/routes-api.md` | 5 min |
| H-19 | **Consolidate Supabase quota references** (Finding F-02): Remove quantitative Supabase numbers from `stack-and-guardrails.md §21`; reference `docs/references.md §Supabase` instead. | `docs/stack-and-guardrails.md` | 10 min |

---

## ADR Gap Analysis

| Needed ADR | Covers | Status |
|---|---|---|
| ADR-0001 | Initial architecture (Next.js + FastAPI + Supabase) | ✅ Exists |
| ADR-0002 | Supabase Free for MVP | ✅ Exists |
| ADR-0003 | `REJECTED` approval action → job state transition | ❌ Missing |
| ADR-0004 | `output_files` vs `job_files` for output storage | ❌ Missing |
| ADR-0005 | Re-upload strategy (new version in same job vs new job) | ❌ Missing |
| ADR-0006 | Supabase Auth `users` sync strategy | ❌ Missing |

---

## What Was NOT Found (Positive Findings)

The following concerns were investigated and found to be **non-issues**:

- ✅ **No legacy auto-excel monolithic architecture presented as new design.** All documents clearly position `auto-excel` as the legacy origin and consistently describe the new platform as a separate, properly layered system.
- ✅ **No stack conflicts.** Next.js, FastAPI, Supabase, Gemini, and Stitch are consistently chosen across all documents with no alternative stacks proposed or implied.
- ✅ **No secrets in documentation.** No API keys, passwords, or production credentials are present in any document.
- ✅ **No hardcoded partner business rules.** All documents correctly defer partner-specific rules to profile configuration and consistently prohibit `if partner == "BFA"` style code.
- ✅ **No AI over-reach.** Gemini restrictions are consistent and enforced throughout all layers (context, guardrails, prompts, flows).
- ✅ **No missing testing strategy.** The TDD-first approach is uniformly mandated across `agents.md`, `stack-and-guardrails.md`, `testing-tdd.md`, and all agent prompts.
- ✅ **No WooCommerce API version conflict.** All documents consistently specify REST API v3 and correctly defer the integration behind a feature flag.
- ✅ **No legacy path references.** No references to outdated directory structures, old project paths, or deprecated conventions were found.
- ✅ **Job status enum is consistent.** The 9 states (`UPLOADED` → `CANCELLED`) appear identically in `requirements.md`, `data-architecture.md`, `application-flows.md`, and `testing-tdd.md` (except the gap noted in A-04 regarding `REJECTED`).

---

*Report generated by Documentation Auditor Subagent — 2026-09-25. Read-only audit. No files modified.*
