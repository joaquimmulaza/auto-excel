# Fase 1 — Extração do Engine de Domínio (Debriefing & Intelligence)

## Resumo Executivo
Na Fase 1 do Cotarco Commercial Manager, extraiu-se o motor de regras de negócio a partir do script legado `main.py` para uma arquitetura limpa em `backend/app/domain/` e `backend/app/services/`, 100% orientada a TDD, puramente determinística em Python 3.12 (sem LLM para finanças/stock) e totalmente desacoplada de CLI.

O ficheiro original `main.py` permaneceu 100% inalterado.

---

## 1. Bugs e Gotchas Identificados no Legado & Soluções Aplicadas

### 1.1 Bug do Preço Zero (Passo 4 do Legado)
- **Problema no Legado**: No `main.py` linha 411, se o fornecedor (Samsung) enviasse preço `<= 0`, o produto existente no catálogo de destino (Mano) recebia esse valor diretamente ou provocava anomalias na lógica posterior. Apenas produtos novos no Passo 5 verificavam `preco == 0.0`.
- **Solução no Novo Motor**:
  * Em [`backend/app/domain/rules.py:evaluate_price_guard()`](file:///c:/up_prices/backend/app/domain/rules.py), a regra `PriceRule.allow_zero_price` (padrão `False`) bloqueia preventivamente preços `<= 0` em produtos existentes, gerando `ValidationIssue` de severidade `BLOCKER` com código `BLOCKED_ZERO_PRICE`.
  * Em produtos novos, itens com preço zero são catalogados com `IGNORED_ZERO_PRICE`.

### 1.2 Sobrescrita Silenciosa de Duplicados (Dicionário Zip)
- **Problema no Legado**: No `main.py` linha 358-359, usava-se `dict(zip(df_samsung['REF_MATCH'], df_samsung['PRECO']))`. Se a tabela de entrada contivesse a mesma referência repetida com valores diferentes, o último sobrescrevia silenciosamente os anteriores sem registo de erro.
- **Solução no Novo Motor**:
  * Em [`backend/app/domain/engine.py:process_price_table()`](file:///c:/up_prices/backend/app/domain/engine.py), realiza-se uma pré-varredura (`detect_duplicates`) que mapeia todas as ocorrências de referências normalizadas.
  * Se houver duplicados, emite-se um `ValidationIssue` com código `DUPLICATE_REFERENCE`, severidade `BLOCKER` e indica-se a lista de todas as linhas afetadas (`details['rows']`), impedindo aplicação cega.

### 1.3 Price Guard Hardcoded vs Dinâmico
- **Problema no Legado**: `LIMIAR_VARIACAO_PRECO = 0.30` estava fixo no código a 30%.
- **Solução no Novo Motor**:
  * O limiar é configurável por perfil de negócio através de [`CommercialProfile.price_rule.max_variation_threshold`](file:///c:/up_prices/backend/app/domain/models.py).
  * Perfis sensíveis podem aplicar 10% ou 15%; perfis mais permissivos podem usar 50%.
  * Variações relativas acima do limiar configurado geram `BLOCKED_PRICE_VARIATION` com severidade `BLOCKER` e a alteração de preço não é aplicada.

### 1.4 Higienização e Normalização Determinística
- Funções em [`backend/app/domain/normalization.py`](file:///c:/up_prices/backend/app/domain/normalization.py):
  * `normalize_col(txt)`: strip, uppercase e remoção de acentos via NFKD ASCII.
  * `ultra_clean(text)`: sanitização estrita preservando apenas `[A-Z0-9-]`.
  * `limpar_preco(val)`: suporte tolerante a moedas (`€`, `EUR`), formato europeu (`2.614.035,09`) e anglo-saxónico (`2614035.09`).
  * `calcular_variacao(old, new)`: cálculo determinístico sem crash em divisão por zero.

---

## 2. Contratos e Modelos Principais

- [`Product`](file:///c:/up_prices/backend/app/domain/models.py): entidade de catálogo com referências canónicas, original e normalizada.
- [`CommercialProfile`](file:///c:/up_prices/backend/app/domain/models.py): encapsula `PriceRule`, `StockRule` e mapeamento de colunas.
- [`ProcessResult`](file:///c:/up_prices/backend/app/domain/models.py): resultado estruturado contendo `items: list[JobItemResult]`, `issues: list[ValidationIssue]`, `summary: ProcessSummary` e `output_records: list[dict]`.

---

## 3. Evidência de Testes TDD
- 36 testes executados via `python -m pytest -v backend/tests/`.
- 100% de sucesso (0 falhas, 0 erros) em 0.59 segundos.
