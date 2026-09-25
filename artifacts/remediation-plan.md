# Cotarco Commercial Manager — Remediation Plan

> **Generated:** 2026-09-25  
> **Phase:** AUDIT → DELEGATE → COLLECT → SYNTHESIZE → PLAN  
> **Status:** READ-ONLY — Nothing has been modified.  
> **Sources:** audit-rules.md · audit-git-artifacts.md · audit-graphify.md · audit-documentation.md

---

## Executive Summary

Four specialized subagents audited the full development environment in parallel:

| Auditor | Report | Findings (raw) |
|---------|--------|----------------|
| Rules Auditor | [audit-rules.md](audit-rules.md) | 18 |
| Git & Artifacts Auditor | [audit-git-artifacts.md](audit-git-artifacts.md) | 6 |
| Graphify Auditor | [audit-graphify.md](audit-graphify.md) | 10 |
| Documentation Auditor | [audit-documentation.md](audit-documentation.md) | 19 |
| **Total (after deduplication)** | | **40 unique findings** |

**Deduplication note:** Graphify cache tracked in git (R-GIT-01) was independently reported by both the Git Auditor and the Graphify Auditor — consolidated into one entry. The missing wiki reference was reported by both the Rules Auditor and the Graphify Auditor — consolidated similarly.

### Risk Distribution

| Priority | Count |
|----------|-------|
| 🔴 P0 — Critical (act before any implementation) | 10 |
| 🟠 P1 — High (act before database/API phases) | 8 |
| 🟡 P2 — Medium (act before UI phases) | 11 |
| 🟢 P3 — Low / Housekeeping | 11 |

---

## Classification Legend

| Category | Meaning |
|----------|---------|
| **SAFE TO FIX** | Clear, unambiguous technical error. No business decision needed. Can be fixed by an agent with a targeted PR. |
| **NEEDS REVIEW** | Technical issue, but requires developer confirmation of intent or preferred approach before changing. |
| **ARCHITECTURE/BUSINESS DECISION** | Requires explicit product-level or team-level decision. Cannot be resolved by an agent alone. |

---

## 🔴 P0 — CRITICAL (Must resolve before implementation begins)

---

### REM-001

| Field | Value |
|-------|-------|
| **ID** | REM-001 |
| **Problema** | 552 ficheiros de `node_modules` do Playwright estão commitados ao git (`.agents/skills/playwright-skill/node_modules/`) |
| **Fonte** | Git & Artifacts Auditor |
| **Impacto** | Repo artificialmente inflado (+3.90 MiB em 4 commits); binários Windows (`.cmd`, `.ps1`) comprometem portabilidade cross-platform; `git clone` lento; histórico poluído |
| **Correção proposta** | 1. Adicionar `node_modules/` ao `.gitignore`. 2. `git rm -r --cached .agents/skills/playwright-skill/node_modules/`. 3. Opcional: `git filter-repo` para expurgar do histórico (só 4 commits — custo baixo). |
| **Risco** | BAIXO — o `package.json` e `package-lock.json` existem; `npm install` restaura tudo |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Manutenção Git |
| **Necessita aprovação humana?** | Sim — confirmar antes de rewrite de histórico |

---

### REM-002

| Field | Value |
|-------|-------|
| **ID** | REM-002 |
| **Problema** | 64 ficheiros de cache do Graphify estão commitados (`graphify-out/cache/ast/` e `graphify-out/cache/semantic/`) |
| **Fonte** | Git & Artifacts Auditor + Graphify Auditor (convergência) |
| **Impacto** | Cache efémera regenerável gratuitamente está a poluir o histórico git; muda em cada `graphify update .`; causa noise em cada `git status` e `git diff` |
| **Correção proposta** | 1. Adicionar `graphify-out/cache/` ao `.gitignore`. 2. `git rm -r --cached graphify-out/cache/`. 3. `git rm --cached graphify-out/.graphify_*` (7 ficheiros de estado interno). |
| **Risco** | BAIXO — regenerável. Não afecta o MCP |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Manutenção Git |
| **Necessita aprovação humana?** | Não |

---

### REM-003

