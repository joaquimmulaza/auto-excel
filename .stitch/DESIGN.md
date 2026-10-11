# Design System: Cotarco Commercial Manager

> Source of truth for Stitch prompts. Cotarco brand tokens override generic taste-design bans.
> Generate/refine with skills `taste-design` or `design-md`. Used by `enhance-prompt` and `stitch-loop`.

## 1. Identity

| Field | Value |
|---|---|
| Product | Cotarco Commercial Manager (CCM) |
| Platform | Web, Desktop-first (1440px), mobile-usable at 390px for priority screens |
| Users | Comercial, Operador, Admin |
| Mission | Internal tool for validating and processing commercial price/stock tables |

## 2. Atmosphere

- **Vibe:** Enterprise operational clarity — dense but legible, trustworthy, low-noise
- **Density:** Cockpit-leaning (tables, jobs, diffs) without visual clutter
- **Motion:** Restrained CSS micro-interactions only; respect `prefers-reduced-motion`
- **Anti-slop:** No purple neon gradients, no decorative glow CTAs, no emoji UI, no marketing card stacks in the hero

## 3. Color palette (semantic)

| Role | Name | Hex |
|---|---|---|
| Brand / Primary action | Cotarco Red | `#FF3C1D` |
| Secondary / muted chrome | Warm Slate | `#6B6363` |
| Surface / cards | Pure Surface | `#FFFFFF` |
| Ink / primary text | Ink Black | `#000000` |
| Canvas | Soft Neutral | `#F7F7F7` |
| Border | Hairline Gray | `#E5E5E5` |
| Success | Forest | `#15803D` |
| Warning | Amber | `#B45309` |
| Error | Crimson | `#B91C1C` |
| Info | Steel | `#1D4ED8` |

## 4. Typography

- **UI sans:** Distinctive modern sans (prefer Geist / Outfit / Plus Jakarta Sans — avoid Inter for display)
- **Data / prices / SKUs:** Tabular nums, monospace for dense numeric columns (`Geist Mono` or `JetBrains Mono`)
- Headings: `text-balance`; body: `text-pretty`
- Max body measure ~65ch on prose; tables use full width with sticky headers when needed

## 5. Geometry, elevation, components

- Corner radius: 8px controls, 12px panels
- Elevation: single soft shadow or 1px borders — no multi-layer glow
- Buttons: primary solid `#FF3C1D` on white text; secondary outlined `#6B6363`
- Tables: compact rows, `tabular-nums`, clear status badges (color **and** text)
- Forms: inline errors next to fields; destructive actions use confirm dialogs
- Loading: structural skeletons on first paint; short spinners only for local actions
- Touch targets ≥ 44×44px; visible `:focus-visible`

## 6. Design System Notes for Stitch Generation

Copy this block into every Stitch prompt / `.stitch/next-prompt.md`:

```markdown
**DESIGN SYSTEM (REQUIRED):**
- Platform: Web, Desktop-first (1440px), enterprise internal tool
- Vibe: Operational clarity, data-dense, low-noise, trustworthy
- Palette: Brand Cotarco Red (#FF3C1D) for primary actions; Secondary Warm Slate (#6B6363); Surface (#FFFFFF); Ink (#000000); Canvas (#F7F7F7); Border (#E5E5E5)
- Semantic: Success (#15803D), Warning (#B45309), Error (#B91C1C), Info (#1D4ED8)
- Typography: Modern sans for UI; monospace/tabular-nums for prices, SKUs, quantities
- Geometry: 8px control radius, 12px panel radius; hairline borders; soft single-layer shadows only
- Components: Dense data tables, status badges with text+color, dropzone upload, stepper/forms, confirm dialogs for destructive actions
- States: loading skeletons, empty with one clear CTA, inline errors
- Anti-patterns: no purple neon, no glow CTAs, no emoji, no marketing hero collage
```
