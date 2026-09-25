# Suite de Testes Automatizados — TDD First

## 1. Filosofia

A estratégia é **testes antes da implementação** para regras de domínio e casos de uso críticos.

Pirâmide:

```text
             E2E (poucos)
          ┌───────────────┐
          │ Playwright    │
          └───────────────┘
        Integration/API
      ┌─────────────────────┐
      │ FastAPI + DB/Test   │
      └─────────────────────┘
   Domain/Unit (muitos)
┌───────────────────────────────┐
│ rules / engine / parsers      │
└───────────────────────────────┘
```

## 2. Backend

### Ferramentas

- pytest;
- pytest-cov;
- httpx/TestClient;
- fixtures;
- test DB isolada;
- Ruff;
- mypy/pyright.

### Testes de domínio obrigatórios

#### Referências

- remove acentos;
- uppercase;
- remove caracteres não permitidos;
- mantém traço conforme regra;
- referências equivalentes fazem match;
- vazio é rejeitado.

#### Preços

- `2.614.035,09` → `2614035.09`;
- `2614035.09` permanece correto;
- moeda/símbolos são tratados;
- valores inválidos resultam em erro/zero conforme contrato, nunca em crash silencioso;
- zero segue regra de validação do profile.

#### Price Guard

- 5% → permitido;
- 29.99% → permitido;
- 30% → comportamento definido e testado pelo profile;
- >30% → blocker quando regra configurada para bloquear;
- preço anterior zero não provoca divisão por zero.

#### Stock

- inteiro válido;
- vazio inválido quando obrigatório;
- negativo rejeitado;
- stock threshold configurável.

#### Duplicados

- dois identificadores normalizados iguais → blocker;
- aliases distintos mas mesmo match → tratados conforme regra definida.

#### Produto existente

- atualiza price/stock conforme profile;
- não atualiza se blocker;
- estados active/sold_out seguem rules;
- histórico é criado.

#### Produto novo

- adicionado quando elegível;
- ignorado quando stock/preço não cumprem regra;
- não duplica produto existente.

## 3. Testes de casos de uso

### `CreateJob`

- cria job com perfil válido;
- rejeita perfil inexistente/inativo;
- cria audit log.

### `UploadFile`

- aceita `.xlsx`;
- rejeita extensão não permitida;
- rejeita ficheiro excessivo;
- guarda hash;
- cria versão.

### `ValidateJob`

- muda `UPLOADED → VALIDATING → READY_FOR_REVIEW`;
- com blocker muda para `NEEDS_CORRECTION`;
- não cria output final.

### `ApproveJob`

- Comercial recebe 403;
- Operador com job válido aprova;
- job não aprovado não pode processar.

### `ProcessJob`

- só `APPROVED` pode processar;
- é idempotente;
- gera outputs;
- grava histórico e audit;
- erro marca `FAILED`.

## 4. API tests

Testar:

- 401 sem token;
- 403 por papel;
- 404 por ID inexistente;
- 409 estado inválido;
- 422 payload inválido;
- 413 upload excessivo;
- 429 rate limit em endpoints de IA.

## 5. Frontend

### Vitest + RTL

Testar componentes críticos:

- UploadDropzone;
- ProfileSelector;
- StatusBadge;
- ValidationSummary;
- DiffTable;
- IssuePanel;
- ApprovalDialog;
- EmptyState/ErrorState.

Testar comportamento, não implementação interna.

## 6. E2E com Playwright

### Cenário E2E-01

```text
login
→ dashboard
→ novo processamento
→ selecionar perfil
→ upload fixture
→ validar
→ review
→ aprovar como Operador
→ processar
→ download output
→ histórico
```

### E2E-02

```text
login Comercial
→ upload com blocker
→ review
→ confirmar NEEDS_CORRECTION
→ reupload
→ nova validação
```

### E2E-03

```text
Comercial tenta aprovar
→ 403 / ação indisponível
```

### E2E-04

```text
Gemini explain
→ backend mockado
→ schema válido
→ UI apresenta resposta como assistiva
```

## 7. Fixtures

Criar datasets pequenos e determinísticos:

```text
fixtures/
├── valid_small.xlsx
├── duplicate_reference.xlsx
├── missing_column.xlsx
├── invalid_price.xlsx
├── zero_price.xlsx
├── price_guard_block.xlsx
├── low_stock.xlsx
├── new_products.xlsx
└── mixed_realistic.xlsx
```

Não usar dados reais de clientes/parceiros em fixtures versionadas.

## 8. Contract tests

Criar schema compartilhado ou validação cruzada entre backend e frontend para respostas-chave:

- JobSummary;
- ValidationIssue;
- JobItem;
- AIResponse.

## 9. Coverage gates

Sugestão inicial:

- domínio: ≥ 90%;
- casos de uso: ≥ 85%;
- backend total: ≥ 80%;
- frontend crítico: ≥ 70%;
- E2E: cobertura dos fluxos críticos, não percentual artificial.

Qualquer limiar deve ser ajustado por evidência, não tratado como objetivo isolado.

## 10. CI quality gates

```text
install
→ lint
→ typecheck
→ unit tests
→ integration tests
→ build frontend
→ E2E (quando pipeline permitir)
→ security checks
```

Merge é bloqueado quando falhar o quality gate definido.

## 11. TDD workflow por tarefa

```text
1. criar/atualizar teste
2. rodar e confirmar RED
3. implementar mínimo
4. rodar e obter GREEN
5. refatorar
6. rodar regressão
7. documentar
```
