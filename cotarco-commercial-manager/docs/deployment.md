# Deployment — Cotarco Commercial Manager

## Arquitetura alvo

```text
Vercel (frontend/)  →  HTTPS  →  Render Free (FastAPI)
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
| Backend hosting | **Render Free Web Service** |
| Render service | `cotarco-ccm-api` (`srv-db3clte0tbcc73d73et0`) |
| Render URL | `https://cotarco-ccm-api.onrender.com` |
| Render dashboard | `https://dashboard.render.com/web/srv-db3clte0tbcc73d73et0` |
| Render region | `frankfurt` |
| Auto-Deploy | Off (`autoDeploy=no`) |
| Vercel root directory | `frontend/` |
| Container | `Dockerfile` na raiz — só local/opcional; produção = Python nativo no Render |

Não reutilizar serviços Render de outros produtos (`sobaixa-api`, `fardo-fashion-ecommerce`) nem projetos Supabase/Vercel `boleia` / `Makini`.

**Cloud Run / GCP:** abandonado para o MVP (billing). O script `scripts/deploy-cloud-run.sh` foi removido. Não fazer deploy para Google Cloud neste produto.

---

## Supabase Auth / JWT

```text
GET https://gaofsokeaqymsmgyjwfm.supabase.co/auth/v1/.well-known/jwks.json
→ keys[].alg = ES256 (EC P-256)
```

| Campo | Valor |
|---|---|
| JWT algorithm | ES256 |
| JWT verification strategy | JWKS / public key (`PyJWKClient`) |
| JWKS URL | `{SUPABASE_URL}/auth/v1/.well-known/jwks.json` |
| Legacy JWT secret (HS256) | Opcional |

Role **nunca** vem do JWT/`user_metadata`:

```text
JWT (JWKS) → sub → public.users.role
```

Trigger `handle_new_auth_user` cria sempre `role = COMERCIAL`.

### Contas de teste (documentação local — NÃO no frontend)

| Email | Role |
|---|---|
| `comercial@cotarco.ao` | COMERCIAL |
| `operador@cotarco.ao` | OPERADOR |
| `admin@cotarco.ao` | ADMIN |

Passwords: só Supabase Auth Dashboard / secrets locais — nunca em `NEXT_PUBLIC_*`.

---

## Supabase Storage

- Bucket `job-files`: `public = false`
- Policies: `anon` / `authenticated` não acedem a `job-files`
- Uploads/downloads: backend com **service role** (server-side only)

---

## Backend — Render Free

Blueprint: [`render.yaml`](../../render.yaml) na raiz do repo.

| Setting | Valor |
|---|---|
| Type | Web Service |
| Name | `cotarco-ccm-api` |
| Repo | `https://github.com/joaquimmulaza/auto-excel` |
| Branch | `cursor/prod-architecture-supabase-7a1e` (até merge) |
| Runtime | Python |
| Root Directory | `.` (raiz) |
| Build | `pip install --upgrade pip && pip install -r backend/requirements.txt` |
| Start | `PYTHONPATH=. uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT` |
| Plan | Free |
| Region | Frankfurt |
| Health Check | Definir `/health` no Dashboard (MCP create não expõe este campo) |
| Auto-Deploy | Off (`autoDeploy=no`) |

Nota: a criação do serviço via MCP pode iniciar um build inicial automático. **Não** voltar a chamar `trigger_deploy` até secrets estarem preenchidos. Esse build pode falhar sem `DATABASE_URL` / Supabase — esperado.

### Environment variables (Render)

| Variable | Required | Secret? | Purpose |
|---|---|---|---|
| `ENVIRONMENT` | yes | no | `production` |
| `AUTH_MODE` | yes | no | `supabase` |
| `STORAGE_BACKEND` | yes | no | `supabase` |
| `STORAGE_BUCKET` | yes | no | `job-files` |
| `SUPABASE_URL` | yes | no | Project URL + JWKS |
| `SUPABASE_ANON_KEY` | yes | no | Anon key (backend) |
| `SUPABASE_SERVICE_ROLE_KEY` | yes | **yes** | Storage privilegiado |
| `DATABASE_URL` | yes | **yes** | Pooler Supabase PostgreSQL |
| `ALLOWED_ORIGINS` | yes | no | URL(s) Vercel do frontend |
| `GEMINI_API_KEY` | se IA activa | **yes** | Gemini |
| `GEMINI_MODEL` | no | no | default no código |
| `PORT` | auto | no | Injectado pelo Render |

`SUPABASE_JWT_SECRET` **não** é necessário para ES256/JWKS.

### Free tier notes

- Cold start após inactividade (~spin down).
- Memória limitada — Pandas/OpenPyXL OK para ficheiros pequenos do MVP.
- Sem Redis/filas/Cloud SQL no Render.

### Primeiro deploy (manual)

1. Confirmar serviço `cotarco-ccm-api` no Dashboard.
2. Preencher secrets no Dashboard (nunca no git/chat).
3. Autorizar o primeiro deploy.
4. Validar `GET https://<service>.onrender.com/health`.
5. Configurar Vercel `NEXT_PUBLIC_API_URL=https://<service>.onrender.com/api/v1`.

---

## Frontend — Vercel

1. Projecto dedicado, **Root Directory:** `frontend`
2. Framework: Next.js
3. Env:

| Variável | Valor |
|---|---|
| `NEXT_PUBLIC_API_URL` | `https://<render-service>.onrender.com/api/v1` |
| `NEXT_PUBLIC_SUPABASE_URL` | `https://gaofsokeaqymsmgyjwfm.supabase.co` |
| `NEXT_PUBLIC_SUPABASE_ANON_KEY` | anon/publishable key |

Nunca `SUPABASE_SERVICE_ROLE_KEY` no Vercel. `vercel.json` na raiz **não** hospeda FastAPI.

---

## Desenvolvimento local

```bash
export ENVIRONMENT=local AUTH_MODE=local STORAGE_BACKEND=local
export DATABASE_URL=sqlite+pysqlite:////tmp/cotarco-ccm.db
uvicorn backend.app.main:app --reload --app-dir .
cd frontend && npm run dev
```

---

## Troubleshooting

| Sintoma | Verificação |
|---|---|
| 401 / JWT | JWKS alcançável; `SUPABASE_URL` correcto |
| CORS | `ALLOWED_ORIGINS` com domínio Vercel exacto |
| Upload | `STORAGE_BACKEND=supabase` + service role |
| Cold start lento | Free tier — aguardar wake-up |
| Role errada | `public.users.role` — não claim do frontend |
