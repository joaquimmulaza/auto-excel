# Source

Official skill from [supabase/agent-skills](https://github.com/supabase/agent-skills) (`skills/supabase-postgres-best-practices`).

- Upstream commit: `c9be0e931b7930f7d02126d04774d904c381e7d7`
- Skill version: `1.1.1`
- Docs: https://supabase.com/docs/guides/getting-started/ai-skills

Installed into this repo because `npx skills add supabase/agent-skills` failed on the Cloud Agent Node (`Class extends value undefined is not a constructor or null`, Node v22.14.0). Equivalent to project-scoped install.

To refresh when the CLI works:

```bash
npx skills add supabase/agent-skills --skill supabase-postgres-best-practices
```

Or re-copy from a fresh clone of `supabase/agent-skills`.
