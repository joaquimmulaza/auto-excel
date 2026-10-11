# AGENTS.md — Cotarco Commercial Manager (root entry)

This repository is developed as **Cotarco Commercial Manager**. The product blueprint lives under `cotarco-commercial-manager/`. Do not invent process: follow that folder and this file.

## Source of truth

| Path | Role |
|---|---|
| `cotarco-commercial-manager/context.md` | Persistent product/domain context |
| `cotarco-commercial-manager/agents.md` | Operating rules for agents |
| `cotarco-commercial-manager/docs/*` | Requirements, data, flows, API, stack, UI, TDD, backlog |
| `cotarco-commercial-manager/prompts/MASTER_ORCHESTRATOR.md` | Phase orchestration |
| `cotarco-commercial-manager/prompts/agents/` | Phase prompts `00`–`06` |
| `cotarco-commercial-manager/prompts/stitch/` | Stitch UI prompts |
| `cotarco-commercial-manager/adr/` | Architecture decisions |

Paths in prompts that say `context.md` / `agents.md` / `docs/...` resolve under `cotarco-commercial-manager/`.

## Mandatory cycle (every non-trivial prompt)

1. **Read** `cotarco-commercial-manager/context.md`, `cotarco-commercial-manager/agents.md`, and the docs required by the task (see agents.md §0).
2. **Graphify MCP recon** on `joaquimmulaza/auto-excel` (`repository_id` UUID `155ea5ab-4976-4975-83e1-efcba12a3061` or `joaquimmulaza/auto-excel`) before broad grep/Read:
   - `list_repositories` if unsure of access
   - `query_graph` / `graphify_find` for behavior/symbols
   - `graphify_callers` / `graphify_callees` / `graphify_impact` / `graphify_tests_for` for blast radius
   - `graphify_file_neighbors` for file deps
3. **Pick the phase prompt** — if the user pasted `00`–`06` or a Stitch prompt, execute that prompt to the letter; otherwise follow `MASTER_ORCHESTRATOR.md` + `docs/mvp-backlog.md` and do not skip critical phases.
4. **Load only scoped skills** from `agents.md` §11 for that phase.
5. **TDD loop** → minimal implementation → QA. UI structural work uses Stitch MCP (max 3 cycles) per `agents.md` §5–6.
6. **Handoff** in the 9-field format from `agents.md` §7.

## Hard limits

- No rewriting the whole project without an explicit task.
- No business rules in the frontend; no Gemini from the browser.
- No secrets in code or committed `.env`.
- No skipping TDD for domain/API work.
- Stop on documentary contradictions; resolve/document before coding.
- After structural code changes, run `graphify update .` when the CLI is available.

## Graphify repository

Canonical indexed repo for this workspace: **`joaquimmulaza/auto-excel`**.
