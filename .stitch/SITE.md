---
stitch-project-id: REPLACE_ME
---

# Cotarco Commercial Manager — Stitch Site Constitution

> **AGENT INSTRUCTION:** Read before every Stitch iteration. Update sitemap when a screen is approved and staged under `.stitch/designs/`. Frontend code is **not** written by `stitch-loop` — that is `prompts/agents/04-frontend.md` after QA.

## 1. Core Identity

| Field | Value |
|---|---|
| Product | Cotarco Commercial Manager |
| Stitch Project ID | `REPLACE_ME` (set after `create_project` / known CCM project; also persist in `.stitch/metadata.json`) |
| Mission | Internal platform for upload → validate → review/diff → approve → process commercial tables |
| Audience | Comercial, Operador, Admin |
| Voice | Clear, operational, precise, Portuguese (Angola) UI copy |

## 2. Visual language

Follow `.stitch/DESIGN.md`. Brand: `#FF3C1D`, `#6B6363`, `#FFFFFF`, `#000000`.

## 3. Architecture & asset flow

| Path | Role |
|---|---|
| `.stitch/DESIGN.md` | Design system source of truth |
| `.stitch/next-prompt.md` | Baton for `stitch-loop` |
| `.stitch/designs/` | Staged HTML + PNG from Stitch |
| `.stitch/metadata.json` | projectId + screen ids |
| `cotarco-commercial-manager/prompts/stitch/` | Human/agent prompt sources |
| `frontend/` | Production Next.js — **after** visual QA only |

## 4. Live Sitemap (Stitch screens)

Mark `[x]` when HTML/PNG exist under `.stitch/designs/` and visual QA passed.

- [ ] `design-system` — Foundation tokens & component gallery (`prompts/stitch/00-design-system.md`)
- [ ] `dashboard` — Comercial / Operador home (`prompts/stitch/01-dashboard.md`)
- [ ] `new-job` — Upload / validate stepper (`prompts/stitch/02-new-job.md`)
- [ ] `review-diff` — Review / diff / approve (`prompts/stitch/03-review-diff.md`)

## 5. Roadmap (Backlog)

### High priority

- [ ] Design system screen
- [ ] Dashboard
- [ ] New job / upload
- [ ] Review / diff

### Later

- [ ] History / download detail
- [ ] Auth / profile shell (if not covered by dashboard)

## 6. Creative Freedom

Only invent extra screens if High Priority is done and product docs require them. Stay on-brand; no marketing landing pages.
