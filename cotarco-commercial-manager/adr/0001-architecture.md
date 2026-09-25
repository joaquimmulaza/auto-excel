# ADR-0001 — Arquitetura inicial

## Status

Accepted for MVP, 23/09/2026.

## Contexto

O sistema nasceu como script Python que processa Excel. A nova versão precisa ser utilizada por Comercial via browser, mantendo o motor Python e preparando múltiplos perfis/destinos.

## Decisão

Usar:

- Next.js/TypeScript no frontend;
- FastAPI/Python no backend;
- engine de domínio Python reutilizável;
- Supabase PostgreSQL/Auth/Storage;
- adapters para destinos;
- Gemini assistivo;
- Stitch MCP para design/iteração de UI.

## Consequências

Positivas:

- preserva o investimento do `auto-excel`;
- separa domínio de interface;
- permite múltiplos destinos;
- suporta integração WooCommerce futura;
- simplifica colaboração de agentes.

Negativas:

- duas linguagens principais;
- necessidade de contratos API;
- CI mais abrangente.
