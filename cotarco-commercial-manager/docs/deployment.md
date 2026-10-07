# Deployment — Cotarco Commercial Manager

## Arquitetura alvo

```text
Vercel (frontend/)  →  HTTPS  →  Cloud Run (FastAPI)
                                      ↓
                               Supabase (PostgreSQL + Auth + Storage)
```

## Decisões

| Item | Valor |
|---|---|
| Supabase project | `cotarco-ccm` |
| Project ref | `gaofsokeaqymsmgyjwfm` |
| Região Supabase | `eu-west-1` (Irlanda) — EU, isolado de `boleia` |
| Storage bucket | `job-files` (privado) |
| Cloud Run region (recomendado) | `europe-west1` |
| Vercel root directory | `frontend/` |

Não reutilizar os projetos Supabase/Vercel `boleia` ou `Makini`.

---

## Supabase

### Já aplicado neste setup

- Migrations `001`–`004` (+ RLS + seed profiles + `password_hash`)
- Trigger `handle_new_auth_user` (auth.users → public.users)
- Users de teste: `comercial@` / `operador@` / `admin@cotarco.ao`
- Bucket privado `job-files` com policies autenticadas

### Secrets a configurar no backend (nunca no frontend)

| Variável | Onde obter |
|---|---|
| `DATABASE_URL` | Supabase → Settings → Database → Connection string (pooler / Transaction mode recomendado para Cloud Run) |
| `SUPABASE_URL` | Project URL |
| `SUPABASE_ANON_KEY` | API anon key |
| `SUPABASE_SERVICE_ROLE_KEY` | service_role (só backend) |
| `SUPABASE_JWT_SECRET` | Settings → API → JWT Secret |

### Auth users (produção)

Criar utilizadores reais no Supabase Auth Dashboard. O trigger sincroniza `public.users` com role default `COMERCIAL`. Ajustar role com SQL privilegiado:

```sql
UPDATE public.users SET role = 'OPERADOR' WHERE email = '...';
```

---

## Backend — Cloud Run (manual até GCP estar pronto)

### Pré-requisitos

1. Criar projeto GCP dedicado + billing
2. Instalar/autenticar `gcloud`
3. Criar secrets no Secret Manager (nomes usados por `scripts/deploy-cloud-run.sh`):
   - `cotarco-database-url`
   - `cotarco-supabase-url`
   - `cotarco-supabase-anon`
   - `cotarco-supabase-service-role`
   - `cotarco-supabase-jwt-secret`
   - `cotarco-gemini-api-key`
   - `cotarco-allowed-origins` (ex.: `https://seu-frontend.vercel.app`)

### Deploy

```bash
export GCP_PROJECT_ID=seu-projeto
export GCP_REGION=europe-west1
./scripts/deploy-cloud-run.sh
```

Validar:

- `GET {URL}/health`
- `GET {URL}/docs`
- `GET {URL}/api/v1/...` com Bearer Supabase

Recursos sugeridos (MVP / free-tier friendly): 1Gi RAM, 1 CPU, timeout 300s, min 0, max 3.

---

## Frontend — Vercel

> **Acção manual necessária:** a criação automática do projecto Vercel via MCP falhou com `403 forbidden` neste ambiente. Criar no dashboard:

1. [vercel.com/new](https://vercel.com/new) → import `joaquimmulaza/auto-excel`
2. Project name: `cotarco-ccm` (ou `auto-excel-frontend`)
3. Team: `joaquim-mulazas-projects`
4. **Root Directory:** `frontend`
5. Framework: Next.js
6. Environment variables (Preview + Production):

| Variável | Valor |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<cloud-run-url>/api/v1` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://gaofsokeaqymsmgyjwfm.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | anon key (publishable) |

Nunca definir `SUPABASE_SERVICE_ROLE_KEY` no Vercel.

O `vercel.json` na raiz já **não** hospeda FastAPI — backend corre no Cloud Run.

---

## Desenvolvimento local

```bash
# Backend
export ENVIRONMENT=local AUTH_MODE=local STORAGE_BACKEND=local
export DATABASE_URL=sqlite+pysqlite:////tmp/cotarco-ccm.db
cd backend && uvicorn backend.app.main:app --reload --app-dir ..

# Frontend
cd frontend
cp .env.example .env.local   # NEXT_PUBLIC_API_URL=http://localhost:8000/api/v1
npm run dev
```

Com Supabase Auth local: definir `NEXT_PUBLIC_SUPABASE_*` e `AUTH_MODE=supabase` no backend + JWT secret.

---

## Troubleshooting

| Sintoma | Verificação |
|---|---|
| CORS error | `ALLOWED_ORIGINS` inclui o domínio Vercel exacto |
| 401 INVALID_TOKEN | `SUPABASE_JWT_SECRET` correcto; token access (não refresh) |
| Upload falha em prod | `STORAGE_BACKEND=supabase` + service role + bucket `job-files` |
| Schema mismatch | Reaplicar migrations; não usar `create_all` em produção |
| Role errada | `public.users.role` — nunca confiar no claim do frontend |

---

## Gaps conhecidos de infra

- Deploy Cloud Run depende de billing/auth GCP do utilizador
- Domínio customizado / MFA / retenção de ficheiros — futuro
- Regras BFA/KERO/SIAC continuam placeholder (`business_rules_confirmed: false`)
