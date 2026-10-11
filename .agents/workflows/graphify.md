---
name: graphify
description: Workflow operacional Graphify — MCP Cloud preferido, CLI local como fallback
---

# Workflow: Grafo de Conhecimento (Graphify)

Fluxo para navegar arquitetura, dependências e regras de negócio com precisão e baixo consumo de contexto.

**Repo canónico (MCP):** `joaquimmulaza/auto-excel` (`155ea5ab-4976-4975-83e1-efcba12a3061`).

---

## 1. Princípios

1. **Contexto cirúrgico** — consultar o grafo antes de abrir muitos ficheiros.
2. **MCP primeiro no Cloud Agent** — tools Graphify MCP; CLI quando o MCP não estiver disponível.
3. **Atualização AST-only** — `graphify update .` após mudanças de código (sem custo LLM).
4. **Integridade** — não editar `graphify-out/graph.json` à mão; usar merge driver/hooks.

---

## 2. Recon obrigatório (antes de implementar)

```text
list_repositories (se preciso)
  → query_graph / graphify_find
  → graphify_impact / graphify_callers / graphify_tests_for
  → Read pontual dos ficheiros retornados
```

### MCP (preferido)

| Tool | Quando |
|---|---|
| `list_repositories` | Confirmar repos e `queryable` |
| `query_graph` | "Onde/como funciona X?" |
| `graphify_find` | Localizar símbolo por fragmento de nome |
| `graphify_node` | Corpo + vizinhos |
| `graphify_callers` / `graphify_callees` | Cadeia de chamadas |
| `graphify_impact` | Blast radius da mudança |
| `graphify_tests_for` | Testes ligados |
| `graphify_file_neighbors` | Imports/dependentes de um ficheiro |
| `shortest_path` / `graphify_trace` | Caminho entre dois nós |

Passar `repository_id` como UUID ou `joaquimmulaza/auto-excel`.

### CLI (fallback)

```bash
graphify query "<pergunta ou termo>"
graphify path "<origem>" "<destino>"
graphify explain "<componente>"
```

---

## 3. Atualizar o grafo

Após criar/renomear/alterar código (`.py`, `.ts`, `.tsx`, `.js`, …):

```bash
graphify update .
# se removeu nós/ficheiros:
graphify update . --force
```

---

## 4. Artefactos locais

| Artefacto | Uso |
|---|---|
| Subgrafo MCP/CLI | Primeira opção no dia a dia |
| `graphify-out/GRAPH_REPORT.md` | Revisão ampla |
| `graphify-out/graph.html` | Inspeção visual humana |
| `graphify-out/graph.json` | Fonte de verdade versionada |

---

## 5. Guardrails

- `graphify hook status` para hooks locais.
- Conflitos em `graph.json`: merge driver (`graphify merge-driver`), nunca merge textual manual.
- Respeitar `.graphifyignore`.
