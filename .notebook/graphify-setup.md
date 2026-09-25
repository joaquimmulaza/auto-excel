# Graphify Knowledge Graph Setup

## Overview
Graphify converts project code and documentation into a queryable knowledge graph with community clustering and visualization.

## Setup Details
- **CLI & Binary**: Managed via `uv tool` (accessible via `graphify` CLI command or `%APPDATA%\uv\tools\graphifyy\Scripts\python.exe`).
- **MCP Server**: Configured in `~/.gemini/antigravity-ide/mcp_config.json` via direct python `-m graphify.serve`.
- **Antigravity Rule**: [.agents/rules/graphify.md](../.agents/rules/graphify.md) installed via `graphify antigravity install`.
- **Antigravity Workflow**: [.agents/workflows/graphify.md](../.agents/workflows/graphify.md).
- **Git Hooks**: Post-commit and post-checkout hooks installed in `.git/hooks/`, with merge driver in [.gitattributes](../.gitattributes).
- **Ignore File**: [.graphifyignore](../.graphifyignore) excludes `.agents/` so internal agent skills do not contaminate repository knowledge.

## Outputs & Graph State
- **Nodes/Edges**: 414 nodes, 388 edges, 42 communities (baseline snapshot; metrics evolve dynamically via `graphify update .` and git hooks, tracked in [graphify-out/GRAPH_REPORT.md](../graphify-out/GRAPH_REPORT.md)).
- **Interactive Graph**: [graphify-out/graph.html](../graphify-out/graph.html)
- **Graph Report**: [graphify-out/GRAPH_REPORT.md](../graphify-out/GRAPH_REPORT.md)
- **Raw Graph Data**: [graphify-out/graph.json](../graphify-out/graph.json)

## Key Commands
- Query: `graphify query "<question>"`
- Shortest path: `graphify path "<ConceptA>" "<ConceptB>"`
- Node explanation: `graphify explain "<NodeName>"`
- Update after code changes: `graphify update .`
