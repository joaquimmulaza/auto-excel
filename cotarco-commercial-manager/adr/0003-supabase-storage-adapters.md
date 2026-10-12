# ADR 0003 — Supabase Storage adapters (vs disco local efémero)

## Status

Aceite (2026-10-11)

## Contexto

Em ambientes serverless (ex.: Vercel), o disco local (`/tmp`) é efémero. O adapter
anterior gravava em `COTARCO_STORAGE_DIR` (default `/tmp/cotarco-storage`), o que
causava `FILE_MISSING_ON_DISK` no download após cold start / nova sessão.

## Decisão

- Interface estável: `store_bytes` / `read_bytes` (consumida por `files.py` e `job_pipeline`).
- `LocalStorageAdapter` para dev/test (`STORAGE_BACKEND=local`).
- `SupabaseStorageAdapter` para produção (`APP_ENV=production` ou `STORAGE_BACKEND=supabase`).
- Caminho lógico: `jobs/{job_id}/{inputs|outputs|logs|reports}/{hash}_{name}`.
- Bucket privado `job-files`; `SUPABASE_SERVICE_ROLE_KEY` apenas no backend.
- URLs assinadas via `get_download_url` quando o cliente precisar de download directo.

## Consequências

- Metadados continuam na base; binários no Storage.
- Testes cobrem adapter local, mock Supabase e regressão de “nova sessão”.
- Não implica migração para Render; não altera regras de preço/stock.
