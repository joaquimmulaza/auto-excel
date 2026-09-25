# Graphify Knowledge Graph Setup

## Overview
Graphify converts project code and documentation into a queryable knowledge graph with community clustering and visualization.

## Setup Details
- **CLI & Binary**: Managed via `uv tool` at `C:\Users\MARKETING DESIGNER01\AppData\Roaming\uv\tools\graphifyy\Scripts\python.exe`.
- **MCP Server**: Configured in `~/.gemini/antigravity-ide/mcp_config.json` via direct python `-m graphify.serve`.
- **Antigravity Rule**: [.agents/rules/graphify.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.agents/rules/graphify.md) installed via `graphify antigravity install`.
- **Antigravity Workflow**: [.agents/workflows/graphify.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.agents/workflows/graphify.md).
- **Git Hooks**: Post-commit and post-checkout hooks installed in `.git/hooks/`, with merge driver in [.gitattributes](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.gitattributes).
- **Ignore File**: [.graphifyignore](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.graphifyignore) excludes `.agents/` so internal agent skills do not contaminate repository knowledge.

## Outputs & Graph State
- **Nodes/Edges**: 58 nodes, 60 edges, 14 communities (covering `main.py`, business rules, Excel workflows, and documentation).
- **Interactive Graph**: [graphify-out/graph.html](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/graphify-out/graph.html)
- **Graph Report**: [graphify-out/GRAPH_REPORT.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/graphify-out/GRAPH_REPORT.md)
- **Raw Graph Data**: [graphify-out/graph.json](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/graphify-out/graph.json)

## Key Commands
- Query: `graphify query "<question>"`
- Shortest path: `graphify path "<ConceptA>" "<ConceptB>"`
- Node explanation: `graphify explain "<NodeName>"`
- Update after code changes: `graphify update .`
