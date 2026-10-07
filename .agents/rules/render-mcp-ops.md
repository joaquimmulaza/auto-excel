---
trigger: always_on
---

# Render MCP — ops obrigatório

Usar o [Render MCP](https://render.com/docs/mcp-server) para qualquer alteração de env, deploy ou troubleshooting do backend `cotarco-ccm-api`. Não declarar deploy OK só pelo Dashboard screenshot.

## Workspace e serviço Cotarco

- Workspace: `My Workspace` — `workspaceId=tea-cv51l1lumphs73fcoag0`
- Serviço: `cotarco-ccm-api` — `serviceId=srv-db3clte0tbcc73d73et0`
- URL: `https://cotarco-ccm-api.onrender.com`
- Passar `workspaceId` em todas as calls MCP (não depender só de sessão).

## Protocolo antes / depois de deploy

1. `list_workspaces` → confirmar workspace.
2. `list_services` / `get_service` → confirmar branch, plan, URL.
3. Após `update_environment_variables` ou `trigger_deploy`:
   - `list_deploys` + `get_deploy` até status terminal (`live` / `build_failed` / `update_failed` / equivalente).
   - Em falha ou dúvida: `list_logs` com `level=error` e texto `sqlite|startup failed|Traceback|SettingsError|DATABASE_URL`.
4. Smoke: `GET https://cotarco-ccm-api.onrender.com/health` deve devolver 200.
5. Só depois avançar para passos seguintes (ex.: Vercel `NEXT_PUBLIC_API_URL`).

## Checklist env de produção (cotarco-ccm-api)

| Key | Origem |
|---|---|
| `ENVIRONMENT=production` | MCP / Dashboard |
| `AUTH_MODE=supabase` | MCP / Dashboard |
| `STORAGE_BACKEND=supabase` | MCP / Dashboard |
| `STORAGE_BUCKET=job-files` | MCP / Dashboard |
| `SUPABASE_URL` | Supabase MCP `get_project_url` |
| `SUPABASE_ANON_KEY` | Supabase MCP `get_publishable_keys` (anon) |
| `ALLOWED_ORIGINS` | URL frontend Vercel |
| `DATABASE_URL` | **Manual** no Dashboard (pooler URI; nunca no chat) |
| `SUPABASE_SERVICE_ROLE_KEY` | **Manual** no Dashboard (nunca no chat) |
| `GEMINI_API_KEY` | **Manual** no Dashboard (nunca no chat) |

SQLite é proibido em production (fail-fast na app). Schema e seeds vêm das migrations Supabase.

## Limitações MCP

- Não existe `list_environment_variables` — não dump secrets.
- Validar secrets por sintomas nos logs + `/health`, não por valores.
- `update_environment_variables` faz merge por defeito; usar `replace=true` só com intenção explícita.
- Após update de env o Render pode disparar deploy automaticamente — sempre ler logs.

## Sintoma conhecido (já corrigido com fail-fast)

`sqlite3.OperationalError: no such table: commercial_profiles` em production = `DATABASE_URL` ausente (default SQLite) + sem `create_all`. Corrigir: definir `DATABASE_URL` Postgres no Dashboard e redeploy; confirmar com `list_logs`.
