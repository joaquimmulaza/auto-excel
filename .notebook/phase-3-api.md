# Fase 3 — FastAPI & Endpoints

**Data**: 2026-09-28
**Status**: ✅ COMPLETO — 96 testes passados (Fases 1+2+3), 0 falhas

---

## Ficheiros Criados

| Ficheiro | Responsabilidade |
|---|---|
| `backend/app/api/__init__.py` | Package marker |
| `backend/app/api/deps.py` | DI: `get_db`, `get_current_user`, `require_role`, `CurrentUser` |
| `backend/app/api/errors.py` | Error handlers: `make_error_body`, `http_exception_handler`, `validation_exception_handler` |
| `backend/app/schemas/__init__.py` | Package marker |
| `backend/app/schemas/profile.py` | `ProfileResponse`, `ProfileListResponse` |
| `backend/app/schemas/job.py` | `JobCreateRequest`, `JobResponse`, `JobListResponse`, `ApprovalRequest`, `ApprovalResponse` |
| `backend/app/schemas/processing.py` | `JobItemResponse`, `ValidationIssueResponse`, `JobSummaryResponse` |
| `backend/app/api/v1/__init__.py` | Package marker |
| `backend/app/api/v1/profiles.py` | `GET /api/v1/profiles`, `GET /api/v1/profiles/{id}` |
| `backend/app/api/v1/jobs.py` | `POST /api/v1/jobs`, `GET /api/v1/jobs`, `GET /api/v1/jobs/{id}` |
| `backend/app/api/v1/processing.py` | `POST /jobs/{id}/validate`, `GET /jobs/{id}/summary`, `GET /jobs/{id}/items`, `GET /jobs/{id}/issues` |
| `backend/app/api/v1/approvals.py` | `POST /jobs/{id}/approve` (OPERADOR/ADMIN only) |
| `backend/app/api/v1/router.py` | Agregador do `v1_router` |
| `backend/app/main.py` | FastAPI app factory com CORS, error handlers, routes |
| `backend/tests/test_api/__init__.py` | Package marker |
| `backend/tests/test_api/conftest.py` | Fixtures TDD: engine, session, seed, clients |
| `backend/tests/test_api/test_profiles_api.py` | 5 testes de profiles |
| `backend/tests/test_api/test_jobs_api.py` | 7 testes de jobs + RBAC |
| `backend/tests/test_api/test_processing_api.py` | 8 testes de processing |
| `backend/tests/test_api/test_approvals_api.py` | 4 testes de approvals + RBAC crítico |

---

## Endpoints Implementados

| Método | Path | Roles | Status HTTP |
|---|---|---|---|
| GET | `/api/v1/profiles` | Any auth | 200 |
| GET | `/api/v1/profiles/{id}` | Any auth | 200 / 404 |
| POST | `/api/v1/jobs` | Any auth | 201 |
| GET | `/api/v1/jobs` | COMERCIAL=próprios; OPERADOR/ADMIN=todos | 200 |
| GET | `/api/v1/jobs/{id}` | COMERCIAL=próprios only | 200 / 403 / 404 |
| POST | `/api/v1/jobs/{id}/validate` | Any auth (own job) | 202 / 409 / 404 |
| GET | `/api/v1/jobs/{id}/summary` | Any auth (own job) | 200 / 404 |
| GET | `/api/v1/jobs/{id}/items` | Any auth (own job) | 200 |
| GET | `/api/v1/jobs/{id}/issues` | Any auth (own job) | 200 |
| POST | `/api/v1/jobs/{id}/approve` | **OPERADOR/ADMIN** (COMERCIAL → **403**) | 200 / 403 / 409 / 404 |
| GET | `/health` | Public | 200 |

---

## RBAC EVIDENCE

**`test_comercial_cannot_approve_returns_403`**: PASSED ✅

```
COMERCIAL tenta POST /api/v1/jobs/{job_id}/approve
→ HTTP 403 {"error": {"code": "FORBIDDEN", ...}}
```

O `require_role("OPERADOR", "ADMIN")` no router de approvals interceta o request **antes** de entrar no handler, garantindo que COMERCIAL nunca consegue aprovar.

---

## Gotchas & Decisões de Arquitetura

### 1. SQLite in-memory com múltiplas conexões
`sqlite+pysqlite:///:memory:` cria uma **DB separada por conexão**. Usar `StaticPool` da SQLAlchemy força todas as conexões a partilhar a mesma instância — essencial quando `seed_db`, `get_db` override, e `db_session` precisam de ver os mesmos dados.

**Referência**: `conftest.py:test_engine()` — `poolclass=StaticPool`

### 2. Dois clientes ativos no mesmo teste (RBAC)
`app.dependency_overrides` é um dict global. Quando `comercial_client` e `operador_client` são usados no mesmo teste, o segundo override sobrescreve o primeiro.

**Fix**: `ContextVar[CurrentUser]` — cada cliente define a variável antes de cada request via `_UserClient._with_user()`. O override do `get_current_user` lê do `ContextVar`.

**Referência**: `conftest.py:_current_user_var`, `_UserClient`

### 3. sessionmaker() como context manager
`sessionmaker()()`  não é context manager diretamente. Usar `Session = session_factory()` com `try/finally session.close()` explícito.

### 4. Legacy main.py intacto
`c:\up_prices\main.py` (root) não foi modificado. A nova app FastAPI reside em `backend/app/main.py`.

---

## Contagem Final de Testes

```
96 passed in 0.80s
├── Fase 1 (Domain Engine):        25 testes
├── Fase 2 (Database/Schema):      35 testes  
└── Fase 3 (FastAPI API):          36 testes
```
