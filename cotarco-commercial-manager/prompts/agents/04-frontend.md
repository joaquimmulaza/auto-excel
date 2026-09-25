# Agent Prompt A50-A55 — Frontend after Stitch Approval

Leia `context.md`, `agents.md`, `docs/ui-wireframes-and-design-system.md` e os resultados aprovados do Stitch.

## Missão

Implementar frontend Next.js do MVP utilizando componentes reais do projeto.

## Regra

1. **Portão Obrigatório UI Skills**: Antes de escrever qualquer código, validar padrões contra o MCP `ui-skills` (acessibilidade WCAG AA, `tabular-nums` para tabelas/preços, touch targets $\ge 44\text{px}$, skeletons estruturais).
2. Não copiar cegamente código exportado por Stitch. Reproduzir a intenção visual dentro da arquitetura e do design system.

## Ordem

1. app shell/auth;
2. dashboard;
3. new job/upload;
4. validation/review;
5. approval/history/download;
6. empty/loading/error/accessibility.

## Testes

Antes de cada componente crítico, criar testes RTL.

Depois do fluxo completo, criar Playwright E2E.

## UX

- usar skeleton no first load;
- spinner para ações de curto prazo;
- feedback de errors inline;
- tabela com filtros;
- não duplicar regras do backend.

## Responsividade

Desktop-first, mas sem quebrar em 1024px e telas prioritárias usáveis a 390px.
