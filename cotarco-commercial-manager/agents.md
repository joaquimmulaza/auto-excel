# AGENTS.md — Operating Rules for AI Coding Agents

## 0. Ordem obrigatória de leitura e recon

Antes de qualquer alteração:

### 0.1 Ler

1. `context.md`
2. `agents.md`
3. `docs/requirements.md`
4. `docs/data-architecture.md`
5. `docs/application-flows.md`
6. `docs/routes-api.md`
7. `docs/stack-and-guardrails.md`
8. `docs/ui-wireframes-and-design-system.md`
9. `docs/testing-tdd.md`
10. `docs/mvp-backlog.md`
11. o documento específico da tarefa

### 0.2 Graphify MCP (obrigatório antes de código)

Repositório canónico: `joaquimmulaza/auto-excel` (`155ea5ab-4976-4975-83e1-efcba12a3061`).

1. Confirmar acesso com `list_repositories` se necessário.
2. Mapear impacto com `query_graph` e/ou `graphify_find`.
3. Para mudanças: `graphify_impact`, `graphify_callers` / `graphify_callees`, `graphify_tests_for`.
4. Só então ler ficheiros pontuais; grep amplo é fallback.

Não iniciar implementação sem compreender o estado atual do repositório **e** o blast radius no grafo.

## 1. Princípio central

**TDD first, code second.**

Para cada tarefa:

`entender → definir critério → escrever/ajustar teste → executar teste falhando → implementar mínimo → executar testes → refatorar → QA → documentar`.

## 2. Não fazer

- Não reescrever o projeto inteiro sem uma tarefa explícita.
- Não apagar lógica funcional do `auto-excel` por conveniência.
- Não colocar regras de negócio no frontend.
- Não chamar Gemini diretamente do browser.
- Não colocar secrets em código ou `.env` versionado.
- Não criar `if partner == ...` espalhados pelo sistema.
- Não publicar em serviços externos durante testes sem mock/fixture explícita.
- Não fazer alterações destrutivas em ficheiros de entrada.
- Não usar IA para substituir validações determinísticas.
- Não marcar tarefa como concluída sem testes e evidência de QA.

## 3. Regras de arquitetura

- Domínio independente de FastAPI/Next.js.
- Integrações atrás de adapters.
- Processamento Excel atrás de services/ports.
- API apenas orquestra casos de uso.
- UI consome API; não duplica regras.
- Banco é fonte de verdade para estado dos jobs, não o filesystem local.
- Storage guarda ficheiros; DB guarda metadados.

## 4. Regra de alterações

Antes de alterar schema, API, domínio ou UI global:

1. localizar todos os consumidores;
2. confirmar impacto;
3. escrever teste/regressão;
4. atualizar documentação correspondente;
5. implementar;
6. testar.

## 5. Stitch MCP — protocolo obrigatório para UI

Quando a tarefa envolve uma nova tela ou alteração estrutural de UI:

1. Ler `docs/ui-wireframes-and-design-system.md`.
2. Executar o **protocolo UI Skills MCP** (§5.1).
3. Criar/refinar o prompt Stitch (skill `enhance-prompt` + constraints das skills carregadas).
4. Chamar Stitch através do MCP disponível no ambiente do agente.
5. Gerar a tela.
6. Fazer QA visual contra os critérios de aceitação **e** as skills UI selecionadas.
7. Se aprovado: usar a proposta como referência para codificação (ainda com Portão 2 / §5.1).
8. Se reprovado: enviar feedback objetivo para Stitch e pedir nova iteração.
9. Repetir até aprovação ou atingir 3 ciclos; depois parar e pedir revisão humana.

**Nunca considerar o código exportado por Stitch como implementação final automaticamente.** Deve ser adaptado à arquitetura, acessibilidade e componentes do projeto.

### 5.1 UI Skills MCP — seleção dinâmica de skills

