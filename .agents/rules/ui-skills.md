---
trigger: always_on
description: Mandatory UI Skills MCP selection + gates before Stitch prompts and frontend code.
---

# UI Skills Workflow Rules (Mandatory Quality Gates)

MCP **UI Skills** (`https://www.ui-skills.com/mcp`) is the authority for interface quality, design engineering, and accessibility.

No Stitch prompt and no frontend code without the selection protocol below.

---

## Protocolo de seleção (obrigatório)

Para cada tarefa de UI (Stitch ou frontend):

```text
list_skills(query…)  →  escolher 2–4 skills  →  get_skill(name…)  →  aplicar + documentar
```

1. **Navegar o registry** com `list_skills` e queries alinhadas à tarefa (ex.: `baseline`, `accessibility`, `typography`, `table`, `form`, `dashboard`).
2. **Escolher 2–4 skills** adequadas — não carregar o catálogo inteiro. Critérios:
   - anti-slop / polish → `ibelick/baseline-ui`
   - acessibilidade → `jakubkrehel/better-accessibility`, `addyosmani/accessibility`, `ibelick/fixing-accessibility`
   - tipografia / dados → `jakubkrehel/better-typography` (e skills com `tabular-nums`)
   - review / guidelines → `vercel-labs/web-design-guidelines`, `superfuture/design-review`
3. **Carregar** cada skill escolhida com `get_skill`.
4. **Documentar** no handoff: `UI_SKILLS_SELECTED: <pathSlugs + motivo>`.
5. Se o MCP falhar: **parar** trabalho UI e reportar o erro (não inventar guidelines).

---

## Portão 1: Pré-Stitch

1. Executar o protocolo de seleção.
2. Processar com [enhance-prompt](.agents/skills/enhance-prompt/SKILL.md):
   - Web Desktop-first; vibe enterprise Cotarco.
   - `DESIGN SYSTEM (REQUIRED)` com `#FF3C1D`, `#6B6363`, `#FFFFFF`, `#000000`.
   - `Page Structure` numerada + vocabulário UI/UX preciso.
3. Injetar no prompt Stitch as constraints das skills carregadas (contraste WCAG AA, densidade, hierarquia, estados).

---

## Portão 2: Pré-implementação frontend

1. Executar o protocolo de seleção (pode reutilizar skills do Portão 1 se ainda válidas).
2. Auditar contra as skills carregadas:
   - touch targets ≥ 44×44px, `:focus-visible`, labels, status texto+cor
   - `tabular-nums` em preços/quantidades
   - `text-balance` / `text-pretty`, skeletons estruturais
3. Implementar a intenção Stitch aprovada sem slop; não misturar sistemas de primitives sem necessidade.
