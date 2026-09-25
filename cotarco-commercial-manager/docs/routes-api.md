# Matriz de Rotas e APIs

## 1. Convenções

Base: `/api/v1`

Formato: JSON salvo upload/download.

Autenticação: Bearer token do provedor de Auth.

Erros:

```json
{
  "error": {
    "code": "JOB_NOT_FOUND",
    "message": "Processamento não encontrado",
    "request_id": "..."
  }
}
```

## 2. Rotas Frontend

| Rota | Acesso | Objetivo |
|---|---|---|
| `/login` | público | autenticação |
| `/` | autenticado | redirect para dashboard |
| `/dashboard` | autenticado | visão geral |
| `/processamentos` | autenticado | lista de jobs |
| `/processamentos/novo` | Comercial+ | criar job |
| `/processamentos/[id]` | autorizado | detalhe |
| `/processamentos/[id]/revisao` | autorizado | preview/diff |
| `/processamentos/[id]/arquivos` | autorizado | inputs/outputs |
| `/historico` | Operador+ | histórico |
| `/produtos/[ref]` | Operador+ | histórico por referência |
| `/configuracoes/perfis` | Admin | perfis |
| `/configuracoes/templates` | Admin | templates |
| `/configuracoes/regras` | Admin | regras |
| `/configuracoes/integracoes` | Admin | integrações |
| `/auditoria` | Operador+ | audit log |
| `/definicoes` | autenticado | preferências |

## 3. Auth

| Método | Endpoint | Papel | Resultado |
|---|---|---|---|
| GET | `/auth/me` | autenticado | utilizador atual |
| POST | `/auth/logout` | autenticado | sessão revogada conforme estratégia |

## 4. Profiles

| Método | Endpoint | Papel |
|---|---|---|
| GET | `/profiles` | autenticado | lista perfis ativos |
| GET | `/profiles/{id}` | autenticado | detalhes |
| POST | `/profiles` | ADMIN | criar |
| PATCH | `/profiles/{id}` | ADMIN | alterar |
| POST | `/profiles/{id}/publish` | ADMIN | publicar versão config |

## 5. Jobs

| Método | Endpoint | Papel | Idempotência |
|---|---|---|---|
| POST | `/jobs` | COMERCIAL+ | `Idempotency-Key` recomendado |
| GET | `/jobs` | autenticado | — |
| GET | `/jobs/{id}` | autorizado | — |
| POST | `/jobs/{id}/files` | autor/Operador | hash + versão |
| POST | `/jobs/{id}/validate` | autor/Operador | sim |
| GET | `/jobs/{id}/summary` | autorizado | — |
| GET | `/jobs/{id}/items` | autorizado | — |
| GET | `/jobs/{id}/issues` | autorizado | — |
| POST | `/jobs/{id}/reopen` | Operador+ | — |
| POST | `/jobs/{id}/approve` | OPERADOR+ | sim |
| POST | `/jobs/{id}/reject` | OPERADOR+ | sim |
| POST | `/jobs/{id}/process` | OPERADOR+ | obrigatório |
| POST | `/jobs/{id}/cancel` | autorizado conforme estado | sim |
| GET | `/jobs/{id}/files/{file_id}/download` | autorizado | — |

## 6. Histórico

| Método | Endpoint | Papel |
|---|---|---|
| GET | `/history/prices` | Operador+ |
| GET | `/history/stock` | Operador+ |
| GET | `/history/products/{reference}` | Operador+ |
| GET | `/audit` | Operador+ |

## 7. Gemini

| Método | Endpoint | Papel |
|---|---|---|
| POST | `/jobs/{id}/ai/summary` | autenticado autorizado |
| POST | `/jobs/{id}/ai/explain-issue` | autenticado autorizado |
| POST | `/jobs/{id}/ai/analyze` | autenticado autorizado |
| POST | `/jobs/{id}/ai/suggest-mapping` | COMERCIAL+ |

Limites, rate-limit e logging por utilizador são obrigatórios.

## 8. Admin

| Método | Endpoint | Papel |
|---|---|---|
| GET | `/admin/users` | ADMIN |
| PATCH | `/admin/users/{id}` | ADMIN |
| GET | `/admin/rules` | ADMIN |
| GET | `/admin/templates` | ADMIN |
| POST | `/admin/templates` | ADMIN |
| PATCH | `/admin/templates/{id}` | ADMIN |
| GET | `/admin/integrations` | ADMIN |
| POST | `/admin/integrations/{id}/test` | ADMIN |

## 9. Status codes

- `200` leitura/ação concluída;
- `201` recurso criado;
- `202` processamento assíncrono aceite;
- `400` payload inválido;
- `401` não autenticado;
- `403` sem autorização;
- `404` não encontrado;
- `409` conflito/idempotência/estado inválido;
- `413` ficheiro demasiado grande;
- `422` falha de validação de domínio;
- `429` rate limit;
- `500` erro inesperado;
- `502/503` dependência externa.

## 10. Contratos-chave

### Criar Job

```json
POST /api/v1/jobs
{
  "profile_id": "uuid",
  "source_system": "SAMSUNG",
  "description": "Tabela preços setembro",
  "options": {}
}
```

### Resultado de validação

```json
{
  "job_id": "uuid",
  "status": "READY_FOR_REVIEW",
  "summary": {
    "total": 1248,
    "updated": 843,
    "new": 102,
    "ignored": 271,
    "blocked": 20
  },
  "issues": {
    "blocker": 20,
    "error": 0,
    "warning": 12,
    "info": 0
  }
}
```

### Item do diff

```json
{
  "reference": "RS64R53112A",
  "old_price": 2393787.53,
  "new_price": 2614035.09,
  "variation_pct": 9.20,
  "old_stock": 0,
  "new_stock": 3,
  "decision": "UPDATE",
  "decision_code": "PRICE_AND_STOCK_UPDATE"
}
```

## 11. API adapter para WooCommerce — futuro

Interface lógica:

```text
WooCommerceAdapter
├── health_check()
├── find_product_by_sku(sku)
├── get_product_snapshot(sku)
├── preview_changes(changes)
├── apply_batch(changes)
└── verify_result(operation_id)
```

A API oficial atual usa `/wp-json/wc/v3/` e suporta produtos, incluindo batch operations; o endpoint de batch tem limite padrão documentado de até 100 objetos por pedido, portanto o adapter deve implementar chunking configurável e verificação pós-escrita.
