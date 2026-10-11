# Prompt Orchestration

## Como usar no Cursor Cloud Agent

1. As regras na raiz (`AGENTS.md`, `.cursor/rules/cotarco-workflow.mdc`) já obrigam docs → Graphify → skills → TDD → handoff.
2. Colar **`MASTER_ORCHESTRATOR.md`** para o agente escolher a próxima fase do backlog, **ou** colar um prompt de fase (`agents/00`–`06` / `stitch/*`) para executar essa missão à risca.
3. Paths nos prompts (`context.md`, `agents.md`, `docs/...`) resolvem sob `cotarco-commercial-manager/`.

## Ordem das fases

```text
00-bootstrap-audit
       ↓
01-domain-tdd
       ↓
02-database
       ↓
03-api
       ↓
Stitch 00 → 01 → 02 → 03
       ↓
04-frontend
       ↓
05-gemini
       ↓
06-integrations-and-demo
```

O agente nunca deve saltar uma etapa crítica por conta própria.

## Gate comum (todos os prompts de fase)

Antes de implementar:

1. Ler os docs listados no prompt (+ `agents.md`).
2. Graphify MCP recon em `joaquimmulaza/auto-excel`.
3. Carregar só as skills da matriz (`agents.md` §11).
4. TDD loop.
5. Entregar handoff de 9 campos (`agents.md` §7).

## Stitch loop

Para cada prompt Stitch:

```text
PROMPT
  ↓
STITCH GENERATE (MCP)
  ↓
VISUAL QA
  ↓
aprovado? → IMPLEMENT
não → FEEDBACK → STITCH (máx. 3 ciclos)
```

## Orquestrador principal

Usar `MASTER_ORCHESTRATOR.md` quando o pedido for livre. Selecionar a próxima tarefa com base no estado do repositório e no handoff da fase anterior.
