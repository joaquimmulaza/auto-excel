# Fase 2 — Database & Supabase (Debriefing & Intelligence)

## Resumo Executivo

Na Fase 2 do Cotarco Commercial Manager, modelou-se o schema relacional PostgreSQL completo alinhado com `data-architecture.md`, implementaram-se modelos SQLAlchemy 2.0 com suporte dual (PostgreSQL/JSONB em produção, SQLite/JSON em testes), políticas RLS por papel de utilizador, e 3 migrações SQL idempotentes prontas para execução no Supabase SQL Editor.

**Testes: 35/35 PASSED (Fase 2) + 36/36 PASSED (Fase 1) = 71 testes verdes.**

---

## 1. Ficheiros Criados

| Ficheiro | Propósito |
|---|---|
| [`backend/app/infra/__init__.py`](file:///c:/up_prices/backend/app/infra/__init__.py) | Package de infraestrutura |
| [`backend/app/infra/db/__init__.py`](file:///c:/up_prices/backend/app/infra/db/__init__.py) | Package de base de dados |
| [`backend/app/infra/db/models.py`](file:///c:/up_prices/backend/app/infra/db/models.py) | Modelos SQLAlchemy 2.0 (10 tabelas) |
| [`backend/app/infra/db/session.py`](file:///c:/up_prices/backend/app/infra/db/session.py) | Gestão de engine e sessões |
| [`backend/app/infra/repositories/__init__.py`](file:///c:/up_prices/backend/app/infra/repositories/__init__.py) | Package de repositórios |
| [`backend/app/infra/repositories/profiles.py`](file:///c:/up_prices/backend/app/infra/repositories/profiles.py) | `ProfileRepository` |
| [`backend/app/infra/repositories/jobs.py`](file:///c:/up_prices/backend/app/infra/repositories/jobs.py) | `JobRepository` |
| [`backend/migrations/001_initial_schema.sql`](file:///c:/up_prices/backend/migrations/001_initial_schema.sql) | DDL inicial (idempotente) |
| [`backend/migrations/002_rls_policies.sql`](file:///c:/up_prices/backend/migrations/002_rls_policies.sql) | Políticas RLS |
| [`backend/migrations/003_seed_commercial_profiles.sql`](file:///c:/up_prices/backend/migrations/003_seed_commercial_profiles.sql) | Seed dos 5 perfis iniciais |
| [`backend/tests/test_database/test_schema.py`](file:///c:/up_prices/backend/tests/test_database/test_schema.py) | Suite de testes (35 testes) |

---

## 2. DDL Summary — Tabelas e Chaves Estrangeiras

```
users
  PK: id (UUID)
  UNIQUE: email

commercial_profiles
  PK: id (UUID)
  UNIQUE: code

profile_rules
  PK: id (UUID)
  FK: profile_id → commercial_profiles.id (CASCADE)
  FK: created_by → users.id (SET NULL)
  UNIQUE: (profile_id, version, rule_code)

processing_jobs
  PK: id (UUID)
  UNIQUE: job_number (BIGINT SEQUENCE)
  FK: profile_id → commercial_profiles.id (RESTRICT)
  FK: created_by → users.id (RESTRICT)
  FK: approved_by → users.id (SET NULL)
  INDEX: (profile_id, status), (created_by, created_at DESC)

job_files
  PK: id (UUID)
  FK: job_id → processing_jobs.id (CASCADE)
  FK: uploaded_by → users.id (SET NULL)
  INDEX: (job_id, created_at DESC)

job_items
  PK: id (UUID)
  FK: job_id → processing_jobs.id (CASCADE)
  INDEX: (job_id, reference_normalized)

validation_issues
  PK: id (UUID)
  FK: job_id → processing_jobs.id (CASCADE)
  FK: job_item_id → job_items.id (SET NULL)
  INDEX: (job_id, severity)

approvals
  PK: id (UUID)
  FK: job_id → processing_jobs.id (CASCADE)
  FK: actor_id → users.id (RESTRICT)

price_history  [APPEND-ONLY]
  PK: id (UUID)
  FK: profile_id → commercial_profiles.id (SET NULL)
  FK: job_id → processing_jobs.id (RESTRICT)
  FK: recorded_by → users.id (SET NULL)
  INDEX: (reference_normalized, recorded_at DESC)

audit_logs  [APPEND-ONLY — SECURITY CRITICAL]
  PK: id (UUID)
  FK: actor_id → users.id (SET NULL)
  FK: job_id → processing_jobs.id (SET NULL)
  INDEX: (entity_type, entity_id, created_at DESC)
```

**Enums definidos:**
- `user_role`: COMERCIAL | OPERADOR | ADMIN
- `job_status`: UPLOADED | VALIDATING | READY_FOR_REVIEW | NEEDS_CORRECTION | APPROVED | PROCESSING | COMPLETED | FAILED | CANCELLED

---

## 3. Gotcha: `_JsonColumn` / `_UuidColumn` Dialect-Aware Types

**Problema descoberto:** `JSONB` e `UUID` do PostgreSQL não são suportados pelo SQLite (usado nos testes in-memory). SQLAlchemy levanta `UnsupportedCompilationError`.

**Solução aplicada em [`models.py`](file:///c:/up_prices/backend/app/infra/db/models.py):**

```python
class _JsonColumn(TypeDecorator):
    impl = JSON
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(JSONB())
        return dialect.type_descriptor(JSON())

class _UuidColumn(TypeDecorator):
    impl = SAString
    def load_dialect_impl(self, dialect):
        if dialect.name == "postgresql":
            return dialect.type_descriptor(PgUUID(as_uuid=True))
        return dialect.type_descriptor(SAString(36))
```

A produção continua a usar JSONB/UUID nativos do PostgreSQL. Os testes correm em SQLite sem qualquer mock.

---

## 4. Gotcha: `metadata` Reservado pelo SQLAlchemy Declarative

`metadata` é um atributo interno do `DeclarativeBase`. Nomear uma coluna ORM com esse nome causa `InvalidRequestError`.

**Solução:** O atributo Python é `extra_metadata`; o nome da coluna no DB é `"metadata"` via mapeamento explícito:

```python
extra_metadata: Mapped[...] = mapped_column("metadata", _JsonColumn(), nullable=True)
```

Referência: [`AuditLogOrm`](file:///c:/up_prices/backend/app/infra/db/models.py) em `models.py`.

---

## 5. RLS Audit — Políticas Aplicadas

| Tabela | COMERCIAL | OPERADOR | ADMIN | Restrição Extra |
|---|---|---|---|---|
| `users` | SELECT próprio | SELECT todos | FULL | — |
| `commercial_profiles` | SELECT activos | SELECT activos | FULL | — |
| `profile_rules` | SELECT | SELECT | FULL | — |
| `processing_jobs` | SELECT/INSERT/UPDATE próprios + status UPLOADED/NEEDS_CORRECTION | SELECT/UPDATE todos | FULL | INSERT exige `created_by = auth.uid()` |
| `job_files` | SELECT/INSERT jobs próprios | SELECT todos | FULL | — |
| `job_items` | SELECT jobs próprios | SELECT todos | FULL | — |
| `validation_issues` | SELECT/UPDATE(resolved) jobs próprios | SELECT todos | FULL | — |
| `approvals` | SELECT jobs próprios | INSERT/SELECT | FULL | COMERCIAL não pode inserir |
| `price_history` | SELECT jobs próprios | SELECT todos | FULL | Sem UPDATE/DELETE |
| `audit_logs` | — | SELECT | FULL | **APPEND-ONLY: nenhuma policy de UPDATE/DELETE** |

**Função helper:** `current_user_role()` resolve o papel do utilizador autenticado via `auth.uid()` → `users.role`.

---

## 6. Seed dos Perfis Iniciais

| Code | Type | Variação | Stock Mín | Integração |
|---|---|---|---|---|
| `MANO` | MARKETPLACE | 30% | 3 | EXCEL_EXPORT |
| `WOOCOMMERCE` | STORE | 30% | 1 | EXCEL_EXPORT (WC desativado — feature flag) |
| `BFA` | PARTNER | **10%** | 0 | EXCEL_EXPORT |
| `KERO` | RESELLER | 30% | 0 | EXCEL_EXPORT |
| `SIAC` | RESELLER | 30% | 0 | EXCEL_EXPORT |

> **IMPORTANTE:** Os parâmetros de BFA, KERO e SIAC são **placeholders**. Regras comerciais exactas devem ser confirmadas com a gestão antes de produção (`business_rules_confirmed: false` nos configs).

---

## 7. Decisões Arquitecturais Registadas

### ADR-implícita: Sem Alembic no MVP

O projecto usa **migrações SQL manuais** (`001_initial_schema.sql`, etc.) executadas no Supabase SQL Editor em vez de Alembic auto-gerado. Motivo: o plano Free do Supabase não expõe a conexão directa de forma simples para Alembic; as migrações SQL manuais são mais portáveis e auditáveis para este contexto.

Se no futuro o backend tiver acesso directo ao PostgreSQL (ex.: Cloud Run com pool), Alembic pode ser adicionado usando `alembic init` com a base ORM já definida.

### Separação DB/Storage

- **PostgreSQL (Supabase DB):** metadata de ficheiros, jobs, itens, histórico, auditoria.
- **Supabase Storage:** ficheiros binários Excel (input/output). Apenas o `storage_path` e `sha256` ficam no DB.

---

## 8. Próximo Passo

**Fase 3 — FastAPI & Endpoints**

Dependências já prontas:
- Modelos ORM (`models.py`) ✅
- Session factory (`session.py`) ✅
- Repositories (`profiles.py`, `jobs.py`) ✅

Próximos ficheiros a criar:
- `backend/app/api/` — routers FastAPI
- `backend/app/api/deps.py` — dependências (sessão, utilizador actual)
- `backend/app/api/routes/profiles.py` — GET /profiles, POST /profiles
- `backend/app/api/routes/jobs.py` — CRUD de jobs
- `backend/app/api/routes/processing.py` — trigger do motor de domínio
- Middleware: autenticação Supabase JWT, request_id, audit log automático
