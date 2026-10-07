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
| Região Supabase | `eu-west-1` (Irlanda) |
| Storage bucket | `job-files` (privado) |
| JWT | **ES256** via JWKS (Signing Keys) |
| Cloud Run region (recomendado) | `europe-west1` |
| Vercel root directory | `frontend/` |
| Container SoT | `Dockerfile` na raiz do repo |

Não reutilizar os projetos Supabase/Vercel `boleia` ou `Makini`.

---

## Supabase Auth / JWT

Inspecção do endpoint público:

```text
GET https://gaofsokeaqymsmgyjwfm.supabase.co/auth/v1/.well-known/jwks.json
→ keys[].alg = ES256 (EC P-256)
```

| Campo | Valor |
|---|---|
| JWT algorithm | ES256 |
| JWT verification strategy | JWKS / public key (`PyJWKClient`) |
| JWKS URL | `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` |
| Legacy JWT secret (HS256) | Opcional; só se o token declarar `alg=HS256` |

Não é necessário migrar o projeto para Signing Keys — **já está** em ES256.

A role **nunca** vem do JWT/`user_metadata`. Fluxo:

```text
JWT (JWKS) → sub → public.users.role
```

Trigger `handle_new_auth_user` cria sempre `role = COMERCIAL`. Elevação OPERADOR/ADMIN só via SQL/admin autorizado.

### Contas de teste (apenas documentação local — NÃO no frontend)

| Email | Role (public.users) |
|---|---|
| `comercial@cotarco.ao` | COMERCIAL |
| `operador@cotarco.ao` | OPERADOR |
| `admin@cotarco.ao` | ADMIN |

Passwords: geridas no Supabase Auth Dashboard / secrets locais — nunca em `NEXT_PUBLIC_*` nem no bundle.

---

## Supabase Storage

- Bucket `job-files`: `public = false`
- Policies: `anon` e `authenticated` **não** acedem a `job-files`
- Uploads/downloads: backend com **service role** (server-side only)
- Signed URLs disponíveis via adapter quando necessário

---

## Secrets backend (nunca no frontend)

| Variável | Notas |
|---|---|
| `DATABASE_URL` | Pooler / Transaction mode recomendado para Cloud Run |
| `SUPABASE_URL` | Também usado para JWKS |
| `SUPABASE_ANON_KEY` | Backend opcional; frontend usa `NEXT_PUBLIC_*` |
| `SUPABASE_SERVICE_ROLE_KEY` | **Só** backend / Secret Manager |
| `GEMINI_API_KEY` | Só backend |
| `ALLOWED_ORIGINS` | Allowlist explícita (URL Vercel) |

`SUPABASE_JWT_SECRET` **não** é necessário para o fluxo ES256 actual.

---

## Backend — Cloud Run

Container: `Dockerfile` na raiz (único). Script: `scripts/deploy-cloud-run.sh`.

Secrets Secret Manager (sem valores em `--set-env-vars`):

- `cotarco-database-url`
- `cotarco-supabase-url`
- `cotarco-supabase-anon`
- `cotarco-supabase-service-role`
- `cotarco-gemini-api-key`
- `cotarco-allowed-origins`

Env não secretos: `ENVIRONMENT=production`, `AUTH_MODE=supabase`, `STORAGE_BACKEND=supabase`, `STORAGE_BUCKET=job-files`.

Recursos: 1Gi / 1 CPU / timeout 300s / min 0 / max 3.

```bash
export GCP_PROJECT_ID=seu-projeto
export GCP_REGION=europe-west1
./scripts/deploy-cloud-run.sh
```

---

## Frontend — Vercel

### Estado inspeccionado (equipa `joaquim-mulazas-projects`)

| Project | ID | Notas |
|---|---|---|
| `boleia` | `prj_mWWuYRj49kPqDq9IRD68Y6YtLEib` | Outro produto — **não** reutilizar |
| `auto-excel` | — | **404 / não existe** nesta equipa |
| `frontend` | — | **404 / não existe** nesta equipa |

Criação via MCP falhou com `403 forbidden`. Criar manualmente no dashboard:

1. Import `joaquimmulaza/auto-excel`
2. Nome sugerido: `cotarco-ccm` ou `auto-excel`
3. **Root Directory:** `frontend`
4. Framework: Next.js
5. Env (Preview + Production):

| Variável | Valor |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<cloud-run-url>/api/v1` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://gaofsokeaqymsmgyjwfm.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | anon/publishable key |

Nunca `SUPABASE_SERVICE_ROLE_KEY` no Vercel.

`vercel.json` na raiz **não** define serviço FastAPI.

---

## Desenvolvimento local

```bash
export ENVIRONMENT=local AUTH_MODE=local STORAGE_BACKEND=local
export DATABASE_URL=sqlite+pysqlite:////tmp/cotarco-ccm.db
# backend
uvicorn backend.app.main:app --reload --app-dir .
# frontend
cd frontend && npm run dev
```

Demo passwords locais: apenas com `AUTH_MODE=local` no backend (seed), nunca embutidas no UI de produção.

---

## Troubleshooting

| Sintoma | Verificação |
|---|---|
| 401 / JWT | JWKS alcançável; `SUPABASE_URL` correcto; token access |
| CORS | `ALLOWED_ORIGINS` com domínio Vercel exacto |
| Upload | `STORAGE_BACKEND=supabase` + service role |
| Role errada | `public.users.role` — não claim do frontend |