| Field | Value |
|-------|-------|
| **ID** | REM-003 |
| **Problema** | Snapshot diário `graphify-out/2026-09-25/` commitado — acumulará indefinidamente a cada run |
| **Fonte** | Git & Artifacts Auditor + Graphify Auditor (convergência) |
| **Impacto** | Se criado a cada execução, o repo acumula centenas de MB em snapshots duplicados. Já ~384 KB no primeiro dia. |
| **Correção proposta** | 1. Adicionar `graphify-out/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/` ao `.gitignore`. 2. `git rm -r --cached graphify-out/2026-09-25/`. 3. Usar git tags para versioning em vez de snapshots de directoria. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Manutenção Git |
| **Necessita aprovação humana?** | Não |

---

### REM-004

| Field | Value |
|-------|-------|
| **ID** | REM-004 |
| **Problema** | `.gitignore` cobre apenas 7 extensões Excel — criticamente incompleto para um projecto Next.js + FastAPI + Python |
| **Fonte** | Git & Artifacts Auditor |
| **Impacto** | `node_modules/`, `__pycache__/`, `.next/`, `.env*`, `*.pyc`, build artifacts, e Graphify outputs são todos desprotegidos; risco de commit acidental de secrets |
| **Correção proposta** | Substituir `.gitignore` por versão completa cobrindo: Node.js (node_modules, .next, dist), Python (__pycache__, .venv, *.pyc), ambiente (.env, .env.local, .env.*.local), Graphify (cache/, snapshots, graph.html), IDEs, OS files, e `artifacts/`. |
| **Risco** | BAIXO — acção aditiva; não remove ficheiros já tracked |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Manutenção Git |
| **Necessita aprovação humana?** | Não |

---

### REM-005

| Field | Value |
|-------|-------|
| **ID** | REM-005 |
| **Problema** | 4 ficheiros de rules com glob morto `cotarco-client//` — directoria que não existe |
| **Fonte** | Rules Auditor (FIND-001 a FIND-004) |
| **Impacto** | ~60% do conteúdo das rules `frontend-architecture.md`, `frontend.md`, `nextjs.md`, `ui-ux.md` é completamente inerte — nunca activa para nenhum ficheiro. Agentes de frontend operam sem guardrails. |
| **Correção proposta** | Curto prazo: mudar `trigger: glob` para `always_on: true` nestas 4 rules como placeholder. Longo prazo: actualizar para o path real quando o frontend for scaffolded. |
| **Risco** | MÉDIO — activar `always_on` aumenta contexto dos agentes em cada chamada |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Sim — confirmar nome final da directoria frontend |

---

### REM-006

| Field | Value |
|-------|-------|
| **ID** | REM-006 |
| **Problema** | `frontend.md` linha 35: directiva Svelte `class:` incluída em projecto React/JSX |
| **Fonte** | Rules Auditor (FIND-013) |
| **Impacto** | Causará erro de compilação se seguida por um agente. Sintaxe inválida em JSX. Contaminação de projecto anterior (Svelte). |
| **Correção proposta** | Substituir por `cn()` do `shadcn/ui` / `clsx` como padrão para classes condicionais em React. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-007

| Field | Value |
|-------|-------|
| **ID** | REM-007 |
| **Problema** | `ui-ux.md` impõe mobile-first; `context.md §8` impõe explicitamente desktop-first para esta ferramenta interna |
| **Fonte** | Rules Auditor (FIND-012) |
| **Impacto** | Contradição directa que afecta todas as decisões de UI. Agentes produzirão designs inconsistentes dependendo de qual regra consultarem primeiro. |
| **Correção proposta** | Actualizar `ui-ux.md` para desktop-first (1440px primary, 390px sem quebra funcional) em conformidade com `context.md`. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-008

