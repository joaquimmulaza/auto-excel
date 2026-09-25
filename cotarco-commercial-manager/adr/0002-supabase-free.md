# ADR-0002 — Supabase no MVP

## Status

Accepted for MVP.

## Decisão

Usar Supabase como plataforma de dados/autenticação/storage durante MVP.

## Motivos

- PostgreSQL gerido;
- Auth;
- Storage;
- API e tooling;
- baixo custo inicial.

## Limitações reconhecidas

O plano Free atual possui quotas e políticas de pausa. Não assumir que é adequado para produção crítica sem estratégia de backups e retenção.

## Mitigação

- ficheiros importantes versionados;
- backups/exports definidos antes de produção;
- migrations versionadas no Git;
- monitorização de utilização;
- plano de upgrade documentado.
