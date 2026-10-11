---
trigger: always_on
description: Consult Graphify MCP/CLI before broad codebase reads; keep the graph current after code changes.
---

## graphify

This project is indexed by Graphify (local `graphify-out/` and Cloud MCP workspace).

Canonical repository for MCP tools: `joaquimmulaza/auto-excel` (`155ea5ab-4976-4975-83e1-efcba12a3061`).

Rules:

- For codebase or architecture questions, use Graphify **before** broad grep/Read.
- Prefer MCP when available:
  - `list_repositories` — confirm access/index readiness
  - `query_graph` — natural-language behavior/architecture questions
  - `graphify_find` / `graphify_node` — locate and inspect symbols
  - `graphify_callers` / `graphify_callees` / `graphify_impact` / `graphify_tests_for` — blast radius and linked tests
  - `graphify_file_neighbors` — file deps
  - `shortest_path` / `graphify_trace` — paths between symbols
- CLI fallback (local): `graphify query`, `graphify path`, `graphify explain`.
- If `graphify-out/wiki/index.md` exists, navigate it instead of reading raw dumps.
- Read `graphify-out/GRAPH_REPORT.md` only for broad architecture review or when query tools do not surface enough context.
- After modifying code files in this session, run `graphify update .` when the CLI is available (AST-only, no API cost).