| Field | Value |
|-------|-------|
| **ID** | REM-008 |
| **Problema** | `approvals.action = REJECTED` não tem correspondência em `job_status` — estado de transição indefinido |
| **Fonte** | Documentation Auditor (A-04) |
| **Impacto** | Bloqueante para implementação. A rejeição de uma aprovação não tem destino no estado machine do job. Criará bug de runtime no primeiro fluxo de aprovação. |
| **Correção proposta** | Criar ADR-0003 para decidir: volta a `PENDING_REVIEW`? Transita para `REJECTED` (novo status)? Requer resubmissão (novo job)? |
| **Risco** | ALTO — decisão de negócio com impacto no schema DB |
| **Categoria** | ARCHITECTURE/BUSINESS DECISION |
| **Agente responsável** | Product Owner + Tech Lead |
| **Necessita aprovação humana?** | Sim — obrigatório |

---

### REM-009

| Field | Value |
|-------|-------|
| **ID** | REM-009 |
| **Problema** | ERD usa `profiles` mas a tabela está definida como `commercial_profiles` — no mesmo documento, mesma secção |
| **Fonte** | Documentation Auditor (C-01) |
| **Impacto** | Inconsistência no schema que causará erro de FK ou migration errada se seguida literalmente. |
| **Correção proposta** | Normalizar para `commercial_profiles` em todo o `data-architecture.md` (nome correcto, mais descritivo). |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-010

| Field | Value |
|-------|-------|
| **ID** | REM-010 |
| **Problema** | `prompts/stitch/00-design-system.md` contém path absoluto Windows específico de uma máquina: `file:///c:/Users/MARKETING DESIGNER01/...` |
| **Fonte** | Documentation Auditor (B-02) |
| **Impacto** | Prompt de Stitch inutilizável em qualquer outra máquina ou agente. Vaza estrutura do filesystem da máquina de desenvolvimento. |
| **Correção proposta** | Substituir path absoluto por referência relativa ao projecto (e.g., `.agents/skills/design-md/`) ou remover a dependência externa do prompt. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

## 🟠 P1 — HIGH (Resolver antes das fases de DB/API)

---

### REM-011

| Field | Value |
|-------|-------|
| **ID** | REM-011 |
| **Problema** | 4-way conflito de tipos de commit: `cotarco-git-workflow.md` (inclui `ui`), `git-commit-rules.md` (só `feat/fix/refactor`), `frontend.md` (mais amplo), `agents.md §9` (inclui `security`) |
| **Fonte** | Rules Auditor (FIND-005) |
| **Impacto** | Agentes produzem commits com tipos incompatíveis; histórico inconsistente; CI/CD e changelogs automatizados quebram. |
| **Correção proposta** | Canonizar `agents.md §9` como fonte única de tipos de commit; todos os outros ficheiros devem referenciar esse documento em vez de redefinir. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-012

| Field | Value |
|-------|-------|
| **ID** | REM-012 |
| **Problema** | `cotarco-git-workflow.md` usa formato `[Type]: Description` (com brackets). Todos os outros usam `type: description` (Conventional Commits standard). |
| **Fonte** | Rules Auditor (FIND-007) |
| **Impacto** | Commits malformados. Ferramentas de release automation (semantic-release, conventional-changelog) não reconhecem o formato com brackets. |
| **Correção proposta** | Remover brackets de `cotarco-git-workflow.md`; alinhar com Conventional Commits. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-013

| Field | Value |
|-------|-------|
| **ID** | REM-013 |
| **Problema** | `cotarco-git-workflow.md` inclui `git push` no fluxo automático (`git add . → commit → push`) sem gate de aprovação humana |
| **Fonte** | Rules Auditor (FIND-008, FIND-009) |
| **Impacto** | Viola `workspace.md §5` (confirmação humana obrigatória) e `context.md §5 Rule 7` (sem operações críticas sem aprovação). Agentes podem fazer push directo para branches activas. |
| **Correção proposta** | Remover `git push` do fluxo automático em `cotarco-git-workflow.md`. Adicionar gate explícito: "aguardar confirmação humana antes de push". |
| **Risco** | ALTO — push não autorizado pode quebrar branches partilhadas |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-014

| Field | Value |
|-------|-------|
| **ID** | REM-014 |
| **Problema** | `agents.md §0` lista apenas 3 de 10 documentos obrigatórios. Contradiz `README.md` que lista todos os 10. |
| **Fonte** | Documentation Auditor (B-01) + Rules Auditor (FIND-017) |
| **Impacto** | Agentes iniciam implementação sem ler `data-architecture.md`, `application-flows.md`, `routes-api.md`, `ui-wireframes-and-design-system.md`. Alta probabilidade de implementação inconsistente. |
| **Correção proposta** | Actualizar `agents.md §0` para incluir toda a sequência de leitura de 10 documentos em conformidade com `README.md`. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-015

