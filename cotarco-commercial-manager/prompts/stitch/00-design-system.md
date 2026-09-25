# Stitch Prompt — Design System CCM

## Contexto

Criar o design system base do Cotarco Commercial Manager, uma aplicação interna enterprise para gestão de tabelas comerciais.

A aplicação será usada principalmente em desktop por equipa Comercial/Operador. O foco é produtividade, clareza de dados e segurança operacional.

## Validação Pré-Stitch Obrigatória (UI Skills & Enhance-Prompt)

Antes de submeter este prompt ao Stitch:
1. Consultar o MCP `ui-skills` (skills `frontend-design`, `interface-design`, `baseline-ui` e playbooks de densidade/acessibilidade) para garantir conformidade de contrastes WCAG AA e espaçamento semântico.
2. Processar a estrutura com a skill [enhance-prompt](file:///c:/Users/MARKETING%20DESIGNER01/Downloads/up_prices/.agents/skills/enhance-prompt/SKILL.md) para gerar a especificação formatada em `DESIGN SYSTEM (REQUIRED)` e `Page Structure` numerada com componentes de alta densidade.

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
