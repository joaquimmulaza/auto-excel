# Agent Prompt A10-A16 — Domain Engine TDD First

## Gate obrigatório (antes de implementar)

1. Ler `context.md`, `agents.md`, `docs/data-architecture.md`, `docs/testing-tdd.md` e `docs/requirements.md` (sob `cotarco-commercial-manager/`).
2. Graphify MCP recon em `joaquimmulaza/auto-excel`: localizar motor/regras (`query_graph`, `graphify_find`); mapear callers/tests com `graphify_callers` / `graphify_tests_for`.
3. Skills só da matriz §11: `coding-guidelines`, `best-practices`.
4. TDD first — nenhum domínio novo sem teste a falhar primeiro.
5. Entregar handoff de 9 campos (`agents.md` §7).

## Missão

Extrair o motor de processamento do script `auto-excel` para uma camada de domínio/serviços testável e reutilizável.

## Regra

TDD first. Nenhuma função nova de domínio pode ser criada sem teste primeiro.

## Ordem

1. referências;
2. preços;
3. stock;
4. price guard;
5. decisões por item;
6. processamento completo;
7. adapters/profile config;
8. testes de paridade com fixtures.

## Contrato alvo

```python
result = process_price_table(
    source_table,
    comparison_table,
    profile_config,
)
```

O resultado deve ser estruturado e conter:

- summary;
- item decisions;
- validation issues;
- history records;
- output instructions.

## Regras

- não depender de terminal;
- não imprimir como mecanismo de retorno;
- não escrever ficheiros dentro do domínio;
- não conhecer FastAPI;
- não conhecer React;
- não chamar Gemini.

## Compatibilidade

Preservar a lógica válida atual do Samsung→Mano através de fixtures reais anonimizadas/sintéticas.

## Definition of Done

- testes unitários verdes;
- casos de regressão cobertos;
- domínio importável sem web;
- código antigo pode ser adaptado para chamar engine.

## Entrega

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: A10-A16
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
```