| Field | Value |
|-------|-------|
| **ID** | REM-015 |
| **Problema** | Dual source-of-truth para outputs: tabela `output_files` E `job_files.kind = OUTPUT` — deixado como "MVP decision" sem resolução |
| **Fonte** | Documentation Auditor (A-05) |
| **Impacto** | Agente de DB criará schema inconsistente; agente de API não saberá qual tabela consultar para outputs |
| **Correção proposta** | Criar ADR-0004 para decidir: consolidar em `job_files` (unificado) ou separar `output_files` para geração/export. |
| **Risco** | ALTO — decisão de schema; difícil de alterar após migrations |
| **Categoria** | ARCHITECTURE/BUSINESS DECISION |
| **Agente responsável** | Tech Lead |
| **Necessita aprovação humana?** | Sim — obrigatório |

---

### REM-016

| Field | Value |
|-------|-------|
| **ID** | REM-016 |
| **Problema** | `processing_jobs` sem campo `description` no schema — presente no contrato de API e no wireframe mas ausente do DB schema |
| **Fonte** | Documentation Auditor (C-02) |
| **Impacto** | Migration inicial estará incompleta; API retorna campo que não existe no DB |
| **Correção proposta** | Adicionar `description TEXT` ao schema de `processing_jobs` em `data-architecture.md`. |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-017

| Field | Value |
|-------|-------|
| **ID** | REM-017 |
| **Problema** | Formato de handoff definido 3 vezes com campos diferentes (5, 6 e 9 campos) em documentos diferentes |
| **Fonte** | Documentation Auditor (D-03) |
| **Impacto** | Agentes entregam handoffs incompatíveis entre si; orquestração quebra se algum campo esperado estiver ausente |
| **Correção proposta** | Canonizar formato de 9 campos em `agents.md §7`; remover definições alternativas dos outros documentos |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-018

| Field | Value |
|-------|-------|
| **ID** | REM-018 |
| **Problema** | Endpoint `POST /jobs/{id}/reopen` existe em `routes-api.md` sem flow correspondente, sem transição de estado, sem conceito de domínio |
| **Fonte** | Documentation Auditor (E-02) |
| **Impacto** | Endpoint "fantasma" — agente de API irá implementá-lo mas o comportamento será indefinido |
| **Correção proposta** | Ou documentar o conceito "reopen" com flow e transição de estado, ou remover o endpoint de `routes-api.md` até à decisão |
| **Risco** | MÉDIO |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Product Owner |
| **Necessita aprovação humana?** | Sim |

---

## 🟡 P2 — MEDIUM (Resolver antes das fases de UI)

---

### REM-019

| Field | Value |
|-------|-------|
| **ID** | REM-019 |
| **Problema** | `git add .` como instrução padrão em `cotarco-git-workflow.md` viola princípio de commits atómicos |
| **Fonte** | Rules Auditor (FIND-006) |
| **Impacto** | Commits misturarão mudanças não relacionadas; rastreabilidade comprometida; rollbacks mais difíceis |
| **Correção proposta** | Substituir por `git add <ficheiros-específicos>` com instrução explícita de staging cirúrgico |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-020

| Field | Value |
|-------|-------|
| **ID** | REM-020 |
| **Problema** | `codeNavi.md` fase Execute não tem "await human confirmation" explícito antes de alterações destrutivas |
| **Fonte** | Rules Auditor (FIND-010) |
| **Impacto** | Inconsistência com `workspace.md §5`; agentes podem executar sem gate de confirmação |
| **Correção proposta** | Adicionar passo explícito "Apresentar plano → Aguardar confirmação humana → Executar" na fase Execute de `codeNavi.md` |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-021

