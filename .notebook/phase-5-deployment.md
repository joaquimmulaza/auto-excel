# Fase 5 — Deploy Cloud (Vercel Production)

## 1. Visão Geral
Deploy de produção do frontend **Cotarco Commercial Manager** na Vercel, realizado em 28/09/2026 para demonstração executiva à Direção Comercial.

---

## 2. Estado Final
| Item | Valor |
|------|-------|
| **Status** | ✅ SUCCESS (`readyState: READY`) |
| **URL de Produção** | `https://frontend-bzba39y6y-joaquim-mulazas-projects.vercel.app` |
| **Alias Alternativo** | `https://frontend-five-beta-69lrg2w7f9.vercel.app` |
| **Deployment ID** | `dpl_C9RHFbtTrT8pjAvFwHizPVM769GG` |
| **Inspect URL** | `https://vercel.com/joaquim-mulazas-projects/frontend/C9RHFbtTrT8pjAvFwHizPVM769GG` |
| **HTTP Status** | 200 OK (341 KB HTML) |
| **Região de Build** | Washington D.C. (iad1) |
| **Build Machine** | 2 cores, 8 GB RAM |

---

## 3. Configuração do Projecto Vercel
- **Projecto:** `joaquim-mulazas-projects/frontend`
- **Framework:** Next.js (auto-detectado)
- **Build Command:** `next build` (padrão Next.js)
- **Output Directory:** `.next` (Next.js default)
- **Root Directory:** `frontend/` (relativo ao repo `joaquimmulaza/auto-excel`)
- **GitHub:** Conectado a `https://github.com/joaquimmulaza/auto-excel`

---

## 4. Pré-Deploy Checklist
- ✅ `git status` limpo — working tree sem ficheiros não comitados
- ✅ `.env`, `.env.local` no `.gitignore` (confirmado)
- ✅ Branch `main` sincronizada com `origin/main`
- ✅ `npm run build` local compilado com 0 erros antes do deploy
- ✅ `tsc --noEmit` exit code 0

---

## 5. Rotas Disponíveis na Produção
```
Route (app)                Size     First Load JS
┌ ○ /                      4.7 kB   119 kB    ← Dashboard
├ ○ /_not-found            873 B    88.1 kB
├ ƒ /jobs/[id]             9.48 kB  124 kB    ← Revisão/Diff/RBAC
└ ○ /jobs/new              4.39 kB  119 kB    ← Upload/Criação
+ First Load JS shared     87.2 kB
```

---

## 6. Gotchas & Notas
- **Vercel CLI desatualizado:** CLI 37.14.0 falhou com "endpoint requires version 47.2.2+". Actualização para 60.1.3 resolveu.
- **MCP Vercel:** Token não configurado no servidor MCP (`Unauthorized`). Deploy feito via CLI directamente.
- **Security Warning Next.js 14.2.15:** Vulnerabilidade de segurança confirmada pelo npm. **Ação pendente:** Actualizar para a versão mais recente do Next.js após a demonstração executiva.
- **Root Directory:** O `frontend/` está na raiz do monorepo `auto-excel`, não dentro de `cotarco-commercial-manager/`. A Vercel detectou correctamente o root.

---

## 7. Próximos Passos
1. Actualizar `next` para versão patched (segurança).
2. Configurar domínio personalizado `cotarco-commercial-manager.vercel.app` ou similar.
3. Adicionar variáveis de ambiente da API (`NEXT_PUBLIC_API_URL`) no dashboard Vercel.
4. Configurar Deployment Protection para acesso restrito.
