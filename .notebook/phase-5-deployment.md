# Fase 5 — Deploy Cloud (Vercel Production)

## 1. Visão Geral
Deploy de produção do frontend **Cotarco Commercial Manager** na Vercel (projeto GitHub `joaquimmulaza/auto-excel`), usado para demonstração e validação em cloud.

---

## 2. Estado Actual (projecto `auto-excel`)

| Item | Valor |
|------|-------|
| **Status** | Produção activa (site público responde; título Cotarco Commercial Manager) |
| **Projecto Vercel** | `auto-excel` |
| **Team** | `joaquim-mulazas-projects` |
| **Dashboard** | https://vercel.com/joaquim-mulazas-projects/auto-excel |
| **URL de Produção** | https://auto-excel-phi.vercel.app/ |
| **Exemplo de hostname de deployment** | `auto-excel-97cyq4j3i-joaquim-mulazas-projects.vercel.app` |
| **Deployment ID (exemplo observado)** | `dpl_4Y4nECEjFqhLobTQhgPw5whQH7rG` |
| **Último commit observado no deploy** | `acb37e1` |
| **Root Directory** | `frontend/` (relativo ao repo `joaquimmulaza/auto-excel`) |
| **Framework** | Next.js |

> **Nota histórica:** o projecto Vercel antigo chamava-se `frontend` (URLs/aliases `frontend-*.vercel.app` e IDs `dpl_C9RH…` documentados em notas anteriores). O nome correcto actual é **`auto-excel`**, não `frontend`.

---

## 3. Configuração do Projecto Vercel
- **Projecto:** `joaquim-mulazas-projects/auto-excel`
- **Framework:** Next.js
- **Root Directory:** `frontend/`
- **GitHub:** `https://github.com/joaquimmulaza/auto-excel`
- **Produção:** https://auto-excel-phi.vercel.app/

Não inventar `prj_*` IDs em docs enquanto o MCP/API não os devolver com OAuth correcto (ver secção 8).

---

## 4. Pré-Deploy Checklist
- ✅ `.env`, `.env.local` no `.gitignore`
- ✅ Branch de produção alinhada com GitHub (`main` / commit observado no deploy)
- ✅ Build Next.js no root `frontend/`
- ⚠️ Env vars de API/Supabase no dashboard: validar via UI Vercel ou MCP **depois** de autorizar o projecto `auto-excel` (MCP actual pode devolver 403)

---

## 5. Rotas Esperadas na Produção
```
Route (app)
┌ ○ /                      ← Dashboard
├ ○ /_not-found
├ ƒ /jobs/[id]             ← Revisão/Diff/RBAC
└ ○ /jobs/new              ← Upload/Criação
```

Confirmar no browser em https://auto-excel-phi.vercel.app/ (título: Cotarco Commercial Manager).

---

## 6. Gotchas & Notas
- **Nome do projecto:** docs e notebooks antigos referiam `frontend`; o projecto vivo é `auto-excel`.
- **MCP Vercel e scope OAuth:** o servidor MCP Vercel é *project-scoped*. Com a ligação actual, `list_projects` / `get_project` / `filter_project_envs` só veem `boleia`. `web_fetch_vercel_url` em `auto-excel-phi` devolve 403 pedindo reautorização do projecto/team. Re-correr `mcp_auth` **sem** conceder acesso a `auto-excel` **não** adiciona o projecto. O site público continua a carregar sem OAuth.
- **Security Warning Next.js:** manter patch de segurança do Next.js no radar pós-demo.
- **Root Directory:** o `frontend/` está na raiz do monorepo `auto-excel`, não dentro de `cotarco-commercial-manager/`.

---

## 7. Próximos Passos
1. Reautorizar Cursor Vercel MCP para o projecto `auto-excel` (ou todos os projectos) — ver secção 8.
2. Após OAuth correcto: listar env vars via MCP e completar `NEXT_PUBLIC_API_URL` / backend rewrite conforme necessário.
3. Actualizar `next` para versão patched (segurança).
4. Domínio personalizado opcional; Deployment Protection se a demo deixar de ser pública.

---

## 8. Acesso de agentes via Vercel MCP (obrigatório para este projecto)

OAuth do **Cursor Vercel MCP** é limitado aos projectos que o utilizador autoriza na ligação. Por isso o agente pode “não ver” `auto-excel` mesmo com o site em produção.

### Porque o agente não listava `auto-excel`
1. MCP autenticado no team `joaquim-mulazas-projects`, mas scope de projectos só inclui o que foi concedido (ex.: apenas `boleia`).
2. `list_projects` / `get_project` / `filter_project_envs` não devolvem `auto-excel`.
3. `web_fetch_vercel_url` no hostname de produção/deployment devolve **403** com mensagem para actualizar a ligação Vercel e autorizar o projecto/team do deployment.
4. Repetir `mcp_auth` sem escolher `auto-excel` (ou “all projects”) **não** resolve.

### Passos para o utilizador autorizar `auto-excel`
1. Em Cursor: abrir as definições / ligações MCP e localizar **Vercel**.
2. Desligar ou **Re-authorize / Update connection** do servidor Vercel MCP.
3. No ecrã OAuth da Vercel, conceder acesso ao projecto **`auto-excel`** (team `joaquim-mulazas-projects`), ou a **todos os projectos** desse team.
4. Confirmar que a ligação não fica limitada só a `boleia`.
5. Pedir ao agente para voltar a correr `list_projects` / `get_project` — deve aparecer `auto-excel`; `web_fetch_vercel_url` em https://auto-excel-phi.vercel.app/ deve deixar de falhar por scope.

Até isso, agentes devem tratar o projecto como **existente e público** (dashboard + URL acima) e **não** concluir que o projecto está ausente só porque o MCP não o lista.
