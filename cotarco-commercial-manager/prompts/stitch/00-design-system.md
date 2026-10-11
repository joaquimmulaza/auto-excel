# Stitch Prompt — Design System CCM

## Contexto

Criar o design system base do Cotarco Commercial Manager, uma aplicação interna enterprise para gestão de tabelas comerciais.

A aplicação será usada principalmente em desktop por equipa Comercial/Operador. O foco é produtividade, clareza de dados e segurança operacional.

## Validação Pré-Stitch Obrigatória (UI Skills MCP + Enhance-Prompt)

Antes de submeter este prompt ao Stitch (`agents.md` §5.1):

1. **Navegar** com `list_skills` (queries sugeridas: `baseline`, `accessibility`, `typography`, `design`).
2. **Escolher 2–4 skills** adequadas ao design system (ex. tipicos: `ibelick/baseline-ui`, a11y, typography, web-design-guidelines) — não assumir lista fixa.
3. **Carregar** cada uma com `get_skill` e aplicar as constraints.
4. Processar com a skill `enhance-prompt` (`.agents/skills/enhance-prompt/SKILL.md`): `DESIGN SYSTEM (REQUIRED)` + `Page Structure` numerada, densidade enterprise.
5. Documentar `UI_SKILLS_SELECTED` no handoff.

## Branding obrigatório

Use exclusivamente como base:

- `#FF3C1D` — brand/accent;
- `#6B6363` — secondary;
- `#FFFFFF` — surface;
- `#000000` — ink.

Criar tokens semânticos para success/warning/error/info sem abandonar a identidade base.

## Componentes

Propor:

- buttons;
- inputs;
- select/combobox;
- badges;
- cards;
- alerts;
- tabs;
- dialogs;
- dropzone;
- data table;
- progress;
- skeleton;
- empty states;
- sidebar/topbar.

## UX

Denso em informação, mas limpo. Bordas discretas, sombras leves, tipografia profissional, hierarquia forte. Sem gradientes excessivos, sem glassmorphism, sem animações decorativas.

Criar variantes para light theme primeiro. Dark theme pode ser contemplado estruturalmente, mas não é requisito bloqueador do MVP.

## QA

A proposta será rejeitada se:

- parecer uma landing page;
- não priorizar dados/tabelas;
- esconder ações críticas;
- usar cores fora do sistema sem justificação;
- não suportar estados de erro/loading.
