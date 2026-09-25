# Prompt Orchestration

## Como usar

Executar os prompts em ordem, respeitando dependências.

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

## Stitch loop

Para cada prompt Stitch:

```text
PROMPT
  ↓
STITCH GENERATE
  ↓
VISUAL QA
  ↓
┌───────────────┐
│ aprovado?     │
└──────┬────────┘
       │
   sim ↓      não → FEEDBACK → STITCH
       ↓
IMPLEMENT
```

Máximo recomendado de 3 iterações automáticas por tela antes de pedir revisão humana.

## Orquestrador principal

O operador humano/ChatGPT pode selecionar o próximo prompt com base no estado atual do repositório e nos resultados do agente anterior. O agente nunca deve decidir sozinho que pode saltar uma etapa crítica.
