# AGENTS.md — Operating Rules for AI Coding Agents

## 0. Ordem obrigatória de leitura

Antes de qualquer alteração, ler:

1. `context.md`
2. `agents.md`
3. `docs/requirements.md`
4. `docs/stack-and-guardrails.md`
5. `docs/testing-tdd.md`
6. o documento específico da tarefa

Não iniciar implementação sem compreender o estado atual do repositório.

## 1. Princípio central

**TDD first, code second.**

Para cada tarefa:

`entender → definir critério → escrever/ajustar teste → executar teste falhando → implementar mínimo → executar testes → refatorar → QA → documentar`.

## 2. Não fazer

- Não reescrever o projeto inteiro sem uma tarefa explícita.
- Não apagar lógica funcional do `auto-excel` por conveniência.
- Não colocar regras de negócio no frontend.
- Não chamar Gemini diretamente do browser.
- Não colocar secrets em código ou `.env` versionado.
- Não criar `if partner == ...` espalhados pelo sistema.
- Não publicar em serviços externos durante testes sem mock/fixture explícita.
- Não fazer alterações destrutivas em ficheiros de entrada.
- Não usar IA para substituir validações determinísticas.
- Não marcar tarefa como concluída sem testes e evidência de QA.

## 3. Regras de arquitetura

- Domínio independente de FastAPI/Next.js.
- Integrações atrás de adapters.
- Processamento Excel atrás de services/ports.
- API apenas orquestra casos de uso.
- UI consome API; não duplica regras.
- Banco é fonte de verdade para estado dos jobs, não o filesystem local.
- Storage guarda ficheiros; DB guarda metadados.

## 4. Regra de alterações

Antes de alterar schema, API, domínio ou UI global:

1. localizar todos os consumidores;
2. confirmar impacto;
3. escrever teste/regressão;
4. atualizar documentação correspondente;
5. implementar;
6. testar.

## 5. Stitch MCP — protocolo obrigatório para UI

Quando a tarefa envolve uma nova tela ou alteração estrutural de UI:

1. Ler `docs/ui-wireframes-and-design-system.md`.
2. Criar prompt específico para Stitch em `prompts/stitch/` ou usar o prompt fornecido pela tarefa.
3. Chamar Stitch através do MCP disponível no ambiente do agente.
4. Gerar a tela.
5. Fazer QA visual contra os critérios de aceitação.
6. Se aprovado: usar a proposta como referência para codificação.
7. Se reprovado: enviar feedback objetivo para Stitch e pedir nova iteração.
8. Repetir até aprovação ou atingir 3 ciclos; depois parar e pedir revisão humana.

**Nunca considerar o código exportado por Stitch como implementação final automaticamente.** Deve ser adaptado à arquitetura, acessibilidade e componentes do projeto.

## 6. QA de Stitch

Critérios mínimos:

- usa a paleta de produto;
- tipografia e espaçamento consistentes;
- hierarquia clara;
- estados loading/empty/error contemplados;
- tabelas legíveis;
- ações críticas visualmente distintas;
- navegação coerente;
- sem informação inventada;
- sem mock de funcionalidades que não existem sem marcar como protótipo;
- desktop 1440px aceitável;
- mobile 390px sem quebra funcional nas telas prioritárias.

## 7. Evidência obrigatória

Todo agente deve terminar uma tarefa fornecendo:

- resumo do que mudou;
- testes executados;
- resultado dos testes;
- riscos/limitações;
- ficheiros alterados;
- decisão que ficou pendente, se houver.

## 8. Handoffs

Nunca depender de memória de conversa. Toda informação necessária deve estar:

- no código;
- em `context.md`;
- em documentação;
- em ADR;
- ou no comentário do PR/commit.

## 9. Convencional de commits

Usar Conventional Commits:

- `feat:`
- `fix:`
- `refactor:`
- `test:`
- `docs:`
- `chore:`
- `security:`

Evitar commits gigantes.
