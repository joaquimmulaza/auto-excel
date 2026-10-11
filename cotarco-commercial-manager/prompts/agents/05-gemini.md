# Agent Prompt A60-A63 — Gemini Assist

## Gate obrigatório (antes de implementar)

1. Ler `context.md`, `agents.md`, `docs/stack-and-guardrails.md` e `docs/routes-api.md` (sob `cotarco-commercial-manager/`).
2. Graphify MCP recon em `joaquimmulaza/auto-excel` para serviços/API existentes (`query_graph`, `graphify_impact`).
3. Skills só da matriz §11: `technical-design-doc-creator`, `security-best-practices`.
4. TDD nos contratos Pydantic e fallbacks sem IA.
5. Entregar handoff de 9 campos (`agents.md` §7).

## Missão

Adicionar uma camada de assistência Gemini no backend.

## Funcionalidades MVP

1. explicar issue;
2. resumir job;
3. analisar anomalias;
4. sugerir mapeamento de coluna.

## Guardrails

- nunca expor API key ao browser;
- nunca permitir que a resposta altere diretamente o domínio;
- JSON estruturado com schema;
- timeout;
- retry limitado;
- rate limit;
- logs sem conteúdo sensível desnecessário;
- resposta claramente rotulada como IA.

## Contrato

Criar modelos Pydantic para saída. Validar sempre a resposta antes de apresentar.

## Fallback

Quando Gemini estiver indisponível, o sistema continua operacional sem IA.

## Entrega

```text
STATUS: DONE | BLOCKED | NEEDS_REVIEW
TASK: A60-A63
SUMMARY: <resumo>
FILES: <lista>
TESTS: <comandos + resultado>
QA: <resultado>
RISKS: <lista>
DOCS_UPDATED: <lista>
NEXT: <próxima tarefa recomendada>
```
