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
3. Carregar só as skills de repo da matriz (`agents.md` §11).
4. Se UI/Stitch/frontend: **UI Skills MCP** — `list_skills` → escolher 2–4 → `get_skill` → aplicar (`agents.md` §5.1).
5. TDD loop.
6. Entregar handoff canónico + `UI_SKILLS_SELECTED` quando aplicável (`agents.md` §7).

## Stitch loop (skills oficiais + baton)

```text
PROMPT / .stitch/next-prompt.md
  ↓
UI Skills MCP → .stitch/DESIGN.md → enhance-prompt
  ↓
STITCH GENERATE (stitch-design MCP)
  ↓
stage .stitch/designs/ → update SITE.md → stitch-loop baton
  ↓
VISUAL QA
  ↓
aprovado? → IMPLEMENT frontend (04)
não → FEEDBACK → STITCH (máx. 3 ciclos/tela)
```

Skills: `taste-design` | `design-md`, `enhance-prompt`, `stitch-design`, `stitch-loop` (ver `agents.md` §5.2).

## Orquestrador principal

Usar `MASTER_ORCHESTRATOR.md` quando o pedido for livre. Selecionar a próxima tarefa com base no estado do repositório e no handoff da fase anterior.
