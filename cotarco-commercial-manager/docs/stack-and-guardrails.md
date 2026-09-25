# Stack Tecnológica & Regras de Ouro (Tech Stack & Guardrails)

## 1. Stack oficial do MVP

| Camada | Tecnologia | Papel |
|---|---|---|
| Web app | Next.js + TypeScript | UI |
| UI | Tailwind + shadcn/ui | Design system/componentes |
| Estado servidor | TanStack Query | cache/fetch |
| Tabelas | TanStack Table | grandes datasets |
| Forms | React Hook Form + Zod | validação de UI |
| Backend | FastAPI | API/casos de uso |
| Domain | Python | regras/processamento |
| Excel | Pandas + OpenPyXL | ETL |
| DB | Supabase PostgreSQL | persistência |
| Auth | Supabase Auth | identidade |
| Storage | Supabase Storage | Excel/artefactos |
| ORM/migrations | SQLAlchemy 2 + Alembic | DB controlado |
| Testes Python | pytest | unit/integration |
| Testes React | Vitest + RTL | component/unit |
| E2E | Playwright | fluxo real |
| Lint Python | Ruff | qualidade |
| Typing | mypy/pyright | contratos |
| CI | GitHub Actions | quality gate |
| Frontend hosting | Vercel | deploy |
| Backend hosting | Cloud Run | deploy |
| AI | Gemini + Google GenAI SDK | assistência |
| UI generation | Google Stitch via MCP | prototipação/design |

## 2. Gestão de dependências

Frontend:

- `pnpm`;
- lockfile obrigatório;
- versões major fixadas/conhecidas.

Backend:

- `uv`;
- lockfile obrigatório;
- dependências atualizadas de forma controlada.

## 3. Guardrail #1 — Domínio primeiro

A lógica de negócio não pode depender de `Request`, `Response`, React, Supabase ou filesystem.

Exemplo:

```python
result = process_price_table(input_table, comparison_catalog, rules)
```

Esse caso de uso deve ser testável sem subir FastAPI.

## 4. Guardrail #2 — Configuração, não hardcode

Não criar regras por parceiro assim:

```python
if partner == "BFA":
    ...
```

Preferir:

```text
CommercialProfile
ProfileRule
Template
Adapter
```

## 5. Guardrail #3 — IA não decide dinheiro

Gemini não pode:

- escolher preço final;
- escolher stock final;
- ignorar blocker;
- aprovar operação;
- chamar integração externa diretamente.

## 6. Guardrail #4 — Secrets

Nunca:

```text
NEXT_PUBLIC_GEMINI_API_KEY
NEXT_PUBLIC_WC_CONSUMER_SECRET
```

As credenciais ficam exclusivamente no backend/secret manager.

## 7. Guardrail #5 — Integrações isoladas

Estrutura:

```text
integrations/
├── mano/
├── woocommerce/
└── future_partner/
```

Nenhum service de domínio deve importar SDK do WooCommerce.

## 8. Guardrail #6 — Mutação crítica exige aprovação

Pré-visualizar primeiro:

`prepare → validate → preview → approve → apply → verify`.

## 9. Guardrail #7 — Idempotência

Cada operação crítica recebe idempotency key e/ou execution id.

Repetições seguras não devem duplicar outputs ou mutações externas.

## 10. Guardrail #8 — Inputs são não confiáveis

Ficheiros enviados devem ser tratados como dados não confiáveis.

- extensão allowlist;
- tamanho máximo;
- MIME verificado;
- parser protegido;
- sem execução de macros;
- sem abertura de hyperlinks como parte do processamento;
- sanitização de strings.

## 11. Guardrail #9 — Não sobrescrever originais

Nunca modificar o Excel original enviado pelo utilizador.

## 12. Guardrail #10 — Auditoria

Toda ação administrativa/crítica gera audit log.

## 13. Guardrail #11 — Erros determinísticos

Cada erro de domínio possui código:

```text
MISSING_COLUMN
EMPTY_REFERENCE
DUPLICATE_REFERENCE
INVALID_PRICE
ZERO_PRICE
NEGATIVE_STOCK
PRICE_VARIATION_BLOCKED
PROFILE_RULE_VIOLATION
```

A UI apresenta mensagem amigável derivada do código.

## 14. Guardrail #12 — TDD first

Não aceitar PR de feature crítica sem testes do caso de uso.

## 15. Guardrail #13 — Design by Stitch, implementation by codebase

Stitch é fonte de exploração visual, não autoridade arquitetural.

O agente:

`prompt Stitch → QA visual → aprovação → adaptar componentes → testes → implementação`.

## 16. Guardrail #14 — Feature flags

WooCommerce e outras integrações críticas começam desativadas.

## 17. Guardrail #15 — Observabilidade mínima

Toda request deve possuir `request_id`/trace id.

Jobs devem possuir `job_id` em logs.

## 18. Guardrail #16 — Branches

- `main` protegida;
- feature branches;
- PR obrigatório;
- CI obrigatório;
- sem push direto em `main` por agentes.

## 19. Guardrail #17 — Definition of Ready

Uma tarefa só pode entrar em desenvolvimento quando possui:

- objetivo;
- escopo;
- critérios de aceitação;
- dependências;
- telas/API afetadas;
- testes esperados.

## 20. Guardrail #18 — Definition of Done

Feature concluída = código + testes + QA + docs + evidência + sem regressões.

## 21. Notas de plataforma atuais

O plano Free do Supabase disponibiliza atualmente PostgreSQL, 500 MB de base por projeto, 1 GB de file storage, 50.000 MAU e 5 GB de egress; também informa que projetos Free podem ser pausados após uma semana de inatividade e que não há backups automáticos no Free. Essas quotas devem ser tratadas como snapshot de setembro de 2026, não como garantia permanente.

O WooCommerce documenta atualmente a REST API v3 como a versão recomendada para novas integrações e disponibiliza operações de produtos e batch.

O Google Cloud lista atualmente o Stitch (Beta) como servidor MCP em `https://stitch.googleapis.com/mcp`.

O Gemini Structured Outputs permite respostas aderentes a JSON Schema e integração com Pydantic/Zod; usar isso nas funcionalidades de IA estruturada.
