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
2. Criar prompt específico para Stitch em `prompts/stitch/` ou usar o prompt fornecido pela tarefa.
3. Chamar Stitch através do MCP disponível no ambiente do agente.
4. Gerar a tela.
5. Fazer QA visual contra os critérios de aceitação.
6. Se aprovado: usar a proposta como referência para codificação.
7. Se reprovado: enviar feedback objetivo para Stitch e pedir nova iteração.
8. Repetir até aprovação ou atingir 3 ciclos; depois parar e pedir revisão humana.

**Nunca considerar o código exportado por Stitch como implementação final automaticamente.** Deve ser adaptado à arquitetura, acessibilidade e componentes do projeto.

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
| `02-database` | `security-best-practices` (Backend) | Schema Supabase/PostgreSQL, migrations, RLS e modelos relacionais |
| `03-api` | `security-best-practices` (Next.js/FastAPI), `tlc-spec-driven` | Endpoints FastAPI, schemas Pydantic, RBAC, idempotência e rotas |
| `04-frontend` | `shadcn-ui`, `frontend-blueprint`, `taste-design` | Interface Next.js, componentes shadcn/ui, acessibilidade e design system |
| `05-gemini` | `technical-design-doc-creator`, `security-best-practices` | Serviços de IA assistiva (Gemini), structured outputs e sanitização |
| `06-integrations` | `playwright-skill`, `core-web-vitals` | Testes E2E com Playwright, adapters de integração externa e performance web |

### Regra de Ouro do Isolamento
- Nenhum subagente pode invocar ou carregar skills fora do seu escopo designado.
- Nenhuma regra financeira ou de stock pode utilizar modelos de linguagem (LLM); toda a lógica de negócio é 100% determinística em Python.
- Nenhum teste é considerado aprovado sem log real de execução no terminal (`pytest`).