| Field | Value |
|-------|-------|
| **ID** | REM-021 |
| **Problema** | Redux Toolkit e Zustand recomendados em `frontend.md` — não estão na stack aprovada em `context.md §7` |
| **Fonte** | Rules Auditor (FIND-011) |
| **Impacto** | Agente de frontend pode instalar dependências não aprovadas |
| **Correção proposta** | Remover Redux Toolkit e Zustand de `frontend.md`; ou adicionar ao stack aprovado em `context.md` com justificação |
| **Risco** | MÉDIO |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Tech Lead |
| **Necessita aprovação humana?** | Sim |

---

### REM-022

| Field | Value |
|-------|-------|
| **ID** | REM-022 |
| **Problema** | `frontend.md` diz "usar const arrow functions"; `frontend-architecture.md` diz "usar function keyword" — contradição directa para definição de componentes |
| **Fonte** | Rules Auditor (FIND-014) |
| **Impacto** | Codebase terá dois estilos misturados; difícil de manter coerência |
| **Correção proposta** | Escolher um padrão. Recomendado: `function` keyword para componentes de página (melhor stack traces), arrow functions para utilitários/callbacks |
| **Risco** | BAIXO |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Tech Lead |
| **Necessita aprovação humana?** | Sim |

---

### REM-023

| Field | Value |
|-------|-------|
| **ID** | REM-023 |
| **Problema** | `context-guard.md` lista apenas 2 dos 6 documentos de leitura obrigatória de `agents.md §0` |
| **Fonte** | Rules Auditor (FIND-017) |
| **Impacto** | Agentes que só seguem o context-guard iniciam sem contexto suficiente |
| **Correção proposta** | Sincronizar `context-guard.md` com a lista completa de `agents.md §0` |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-024

| Field | Value |
|-------|-------|
| **ID** | REM-024 |
| **Problema** | `graphify-out/wiki/index.md` referenciado em `.agents/rules/graphify.md` linha 12 mas não existe |
| **Fonte** | Rules Auditor (FIND-018) + Graphify Auditor (convergência) |
| **Impacto** | Rule invocável mas com condicional que nunca se activa; documentação enganosa |
| **Correção proposta** | Opção A: Gerar wiki com `graphify wiki .` e commitá-la. Opção B: Remover referência da rule até wiki ser gerada. |
| **Risco** | BAIXO |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Agente de Graphify Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-025

| Field | Value |
|-------|-------|
| **ID** | REM-025 |
| **Problema** | Merge driver do Graphify (`graph.json merge=graphify`) documentado apenas em `.git/config` local — colaboradores não recebem instrução para instalá-lo |
| **Fonte** | Graphify Auditor |
| **Impacto** | Em repositório multi-developer, merge conflicts em `graph.json` não serão resolvidos automaticamente para outros colaboradores |
| **Correção proposta** | Adicionar secção de setup ao `README.md` ou criar `scripts/setup-dev.sh` com `graphify antigravity install` |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-026

| Field | Value |
|-------|-------|
| **ID** | REM-026 |
| **Problema** | Git hooks do Graphify (`post-commit`, `post-checkout`) são locais (`.git/hooks/`) e não estão documentados para onboarding |
| **Fonte** | Graphify Auditor |
| **Impacto** | Novo developer ou novo ambiente não terá os hooks; graph ficará desactualizado sem aviso |
| **Correção proposta** | Documentar hooks em setup guide; considerar `husky` ou script de setup para instalação automática |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-027

| Field | Value |
|-------|-------|
| **ID** | REM-027 |
| **Problema** | `.agents/workflows/graphify.md` é um stub vazio (11 linhas de boilerplate) |
| **Fonte** | Graphify Auditor |
| **Impacto** | Agentes que tentam seguir o workflow não têm passos concretos |
| **Correção proposta** | Escrever workflow concreto: quando fazer `graphify update`, `graphify query`, como interpretar resultados, quando actualizar após refactor |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-028

| Field | Value |
|-------|-------|
| **ID** | REM-028 |
| **Problema** | `.gitattributes` tem apenas 1 linha — sem `text=auto eol=lf`, sem declarações de binários; causando warning LF→CRLF |
| **Fonte** | Git & Artifacts Auditor |
| **Impacto** | Ficheiros com CRLF em Windows causam diffs ruidosos; risco de corrupção em scripts shell |
| **Correção proposta** | Expandir `.gitattributes` com: `* text=auto eol=lf`, declarações binárias para imagens/Excel, e LFS config para ficheiros grandes |
| **Risco** | BAIXO |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Manutenção Git |
| **Necessita aprovação humana?** | Não |

