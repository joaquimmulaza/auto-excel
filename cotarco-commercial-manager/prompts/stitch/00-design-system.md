# Stitch Prompt — Design System CCM

## Contexto

Criar o design system base do Cotarco Commercial Manager, uma aplicação interna enterprise para gestão de tabelas comerciais.

A aplicação será usada principalmente em desktop por equipa Comercial/Operador. O foco é produtividade, clareza de dados e segurança operacional.

## Validação Pré-Stitch Obrigatória (§5.1–5.2)

Antes de submeter este prompt ao Stitch:

1. Ler `.stitch/DESIGN.md` (criar/atualizar com `taste-design` brand Cotarco se em falta).
2. UI Skills MCP: `list_skills` (`baseline`, `accessibility`, `typography`, `design`) → escolher 2–4 → `get_skill`.
3. `enhance-prompt` + bloco Section 6 de `.stitch/DESIGN.md`.
4. Gerar via `stitch-design` / Stitch MCP; stage em `.stitch/designs/design-system.*`; atualizar `SITE.md` / `metadata.json`.
5. Handoff: `UI_SKILLS_SELECTED` + `STITCH_SKILLS_USED`.

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
