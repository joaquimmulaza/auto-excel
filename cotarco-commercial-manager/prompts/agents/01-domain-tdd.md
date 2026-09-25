# Agent Prompt A10-A16 — Domain Engine TDD First

Leia `context.md`, `agents.md`, `docs/data-architecture.md`, `docs/testing-tdd.md` e `docs/requirements.md`.

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
