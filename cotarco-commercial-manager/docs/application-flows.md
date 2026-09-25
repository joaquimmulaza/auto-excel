# Fluxos da Aplicação

## 1. Fluxo principal — Comercial

```text
Login
  ↓
Dashboard
  ↓
Novo processamento
  ↓
Selecionar perfil comercial
  ↓
Upload Excel
  ↓
Validação estrutural
  ↓
Normalização + regras
  ↓
Preview / Diff
  ↓
┌──────────────────────────────┐
│ Existem blockers/erros?      │
└──────────────┬───────────────┘
               │
        Sim ───┴─── Não
         ↓           ↓
NEEDS_CORRECTION   READY_FOR_REVIEW
         ↓           ↓
Corrigir/reupload   Operador revê
                     ↓
                  Aprovar
                     ↓
                 PROCESSING
                     ↓
                  COMPLETED
                     ↓
               Excel + log
                     ↓
                  Histórico
```

## 2. Fluxo do Operador

```text
Dashboard
  ↓
Fila de revisão
  ↓
Abrir job
  ↓
Ver resumo
  ↓
Filtrar blockers/warnings
  ↓
Abrir itens suspeitos
  ↓
Aprovar / rejeitar
  ↓
Executar processamento
  ↓
Validar output
  ↓
Disponibilizar download
```

## 3. Fluxo de correção

```text
Job = NEEDS_CORRECTION
        ↓
Comercial abre job
        ↓
Lista de problemas
        ↓
Baixar/abrir tabela original
        ↓
Corrigir no Excel
        ↓
Enviar nova versão
        ↓
Nova validação
        ↓
READY_FOR_REVIEW ou NEEDS_CORRECTION
```

Não apagar a versão anterior; criar versionamento.

## 4. Fluxo de processamento

```text
APPROVED
   ↓
Create processing run
   ↓
Load immutable input version
   ↓
Execute domain rules
   ↓
Generate outputs
   ↓
Validate outputs
   ↓
Persist summary/history/audit
   ↓
COMPLETED
```

Uma falha em qualquer etapa deve resultar em `FAILED` e não em `COMPLETED`.

## 5. Fluxo Gemini

```text
Utilizador clica "Explicar alerta"
             ↓
Backend reúne apenas contexto necessário
             ↓
Sanitiza/minimiza dados
             ↓
Gemini
             ↓
Schema estruturado
             ↓
Backend valida resposta
             ↓
UI mostra "Assistência de IA"
```

Gemini nunca muda `job.status`, nunca altera preço e nunca aprova.

## 6. Fluxo de perfil configurável

```text
Admin cria/edita Profile
       ↓
Define campos/template
       ↓
Define rules_version
       ↓
Publica configuração
       ↓
Novo job seleciona profile
       ↓
Engine carrega config versionada
```

## 7. Fluxo WooCommerce futuro

```text
COMPLETED
   ↓
Operator selects "Preparar publicação"
   ↓
Adapter WooCommerce
   ↓
Fetch remote product snapshot
   ↓
Compare
   ↓
Preview
   ↓
Explicit confirmation
   ↓
Batch update
   ↓
Verify response
   ↓
Audit
```

A documentação oficial atual do WooCommerce disponibiliza REST API v3 para produtos e operações de batch; ainda assim, a integração só deve ser ativada depois de testes contra o ambiente real da Cotarco.

## 8. Fluxo Mano

No MVP:

```text
COMPLETED
   ↓
Gerar ficheiro compatível
   ↓
Download
   ↓
Operador atualiza Mano manualmente
```

Nenhuma hipótese de API deve ser codificada como facto até existir documentação/credencial verificável.