---

### REM-029

| Field | Value |
|-------|-------|
| **ID** | REM-029 |
| **Problema** | Estratégia de sync entre `users.id` e Supabase `auth.users` marcada como "alinhado quando possível" — sem definição concreta |
| **Fonte** | Documentation Auditor (C-03) |
| **Impacto** | Agente de autenticação não saberá como sincronizar tabelas; implementação inconsistente ou incoerente |
| **Correção proposta** | Criar ADR-0006: definir trigger de DB automático vs. sync via Edge Function vs. referência directa a `auth.users` |
| **Risco** | MÉDIO — decisão de arquitectura de auth |
| **Categoria** | ARCHITECTURE/BUSINESS DECISION |
| **Agente responsável** | Tech Lead |
| **Necessita aprovação humana?** | Sim |

---

## 🟢 P3 — LOW (Housekeeping — antes do MVP Demo)

---

### REM-030

| Field | Value |
|-------|-------|
| **ID** | REM-030 |
| **Problema** | Framer Motion recomendado em `frontend.md` — não está na stack aprovada; contradiz "sem excesso de animações" |
| **Fonte** | Rules Auditor (FIND-015) |
| **Correção proposta** | Remover. Usar CSS transitions nativas (já definidas no design system). |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-031

| Field | Value |
|-------|-------|
| **ID** | REM-031 |
| **Problema** | "Don't use semicolons" em `frontend.md` — deve ser delegado ao Prettier config, não a uma rule de agente |
| **Fonte** | Rules Auditor (FIND-016) |
| **Correção proposta** | Remover a rule; garantir que `.prettierrc` define `"semi": false` |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Rules Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-032

| Field | Value |
|-------|-------|
| **ID** | REM-032 |
| **Problema** | `.notebook/graphify-setup.md` referencia "58 nodes, 60 edges" — graph actual tem 414 nodes, 388 edges |
| **Fonte** | Graphify Auditor |
| **Correção proposta** | Actualizar contagens no notebook (ou remover — são efémeras por natureza) |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-033

| Field | Value |
|-------|-------|
| **ID** | REM-033 |
| **Problema** | `agents.md` não menciona Graphify MCP — descobrível apenas via rule `always_on` |
| **Fonte** | Graphify Auditor |
| **Correção proposta** | Adicionar parágrafo em `agents.md` sobre Graphify MCP: quando usar, como fazer query, quando actualizar |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-034

| Field | Value |
|-------|-------|
| **ID** | REM-034 |
| **Problema** | Re-upload: "nova versão no mesmo job OU novo job" — decisão por resolver (RF-010) |
| **Fonte** | Documentation Auditor (E-01) |
| **Correção proposta** | Criar ADR-0005: definir comportamento de re-upload explicitamente |
| **Categoria** | ARCHITECTURE/BUSINESS DECISION |
| **Agente responsável** | Product Owner |
| **Necessita aprovação humana?** | Sim |

---

### REM-035

| Field | Value |
|-------|-------|
| **ID** | REM-035 |
| **Problema** | Workflow de Stitch duplicado em 6 documentos; guardrails de Gemini duplicados em 5 documentos |
| **Fonte** | Documentation Auditor (D-01, D-02) |
| **Correção proposta** | Centralizar em `agents.md §5` e `agents.md §X`; outros documentos referenciam em vez de duplicar |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-036

| Field | Value |
|-------|-------|
| **ID** | REM-036 |
| **Problema** | Números de quota do Supabase (free tier) definidos em 2 documentos — risco de drift quando quotas mudarem |
| **Fonte** | Documentation Auditor (F-02) |
| **Correção proposta** | Manter em apenas 1 documento (`stack-and-guardrails.md`); o outro referencia |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-037

