---
name: graphify
description: Workflow operacional para consulta, navegação estrutural e manutenção contínua do Grafo de Conhecimento (Graphify)
---

# Workflow: Grafo de Conhecimento (Graphify)

Este documento define o fluxo operacional e as diretrizes de uso do Grafo de Conhecimento do projeto (`graphify-out/graph.json`), utilizado por agentes de IA e desenvolvedores para navegar pela arquitetura, dependências e regras de negócio com alta precisão e economia de contexto.

---

## 1. Princípios Operacionais

1. **Contexto Cirúrgico**: Consultar o grafo antes de inspecionar múltiplos arquivos desnecessários. Uma consulta ao grafo devolve o subgrafo exato de nós e arestas relevantes, reduzindo o consumo de tokens e prevenindo alucinações.
2. **Atualização Incremental sem Custo**: Alterações em arquivos de código devem ser refletidas no grafo usando comandos AST-only, que não consomem cota de LLM nem geram custo de API.
3. **Preservação de Integridade**: O arquivo `graphify-out/graph.json` é a fonte de verdade estrutural do grafo; use as ferramentas oficiais de atualização e merge driver para mantê-lo íntegro.

---

## 2. Quando e Como Consultar o Grafo

### Casos de Uso
- Dúvidas sobre a arquitetura do sistema e organização de módulos.
- Identificação de funções, classes, regras de negócio ou contratos afetados por uma mudança.
- Descoberta de fluxos de importação e chamadas existentes.

### Comandos de Consulta
- **CLI Principal:**
  ```bash
  graphify query "<pergunta ou termo de pesquisa>"
  ```
  *Exemplos:*
  ```bash
  graphify query "validação de preços"
  graphify query "regras samsung"
  graphify query "auto-excel"
  ```

- **Via MCP (se disponível no ambiente do agente):**
  Utilize a tool `query_graph` passando a pergunta ou conceito desejado.

### Interpretação da Saída
- O comando executa uma busca semântica/léxica nos nós do grafo e uma travessia BFS (Breadth-First Search) a partir dos nós correspondentes.
- Retorna uma lista de **nós relevantes** (`NODE <nome> [src=<arquivo> loc=L<linha> community=<comunidade>]`) e **arestas de conexão** (`EDGE <origem> --<tipo> [EXTRACTED]--> <destino>`).
- Utilize as referências de arquivo e linha retornadas para inspecionar cirurgicamente apenas os pontos exatos no código.

---

## 3. Análise de Relações e Nós Focados

Quando uma pergunta ampla apontar nós que precisam de investigação detalhada, utilize as ferramentas de inspeção pontual:

### A. Caminho Mais Curto entre Dois Conceitos (`graphify path`)
Permite identificar como dois nós (módulos, classes, funções, requisitos) se relacionam direta ou indiretamente na arquitetura.

- **Comando:**
  ```bash
  graphify path "<Nó Origem>" "<Nó Destino>"
  ```
  *Exemplo:*
  ```bash
  graphify path "find_column()" "avaliar_price_guard()"
  ```
- **Utilidade:** Diagnosticar acoplamento, rastrear cadeias de chamadas ou validar o impacto transversal de uma alteração arquitetural.

### B. Explicação Focada de um Nó e seus Vizinhos (`graphify explain`)
Fornece um resumo estruturado de um nó específico, sua comunidade, seu grau de conectividade e todas as suas arestas de entrada e saída.

- **Comando:**
  ```bash
  graphify explain "<Nome do Nó>"
  ```
  *Exemplo:*
  ```bash
  graphify explain "find_column()"
  ```
- **Utilidade:** Analisar quem consome uma função (`<-- chamador [calls]`) e quais dependências ela invoca (`--> dependência [calls]`), sem precisar ler manualmente todo o código-fonte.

---

## 4. Quando e Como Atualizar o Grafo

### Quando Executar
- **Sempre após modificar, criar ou renomear arquivos de código** (`.py`, `.ts`, `.js`, etc.) durante a sessão de desenvolvimento.
- **Após implementar novos módulos, testes de domínio ou refatorações de código.**

### Como Executar
Execute a atualização incremental a partir da raiz do repositório:

```bash
graphify update .
```

### Características da Atualização
- **Operação AST-Only:** Analisa unicamente as árvores de sintaxe abstrata dos arquivos de código modificados.
- **Custo Zero:** Não realiza chamadas a provedores de LLM externos (0 tokens consumidos).
- **Preservação Semântica:** Mantém as comunidades e anotações semânticas pré-existentes, atualizando apenas os nós e arestas do código modificado.
- **Refatorações com Exclusão de Código:** Caso uma refatoração tenha removido arquivos ou reduzido nós existentes, adicione a flag `--force`:
  ```bash
  graphify update . --force
  ```

---

## 5. Interpretação de Saídas e Relatórios

O Graphify gera diferentes artefatos com propósitos complementares:

| Artefato | Propósito | Quando Utilizar |
| :--- | :--- | :--- |
| **Subgrafos de Consulta** (`query`, `path`, `explain`) | Subconjunto focado de nós e arestas relevantes para uma tarefa específica. | **Primeira opção:** consumo rápido de contexto pelo agente durante a execução de tarefas diárias. |
| `graphify-out/GRAPH_REPORT.md` | Relatório global com métricas de volume, frescura de commit e lista de hubs arquiteturais/comunidades. | Planejamento arquitetural, revisão abrangente de integridade do grafo ou quando queries pontuais forem insuficientes. |
| `graphify-out/graph.html` | Visualização visual e interativa no navegador. | Inspeção visual humana para análise topológica e exploração de clusters. |
| `graphify-out/graph.json` | Estrutura de dados serializada do grafo de conhecimento. | Fonte de verdade estrutural versionada no Git e protegida pelo merge driver. |

---

## 6. Guardrails de Manutenção

- **Automação via Hooks:** Garanta que os hooks locais estão ativos executando `graphify hook status`.
- **Merge Driver:** Nunca force merge manual ou resolva conflitos de `graphify-out/graph.json` com editores de texto convencionais; utilize o driver registrado (`graphify merge-driver`).
- **Escopo do Grafo:** Respeite as diretrizes de exclusão definidas no `.graphifyignore` para evitar que ferramentas e configurações internas contaminem o grafo de domínio.
