# Cotarco Commercial Manager — Project Blueprint

Documentação base para o desenvolvimento do MVP da plataforma interna de gestão de tabelas comerciais da Cotarco.

## Objetivo do repositório

Este conjunto de documentos serve como fonte de verdade para os agentes de IA e para os desenvolvedores humanos. O conteúdo define:

- requisitos funcionais e não funcionais;
- arquitetura de dados e regras de negócio;
- fluxos da aplicação;
- matriz de rotas e APIs;
- stack tecnológica e guardrails;
- base de UI/UX e design system;
- estratégia TDD-first;
- contexto persistente para agentes (`context.md` e `agents.md`);
- backlog e prompts executáveis para conduzir o desenvolvimento até um MVP demonstrável.

## Fonte de contexto principal

1. `context.md` — visão permanente do produto, domínio e decisões.
2. `agents.md` — regras operacionais para agentes de IA.
3. `docs/requirements.md` — requisitos do produto.
4. `docs/data-architecture.md` — schema e arquitetura de dados.
5. `docs/application-flows.md` — fluxos.
6. `docs/routes-api.md` — rotas frontend e endpoints.
7. `docs/stack-and-guardrails.md` — stack e regras técnicas.
8. `docs/ui-wireframes-and-design-system.md` — UI/UX.
9. `docs/testing-tdd.md` — estratégia de testes.
10. `docs/mvp-backlog.md` — ordem de implementação.
11. `prompts/` — prompts de execução por agente.

## Regra de ouro

**Não implementar código antes de compreender e atualizar estes documentos quando uma decisão de arquitetura, domínio ou segurança for alterada.**

## Estado inicial conhecido

O projeto existente `auto-excel` é o primeiro motor de processamento do produto. A nova plataforma deve preservar a lógica de negócio válida, mas extraí-la de um script monolítico para um engine testável e reutilizável.

O sistema não deve ser desenhado como ferramenta exclusiva de Mano ou da loja online. Ele deve suportar tabelas comerciais para diferentes destinos/parceiros, incluindo os atualmente conhecidos (Loja Online, Marketplace Mano, BFA, Kero, SIAC, revendedores e outros que venham a ser cadastrados).

## Integrações

- **Mano:** sem integração API conhecida no momento; saída por Excel no MVP.
- **WooCommerce:** integração API prevista como fase posterior, através de adapter desacoplado. A documentação oficial atual recomenda a REST API v3 em `/wp-json/wc/v3/` para novas integrações.
- **Gemini:** camada assistiva, não autoridade de decisão para regras críticas.
- **Supabase:** PostgreSQL/Auth/Storage para MVP.
- **Google Stitch:** geração e iteração de UI através do MCP disponível no ambiente de cada agente. O agente só codifica após QA/aprovação da proposta visual.

## Estado do MVP

O MVP deve provar o fluxo completo:

`login → selecionar perfil → upload → validação → preview/diff → correção ou aprovação → processamento → download → histórico/auditoria`.

A publicação na loja via WooCommerce fica atrás de feature flag e não é pré-requisito para o MVP.