| Field | Value |
|-------|-------|
| **ID** | REM-037 |
| **Problema** | `00-bootstrap-audit.md` instrui agente a "criar docs/" — directoria já existe |
| **Fonte** | Documentation Auditor (B-03) |
| **Correção proposta** | Actualizar prompt para validar existência antes de criar; ou remover instrução obsoleta |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-038

| Field | Value |
|-------|-------|
| **ID** | REM-038 |
| **Problema** | `Admin` vs `ADMIN` — capitalização inconsistente em `routes-api.md` |
| **Fonte** | Documentation Auditor (A-03) |
| **Correção proposta** | Normalizar para `ADMIN` (uppercase) — padrão já usado na maioria dos documentos |
| **Categoria** | SAFE TO FIX |
| **Agente responsável** | Agente de Documentation Maintenance |
| **Necessita aprovação humana?** | Não |

---

### REM-039

| Field | Value |
|-------|-------|
| **ID** | REM-039 |
| **Problema** | Não existe hierarquia formal de precedência documental — 3 documentos definem listas de leitura parciais e inconsistentes |
| **Fonte** | Documentation Auditor (F-01) |
| **Correção proposta** | Definir em `agents.md §0` a hierarquia: `agents.md > context.md > docs/ > adr/ > prompts/` com nota "em caso de conflito, o documento de maior precedência governa" |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Tech Lead |
| **Necessita aprovação humana?** | Sim |

---

### REM-040

| Field | Value |
|-------|-------|
| **ID** | REM-040 |
| **Problema** | `artifacts/` directory não está no `.gitignore` — aparece como noise em cada `git status` |
| **Fonte** | Git & Artifacts Auditor |
| **Correção proposta** | Decidir: adicionar `artifacts/` ao `.gitignore` (relatórios efémeros) OU commitar como documentação permanente |
| **Categoria** | NEEDS REVIEW |
| **Agente responsável** | Tech Lead |
| **Necessita aprovação humana?** | Sim |

---

## 4 ADRs em Falta (Bloqueantes de Implementação)

| ADR | Decisão Necessária | Finding |
|-----|---------------------|---------|
| **ADR-0003** | `REJECTED` em aprovação → qual `job_status`? | REM-008 |
| **ADR-0004** | `output_files` vs `job_files.kind=OUTPUT` — qual é a fonte de verdade? | REM-015 |
| **ADR-0005** | Re-upload: nova versão no mesmo job vs. novo job | REM-034 |
| **ADR-0006** | Sync strategy: `users` ↔ `auth.users` (trigger, Edge Function, ou referência directa) | REM-029 |

---

## Resumo por Categoria

| Categoria | Count | IDs |
|-----------|-------|-----|
| **SAFE TO FIX** | 24 | REM-001,002,003,004,006,007,009,010,011,012,013,014,016,017,019,020,023,025,026,027,028,030,031,032,033,036,037,038 |
| **NEEDS REVIEW** | 8 | REM-005,018,021,022,024,035,039,040 |
| **ARCHITECTURE/BUSINESS DECISION** | 4+4 ADRs | REM-008,015,029,034 |

---

## Sugestão de Sequência de Remediação

```
FASE 1 — Git Hygiene (sem dependências, sem risco)
  REM-001, REM-002, REM-003, REM-004, REM-028

FASE 2 — Rules Fixes (seguros, sem aprovação)
  REM-006, REM-007, REM-011, REM-012, REM-013, REM-019, REM-020, REM-023

FASE 3 — Documentation Fixes (seguros, sem aprovação)
  REM-009, REM-010, REM-014, REM-016, REM-017, REM-025, REM-026, REM-027

FASE 4 — Decisões Humanas (bloqueantes)
  ADR-0003 → ADR-0004 → ADR-0005 → ADR-0006
  + REM-018, REM-021, REM-022, REM-039, REM-040

FASE 5 — Housekeeping (após fases anteriores)
  REM-024, REM-030, REM-031, REM-032, REM-033, REM-035, REM-036, REM-037, REM-038
```

---

*Este plano é AUDIT-ONLY. Nenhum ficheiro foi modificado durante esta fase.*  
*Para executar remediação, criar tarefa explícita para cada REM-ID aprovado.*
