---
trigger: always_on
description: Mandatory Supabase + Postgres best-practices skills before DB/Auth/Storage/API work.
---

# Supabase Skills Workflow Rules

Official skills from [supabase/agent-skills](https://github.com/supabase/agent-skills) live in `.agents/skills/`:

- `supabase`
- `supabase-postgres-best-practices`

Docs: https://supabase.com/docs/guides/getting-started/ai-skills

## When mandatory

Any task that touches:

- schema, migrations, indexes, constraints
- RLS / policies / GRANT
- Auth, sessions, JWT, SSR clients
- Storage buckets / policies
- Supabase-backed API routes or repositories
- Postgres performance / pooling / locking

Phases `02-database` and `03-api` always load both skills (`agents.md` §5.3 + §11).

## Protocol

```text
Read supabase/SKILL.md
  → Read supabase-postgres-best-practices/SKILL.md
  → Load relevant references/
  → Implement with TDD
  → Verify (test query / pytest)
  → SUPABASE_SKILLS_USED in handoff
```

## Hard stops

- No `service_role` in frontend or committed secrets
- No skipping RLS on exposed schemas
- No using `user_metadata` for authorization decisions
- No marking DB work done without test evidence