Endpoint: `https://www.ui-skills.com/mcp`. Tools: `list_skills`, `get_skill`.

Antes de Stitch **ou** de código frontend, o agente **navega o registry e escolhe** skills — não assume uma lista fixa:

```text
list_skills(query…) → escolher 2–4 skills → get_skill → aplicar → documentar UI_SKILLS_SELECTED
```

1. Chamar `list_skills` com 1–3 queries alinhadas à tarefa (ex.: `baseline`, `accessibility`, `typography`, `table`, `form`, `dashboard`, `design review`).
2. Selecionar **2–4** skills pelo `pathSlug`/`name` mais relevantes (ex. tipicos Cotarco: `ibelick/baseline-ui`, `jakubkrehel/better-accessibility`, `jakubkrehel/better-typography`, `vercel-labs/web-design-guidelines`).
3. Carregar cada uma com `get_skill`.
4. Aplicar no prompt Stitch (`enhance-prompt`) ou na implementação/QA frontend.
5. Incluir no handoff: `UI_SKILLS_SELECTED: <pathSlugs + motivo breve>`.
6. Se o MCP `ui-skills` estiver indisponível: **bloquear** trabalho de UI e reportar o erro.

### 5.3 Supabase Skills (obrigatório para DB / Auth / Storage / API com Supabase)

