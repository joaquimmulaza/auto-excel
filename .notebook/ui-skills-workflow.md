# UI Skills MCP & Workflow Integration

## Overview
Integração do servidor MCP **UI Skills** (`https://www.ui-skills.com/mcp`) para impor portões de qualidade de engenharia de design antes da geração visual no Stitch e antes da escrita de código no frontend.

## Configuration
- Server configurado em [mcp_config.json](file:///C:/Users/MARKETING%20DESIGNER01/.gemini/antigravity-ide/mcp_config.json) via endpoint `https://www.ui-skills.com/mcp`.
- Ferramentas disponíveis via MCP: `list_skills`, `get_skill`.

## Mandatory Gates
1. **Gate 1: Pré-Stitch (UI Skills + Enhance-Prompt)**:
   - Local: [.agents/rules/ui-skills.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.agents/rules/ui-skills.md) (L14-L27), [00-design-system.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/cotarco-commercial-manager/prompts/stitch/00-design-system.md) (L9-L15).
   - Ação: 
     - Consultar `ui-skills` para enriquecer prompts com regras de contraste WCAG AA, tipografia e densidade de informação enterprise.
     - Processar pela skill [enhance-prompt](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.agents/skills/enhance-prompt/SKILL.md) para injetar o bloco estruturado `DESIGN SYSTEM (REQUIRED)` e `Page Structure` numerada com keywords específicas de componentes.
2. **Gate 2: Pré-Implementação de Código**:
   - Local: [.agents/rules/ui-skills.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.agents/rules/ui-skills.md) (L26-L40), [04-frontend.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/cotarco-commercial-manager/prompts/agents/04-frontend.md) (L10-L13).
   - Ação: Auditar componentes para garantir `tabular-nums` em dados, touch targets $\ge 44\text{px}$, skeletons estruturais e ausência de slop.
3. **Orquestração**:
   - Registado em [MASTER_ORCHESTRATOR.md](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/cotarco-commercial-manager/prompts/MASTER_ORCHESTRATOR.md) (L38-L56).
