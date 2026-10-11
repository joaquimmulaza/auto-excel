# `.stitch/` — Cotarco Stitch workspace

Scaffolding for Google Stitch skills in this repo.

| File | Purpose |
|---|---|
| `DESIGN.md` | Semantic design system (Section 6 = Stitch prompt block) |
| `SITE.md` | Vision, Stitch project ID, sitemap, roadmap |
| `next-prompt.md` | Baton for `stitch-loop` |
| `metadata.json` | Persisted `projectId` + screen map (create on first Stitch run) |
| `designs/` | Staged HTML/PNG from Stitch |

## Pipeline (agents)

See `cotarco-commercial-manager/agents.md` §5.2 and skills:

- `taste-design` / `design-md` → `DESIGN.md`
- UI Skills MCP → `enhance-prompt` → Stitch MCP (`stitch-design`)
- Multi-screen → `stitch-loop`
- After QA → `prompts/agents/04-frontend.md`

## Docs

- https://stitch.withgoogle.com/docs/skills/get-started/
- https://stitch.withgoogle.com/docs/skills/roundtrip/
- https://stitch.withgoogle.com/docs/skills/build-in-a-loop/
- https://stitch.withgoogle.com/docs/skills/taste/
- https://stitch.withgoogle.com/docs/design-md/overview/