Skills oficiais em `.agents/skills/` (fonte: [supabase/agent-skills](https://github.com/supabase/agent-skills), docs: https://supabase.com/docs/guides/getting-started/ai-skills):

| Skill | Quando carregar |
|---|---|
| `supabase` | Qualquer tarefa Supabase (Database, Auth, Storage, RLS, migrations, CLI/MCP, clients SSR, troubleshooting) |
| `supabase-postgres-best-practices` | **Antes** de escrever/alterar SQL, schema, indexes, RLS, pooling, queries ou diagnóstico de performance |

Protocolo:

```text
Ler SKILL.md de supabase + supabase-postgres-best-practices
  → carregar references/ relevantes (query-*, security-*, schema-*, conn-*)
  → aplicar checklist de segurança Supabase (RLS, GRANT, service_role, views)
  → TDD / verificar com query de teste
  → handoff SUPABASE_SKILLS_USED
```

Regras:

1. Fases `02-database` e `03-api` (e qualquer migration/RLS/Auth/Storage) **devem** carregar ambas as skills antes de implementar.
2. Preferir Supabase MCP + CLI quando disponíveis; skills guiam o *como*, não substituem verificação.
3. Nunca expor `service_role` no frontend; RLS em todo schema exposto; não usar `user_metadata` para autorização.
4. Handoff: `SUPABASE_SKILLS_USED: supabase,supabase-postgres-best-practices` (+ references lidas se aplicável).

Instalação / refresh: `npx skills add supabase/agent-skills` (ou re-copiar de `supabase/agent-skills` se a CLI falhar). Ver `SOURCE.md` em cada skill.

## 6. QA de Stitch

Critérios mínimos:

- usa a paleta de produto;
- tipografia e espaçamento consistentes;
- hierarquia clara;
- estados loading/empty/error contemplados;
- tabelas legíveis;
- ações críticas visualmente distintas;
- navegação coerente;
- sem informação inventada;
- sem mock de funcionalidades que não existem sem marcar como protótipo;
- desktop 1440px aceitável;
- mobile 390px sem quebra funcional nas telas prioritárias.

## 7. Evidência obrigatória e Handoff

Todo agente deve terminar uma tarefa fornecendo obrigatoriamente o handoff no formato canónico de 9 campos:

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: <id>
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
UI_SKILLS_SELECTED: <pathSlugs + motivo | n/a se tarefa não-UI>
SUPABASE_SKILLS_USED: <supabase,supabase-postgres-best-practices | n/a>
```

## 8. Handoffs

Nunca depender de memória de conversa. Toda informação necessária deve estar:

- no código;
- em `context.md`;
- em documentação;
- em ADR;
- ou no comentário do PR/commit.

## 9. Convencional de commits

Usar Conventional Commits:

- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `docs:`
- `chore:`
- `security:`

Evitar commits gigantes.

## 10. Graphify MCP e CLI — Navegação e Manutenção da Codebase

Antes de modificar código ou arquitetura, usar Graphify. Preferir **MCP Cloud** quando disponível; CLI é fallback local.

**Repo:** `joaquimmulaza/auto-excel` — passar `repository_id` como UUID ou `owner/name` nas tools.

### MCP (Cloud Agent — preferido)

| Tool | Uso |
|---|---|
| `list_repositories` | Confirmar repos acessíveis e estado do índice |
| `query_graph` | Pergunta em linguagem natural sobre comportamento/arquitetura |
| `graphify_find` | Localizar definição de símbolo/classe/função |
| `graphify_node` | Corpo + vizinhos imediatos de um símbolo |
| `graphify_callers` / `graphify_callees` | Quem chama / o que é chamado |
| `graphify_impact` | Blast radius direto (callers + callees) |
| `graphify_tests_for` | Testes ligados a símbolo/ficheiro |
| `graphify_file_neighbors` | Dependências e dependentes de um ficheiro |
| `shortest_path` / `graphify_trace` | Caminho entre dois símbolos |

### CLI (fallback local)

- `graphify query "<pergunta ou termo>"`
- `graphify path "<origem>" "<destino>"`
- `graphify explain "<componente>"`

### Manutenção do grafo

- Após mudanças estruturais de código: `graphify update .` (AST-only, sem custo de LLM) quando a CLI estiver disponível.
- Não editar `graphify-out/graph.json` à mão; usar merge driver / hooks documentados no README.

## 11. Matriz de Atribuição de Skills (Isolamento por Escopo)

Para evitar poluição de contexto e cruzamento indevido de regras entre camadas, cada agente/etapa opera estritamente com as suas skills atribuídas:

| Agente / Escopo | Skills Atribuídas | Responsabilidade Principal |
|---|---|---|
| `00-bootstrap-audit` | `tlc-spec-driven`, `web-quality-audit` | Auditoria inicial de repositório, baseline e quality gates |
| `01-domain-tdd` | `coding-guidelines`, `best-practices` | Extração do motor de domínio, regras determinísticas de negócio e TDD puro |
| `02-database` | `supabase`, `supabase-postgres-best-practices`, `security-best-practices` (Backend) | Schema Supabase/PostgreSQL, migrations, RLS e modelos relacionais (§5.3) |
| `03-api` | `supabase`, `supabase-postgres-best-practices`, `security-best-practices` (Next.js/FastAPI), `tlc-spec-driven` | Endpoints FastAPI, schemas Pydantic, RBAC, Auth/Storage Supabase, idempotência (§5.3) |
| `04-frontend` | `shadcn-ui`, `frontend-blueprint`, `taste-design` + **UI Skills MCP** (§5.1) | Interface Next.js; selecionar skills MCP por tarefa antes de codificar |
| `stitch/*` | `enhance-prompt`, `stitch-design` + **UI Skills MCP** (§5.1) | Geração visual; `list_skills` → escolher → `get_skill` antes do Stitch |
| `05-gemini` | `technical-design-doc-creator`, `security-best-practices` | Serviços de IA assistiva (Gemini), structured outputs e sanitização |
| `06-integrations` | `playwright-skill`, `core-web-vitals` | Testes E2E com Playwright, adapters de integração externa e performance web |

### Regra de Ouro do Isolamento
- Nenhum subagente pode invocar ou carregar skills fora do seu escopo designado.
- Nenhuma regra financeira ou de stock pode utilizar modelos de linguagem (LLM); toda a lógica de negócio é 100% determinística em Python.
- Nenhum teste é considerado aprovado sem log real de execução no terminal (`pytest`).

