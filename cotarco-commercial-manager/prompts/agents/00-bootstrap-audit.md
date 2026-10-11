# Agent Prompt A00 — Bootstrap + Audit

## Gate obrigatório (antes de implementar)

1. Ler `context.md`, `agents.md`, `docs/requirements.md`, `docs/stack-and-guardrails.md` e `docs/testing-tdd.md` (sob `cotarco-commercial-manager/`).
2. Graphify MCP recon em `joaquimmulaza/auto-excel`: `query_graph` / `graphify_find` sobre estrutura e motor `auto-excel`; `graphify_file_neighbors` nos hubs.
3. Skills só da matriz §11: `tlc-spec-driven`, `web-quality-audit`.
4. TDD / caracterização conforme secção TDD.
5. Entregar handoff de 9 campos (`agents.md` §7).

## Missão

Auditar o repositório atual e preparar a fundação do novo projeto sem destruir o motor existente.

## Contexto

O repositório contém o primeiro motor de automação de Excel. Precisamos transformá-lo gradualmente numa plataforma web interna de gestão de tabelas comerciais para múltiplos perfis/destinos.

## Tarefas

1. Mapear ficheiros, dependências e comportamento atual.
2. Identificar regras do `auto-excel` que precisam de preservação.
3. Validar e organizar a estrutura existente em `docs/`.
4. Configurar lint/typecheck/test runners sem introduzir features.
5. Criar um baseline test que prove que o código antigo ainda executa ou documentar por que não.
6. Criar/ajustar `.gitignore`, `.env.example` e documentação de setup.

## TDD

Escrever pelo menos testes de caracterização para as principais funções existentes antes de refatorar.

## Não fazer

Não criar UI ainda. Não remover o `main.py` ainda. Não alterar regras de negócio sem teste.

## Definition of Done

- build/lint/test comandos documentados;
- baseline verde;
- relatório de dependências e riscos;
- estrutura preparada;
- nenhum secret.

## Entrega

Handoff canónico:

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: A00
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
```
