# UI Skills MCP & Workflow Integration

## Overview

Integração do MCP **UI Skills** (`https://www.ui-skills.com/mcp`) com seleção dinâmica de skills por tarefa, antes do Stitch e antes do código frontend.

## Configuration (Cloud Agent)

- Endpoint HTTP: `https://www.ui-skills.com/mcp`
- Tools: `list_skills`, `get_skill`
- Cursor rules: `.cursor/rules/ui-skills.mdc`, `.cursor/rules/cotarco-workflow.mdc`
- Blueprint: `cotarco-commercial-manager/agents.md` §5.1

## Selection protocol

```text
list_skills(query…) → choose 2–4 skills → get_skill → apply → UI_SKILLS_SELECTED in handoff
```

Queries tipicas Cotarco: `baseline`, `accessibility`, `typography`, `table`, `form`, `dashboard`, `design review`.

## Gates

1. **Pré-Stitch** — seleção + `enhance-prompt` + Stitch MCP (máx. 3 ciclos).
2. **Pré-frontend** — seleção (ou reutilizar) + auditoria contra skills carregadas + implementação.

## References

- `.agents/rules/ui-skills.md`
- `cotarco-commercial-manager/prompts/MASTER_ORCHESTRATOR.md`
- `cotarco-commercial-manager/prompts/stitch/*`
- `cotarco-commercial-manager/prompts/agents/04-frontend.md`
