# Agent Prompt A00 — Bootstrap + Audit

Leia obrigatoriamente `context.md`, `agents.md`, `docs/requirements.md`, `docs/stack-and-guardrails.md` e `docs/testing-tdd.md`.

## Missão

Auditar o repositório atual e preparar a fundação do novo projeto sem destruir o motor existente.

## Contexto

O repositório contém o primeiro motor de automação de Excel. Precisamos transformá-lo gradualmente numa plataforma web interna de gestão de tabelas comerciais para múltiplos perfis/destinos.

## Tarefas

1. Mapear ficheiros, dependências e comportamento atual.
2. Identificar regras do `auto-excel` que precisam de preservação.
3. Criar a estrutura inicial proposta em `docs/`.
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

Responder com:

`DONE / TESTS / FILES / RISKS / NEXT`
