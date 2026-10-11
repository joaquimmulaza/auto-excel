---
name: stitch-loop
description: Iteratively build Cotarco Commercial Manager screens with Stitch using a baton-passing loop (.stitch/next-prompt.md), adapted from google-labs-code/stitch-skills stitch-loop.
allowed-tools:
  - "stitch*:*"
  - "Read"
  - "Write"
  - "Bash"
---

# Stitch Build Loop — Cotarco Commercial Manager

You are an **autonomous UI builder** for the Cotarco Commercial Manager (CCM) MVP. Each iteration generates one screen with Stitch, stages assets under `.stitch/designs/`, updates `.stitch/SITE.md`, and writes the next baton to `.stitch/next-prompt.md`.

This is **not** a marketing-site loop. Do **not** write into `site/public/`. Frontend implementation happens later via `prompts/agents/04-frontend.md` after visual QA.

## Prerequisites

- Stitch MCP connected
- `.stitch/DESIGN.md` (create with `taste-design` using Cotarco brand, or `design-md` from an existing screen)
- `.stitch/SITE.md` (vision, Stitch project ID, sitemap, roadmap)
- UI Skills MCP selection (`agents.md` §5.1) before each generate
- Repo skill `enhance-prompt` to polish the baton prompt

**Brand override:** Cotarco tokens in `.stitch/DESIGN.md` win over generic `taste-design` bans (including ink `#000000`).

## Baton

`.stitch/next-prompt.md`:

```markdown
---
page: dashboard
deviceType: DESKTOP
---
[Enhanced prompt including DESIGN SYSTEM block from .stitch/DESIGN.md Section 6]
```

- `page` → output basename under `.stitch/designs/{page}.html` / `.png`
- Must include the DESIGN SYSTEM block from `.stitch/DESIGN.md`
- You **MUST** update the baton before finishing an iteration

## Execution protocol

### 1. Read baton + context

Read `.stitch/next-prompt.md`, `.stitch/SITE.md`, `.stitch/DESIGN.md`.

- Do not recreate screens already marked `[x]` in the sitemap.
- Prefer High Priority roadmap items in `SITE.md`.

### 2. Gates before Stitch

1. UI Skills MCP: `list_skills` → choose 2–4 → `get_skill`
2. `enhance-prompt` on the baton body (keep DESIGN SYSTEM + Cotarco tokens)
3. Max **3** Stitch refine cycles per screen (`agents.md` §5)

### 3. Generate with Stitch MCP

1. Resolve `projectId` from `.stitch/metadata.json` or `SITE.md`; create project if missing and persist metadata.
2. `generate_screen_from_text` with `projectId`, enhanced prompt, `deviceType` (default `DESKTOP`).
3. On timeout, poll `list_screens` / `get_screen` (do not blindly retry generate).
4. Download HTML + screenshot to `.stitch/designs/{page}.html` and `.stitch/designs/{page}.png` (append `=w{width}` to screenshot URLs when needed).
5. Update `.stitch/metadata.json` screens map via `get_project`.

### 4. Stage only (no production frontend)

Keep assets in `.stitch/designs/`. Do not copy into `frontend/` until Stitch QA passes and the frontend agent runs.

### 5. Update SITE.md

- Mark the page `[x]` in the sitemap
- Advance/clear the matching roadmap item

### 6. Write next baton (required)

Pick the next pending CCM screen from the roadmap (design-system → dashboard → new-job → review-diff → …). Include full DESIGN SYSTEM block. If roadmap complete, set baton body to `STATUS: LOOP_COMPLETE` and stop.

## Cotarco file layout

```text
.stitch/
├── README.md
├── metadata.json      # projectId + screens map
├── DESIGN.md          # semantic design system
├── SITE.md            # vision, sitemap, roadmap
├── next-prompt.md     # baton
└── designs/           # staged Stitch HTML + PNG
```

## Roundtrip (design → code)

After visual QA approval:

1. Keep Stitch export as reference only
2. Implement in Next.js via `04-frontend` + shadcn/project components
3. Never treat Stitch HTML as final production code

## Pitfalls

- Forgetting to update `next-prompt.md`
- Generating without DESIGN.md / UI Skills selection
- Writing into `frontend/` from this skill
- Ignoring Cotarco brand tokens
- Exceeding 3 refine cycles without human review

## Official references

- https://stitch.withgoogle.com/docs/skills/build-in-a-loop/
- https://stitch.withgoogle.com/docs/skills/roundtrip/
- https://stitch.withgoogle.com/docs/design-md/overview/
- Upstream: https://github.com/google-labs-code/stitch-skills
