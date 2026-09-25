# Rules Auditor — Audit Report
**Project:** Cotarco Commercial Manager  
**Audit Target:** `.agents/rules/` (11 files)  
**Auditor:** Rules Auditor Subagent  
**Date:** 2026-09-25  
**Mode:** READ-ONLY — no existing files modified

---

## Executive Summary

The `.agents/rules/` directory contains **11 rule files** governing agent behaviour for the Cotarco Commercial Manager project. The audit uncovered **18 distinct findings** across five risk categories.

The most critical systemic problem is a **dead glob path** (`cotarco-client//`) appearing in four separate rule files. The frontend application directory does not exist under that name — meaning all four glob-triggered rules **never activate** for any real file. This silently neutralises a substantial portion of the rule system.

A secondary cluster of problems involves **three competing and partially contradictory Git/commit workflow rules** that define different allowed commit types, different formatting requirements, different message length constraints, and different approval semantics. An agent receiving all three simultaneously cannot deterministically satisfy all of them.

A third cluster involves **legacy and generic patterns** clearly inherited from previous projects or from generic AI-assistant rule templates (the `auto-excel` monorepo era, mobile-first UX rules, Redux/Zustand state management rules) that contradict the documented target stack and product decisions in `context.md` and `agents.md`.

Finally, the `context-guard.md` rule, though well-intentioned, is **dangerously underspecified** — it mandates reading two files but provides zero enforcement criteria, no failure behaviour, and omits several other mandatory documents called out in `agents.md §0`.

**Overall risk posture: HIGH** — the combination of dead globs, commit rule conflicts, and legacy contradictions means agents are operating on a partially broken rule surface.

---

## Files Audited

| # | File | Size | Last Modified | Trigger Type |
|---|------|------|--------------|-------------|
| 1 | `codeNavi.md` | 1,449 B | 2026-05-11 | `always_on` |
| 2 | `context-guard.md` | 135 B | 2026-09-25 | `always_on` |
| 3 | `cotarco-git-workflow.md` | 370 B | 2026-05-11 | `model_decision` |
| 4 | `frontend-architecture.md` | 5,153 B | 2026-05-11 | `glob: cotarco-client//*.{js,jsx,ts,tsx}` |
| 5 | `frontend.md` | 3,343 B | 2026-05-11 | `glob: cotarco-client//*.{js,jsx,ts,tsx}` |
| 6 | `git-commit-rules.md` | 898 B | 2026-05-11 | `model_decision` |
| 7 | `graphify.md` | 947 B | 2026-09-25 | `always_on` |
| 8 | `nextjs.md` | 2,406 B | 2026-09-25 | `glob: cotarco-client//*.{js,jsx,ts,tsx}` |
| 9 | `ui-skills.md` | 3,276 B | 2026-09-25 | `always_on` |
| 10 | `ui-ux.md` | 5,189 B | 2026-05-11 | `glob: cotarco-client//*` |
| 11 | `workspace.md` | 1,410 B | 2026-05-11 | `always_on` |

**Also verified:** Workspace root structure, presence/absence of referenced directories.

---

## Detailed Findings

---

### CATEGORY A — Dead / Incorrect Glob Paths

---

#### FIND-001
| Field | Detail |
|-------|--------|
| **ID** | FIND-001 |
| **File & Line** | `frontend-architecture.md` — Line 3 |
| **Issue** | Glob `cotarco-client//*.{js,jsx,ts,tsx}` references a directory that does not exist in the workspace root. The actual workspace root contains no `cotarco-client/` directory. The only relevant directory currently is the planning/documentation folder `cotarco-commercial-manager/`. |
| **Impact** | **This rule never activates.** All 138 lines of frontend architecture guidance (Server Components First, TypeScript patterns, Shadcn/UI, Zod, TanStack Query) are completely invisible to agents working on any frontend file. |
| **Proposed Remediation** | Update glob to match the real frontend directory once it is created (e.g., `apps/web/**/*.{ts,tsx}` or `frontend/**/*.{ts,tsx}` per the agreed project layout). Until the directory exists, use `always_on` with a conditional check, or declare the expected path explicitly in `context.md`. |
| **Risk Level** | 🔴 CRITICAL |

---

#### FIND-002
| Field | Detail |
|-------|--------|
| **ID** | FIND-002 |
| **File & Line** | `frontend.md` — Line 3 |
| **Issue** | Same dead glob: `cotarco-client//*.{js,jsx,ts,tsx}`. |
| **Impact** | The entire "Senior Frontend Developer" persona, coding guidelines, and commit instructions in `frontend.md` never activate. Agents have no automatic guidance for JSX/TSX work. |
| **Proposed Remediation** | Same as FIND-001. Additionally, consider merging `frontend.md` and `frontend-architecture.md` — they heavily overlap. |
| **Risk Level** | 🔴 CRITICAL |

---

#### FIND-003
| Field | Detail |
|-------|--------|
| **ID** | FIND-003 |
| **File & Line** | `nextjs.md` — Line 3 |
| **Issue** | Same dead glob: `cotarco-client//*.{js,jsx,ts,tsx}`. |
| **Impact** | Next.js-specific guidance (App Router patterns, Server Actions, security review protocol) never activates for any file. |
| **Proposed Remediation** | Same as FIND-001. |
| **Risk Level** | 🔴 CRITICAL |

---

#### FIND-004
| Field | Detail |
|-------|--------|
| **ID** | FIND-004 |
| **File & Line** | `ui-ux.md` — Line 3 |
| **Issue** | Glob `cotarco-client//*` — uses double-slash `//` which is a non-standard glob pattern. On most systems this is equivalent to `cotarco-client/*` but the non-standard syntax may fail in certain glob engines. More importantly, `cotarco-client/` does not exist. |
| **Impact** | All 122 lines of UI/UX guidance never activate. The `//` double-slash also creates a potential portability issue if the glob engine is strict. |
| **Proposed Remediation** | Fix the path to match the real frontend directory and use standard glob syntax (`/**/*` or `/**/*.{ts,tsx,css}`). |
| **Risk Level** | 🔴 CRITICAL |

---

### CATEGORY B — Git / Commit Workflow Conflicts

---

#### FIND-005
| Field | Detail |
|-------|--------|
| **ID** | FIND-005 |
| **File & Line** | `cotarco-git-workflow.md` — Line 8 vs. `git-commit-rules.md` — Line 7 vs. `frontend.md` — Lines 43-45 vs. `agents.md` — Lines 114-120 |
| **Issue** | **Four different definitions of allowed commit type prefixes across four sources:** — `cotarco-git-workflow.md`: `feat, fix, ui, refactor, test, chore` (includes `ui`, excludes `docs`, `security`, `perf`, `style`) — `git-commit-rules.md`: only `feat`, `fix`, `refactor` — `frontend.md`: `fix, feat, chore, docs, style, refactor, perf, test` (broadest set, closest to full Conventional Commits) — `agents.md §9`: `feat, fix, refactor, test, docs, chore, security` (includes `security`, excludes `ui`, `style`, `perf`) |
| **Impact** | An agent cannot simultaneously satisfy all four rules. A `docs:` commit satisfies `agents.md` and `frontend.md` but violates `git-commit-rules.md` (not in its 3-type list). A `ui:` commit satisfies `cotarco-git-workflow.md` but violates all three others. A `security:` commit satisfies `agents.md` but violates `cotarco-git-workflow.md`. This ambiguity will cause inconsistent commit histories and potential CI/linting failures if conventional-commit enforcement is added. |
| **Proposed Remediation** | Establish a single canonical commit type list in one authoritative file (recommend `cotarco-git-workflow.md`). Update `agents.md` and remove the commit section from `frontend.md` and `git-commit-rules.md`, or make them explicitly defer to the canonical source. The recommended canonical set: `feat, fix, refactor, test, docs, chore, security` (aligned with `agents.md`, which is the project's primary agent governance document). Remove the non-standard `ui` type. |
| **Risk Level** | 🔴 HIGH |

---

#### FIND-006
| Field | Detail |
|-------|--------|
| **ID** | FIND-006 |
| **File & Line** | `cotarco-git-workflow.md` — Line 10 vs. `workspace.md` — Line 25 vs. `agents.md` — Line 122 |
| **Issue** | **Conflicting commit granularity requirements.** `cotarco-git-workflow.md` line 10 specifies `git add .` (adds ALL changed files in one shot). `workspace.md` §6 requires "atomic commits representing a single logical change." `agents.md` §9 says "Evitar commits gigantes" (avoid giant commits). `git add .` is structurally incompatible with atomic/single-logical-change commits when multiple features are in progress. |
| **Impact** | An agent following `cotarco-git-workflow.md` literally will stage all modified files indiscriminately, creating non-atomic commits that violate the spirit of `workspace.md` and `agents.md`. This makes `git bisect` and PR reviews harder. |
| **Proposed Remediation** | Replace `git add .` in `cotarco-git-workflow.md` with `git add <specific-files>` or `git add -p`. Add explicit guidance that staging must be scoped to the logical unit of change. |
| **Risk Level** | 🟠 MEDIUM |

---

#### FIND-007
| Field | Detail |
|-------|--------|
| **ID** | FIND-007 |
| **File & Line** | `git-commit-rules.md` — Lines 6-7 vs. `cotarco-git-workflow.md` — Line 6 |
| **Issue** | **Conflicting commit message format requirements.** `git-commit-rules.md` requires: short description < 50 chars + newline + detailed description, written in markdown, informal tone, no specific file names, no phrases like "this commit". `cotarco-git-workflow.md` requires: `[Type]: Description` (using square brackets, not `type:` colon format). The bracket format `[Type]` is **not** Conventional Commits; it is a different, legacy syntax. `agents.md` and `frontend.md` both use the standard `type:` colon format. |
| **Impact** | Agents will produce commit messages in incompatible formats depending on which rule wins. If a commitlint or conventional-commits CI check is added later, the `[Type]` bracket format will fail validation. |
| **Proposed Remediation** | Standardise on `type: description` format (no square brackets) across all files. Update `cotarco-git-workflow.md` line 6. |
| **Risk Level** | 🟠 MEDIUM |

---

#### FIND-008
| Field | Detail |
|-------|--------|
| **ID** | FIND-008 |
| **File & Line** | `cotarco-git-workflow.md` — Line 10 |
| **Issue** | The workflow rule includes `git push` as a mandatory, autonomous step in the commit flow. There is no human approval gate between commit and push. |
| **Impact** | This directly conflicts with `context.md §5 Rule 7`: "Nenhuma alteração externa deve ocorrer sem aprovação explícita quando a operação for classificada como crítica." While a git push is not an "external system operation" in the financial sense, pushing code autonomously to a shared branch bypasses any PR/review process. Combined with `workspace.md §5` ("wait for developer confirmation before executing"), autonomous push is a policy violation. |
| **Proposed Remediation** | Remove `git push` from the automatic flow. Replace with: "After commit, present a summary and await explicit human approval before pushing." This aligns with `workspace.md §5` and the general approval-gate philosophy. |
| **Risk Level** | 🟠 MEDIUM |

---

### CATEGORY C — Autonomy vs. Human Approval Gate Conflicts

---

#### FIND-009
| Field | Detail |
|-------|--------|
| **ID** | FIND-009 |
| **File & Line** | `cotarco-git-workflow.md` — Line 10 (autonomous push) vs. `workspace.md` — Line 22 (explicit plan + confirmation) vs. `context.md` — Line 128 (no critical ops without explicit approval) |
| **Issue** | `cotarco-git-workflow.md` grants the agent full autonomy to push after a commit (triggered by `model_decision`). `workspace.md` §5 requires explicit planning and developer confirmation for any non-trivial task before execution. These two rules contradict each other when the "task" involves a push. |
| **Impact** | An agent following `cotarco-git-workflow.md` will push autonomously. An agent following `workspace.md` will pause and ask. With both active simultaneously, outcome is non-deterministic. |
| **Proposed Remediation** | See FIND-008. Additionally, clarify in `cotarco-git-workflow.md` that `model_decision` trigger means the agent decides the commit message format, not that it has authority to push unilaterally. |
| **Risk Level** | 🟠 MEDIUM |

---

#### FIND-010
| Field | Detail |
|-------|--------|
| **ID** | FIND-010 |
| **File & Line** | `codeNavi.md` — Lines 20-21 vs. `workspace.md` — Lines 21-22 |
| **Issue** | Both rules define a planning/confirmation gate but with different framing. `codeNavi.md` says "Present a plan before executing. Each step must have a verification criterion." `workspace.md` §5 says "always outline a step-by-step execution plan and wait for the developer's confirmation." `codeNavi.md` does not explicitly say to *wait for confirmation* — it says to present a plan and then Execute. This is a subtle but real difference: one requires human confirmation, the other is self-authorising if the plan is presented. |
| **Impact** | Low in isolation, medium when combined with autonomous push (FIND-008/009). An agent might reason: "I presented my plan (satisfying codeNavi), so I can proceed" without waiting for human sign-off (violating workspace.md). |
| **Proposed Remediation** | Add "and await human confirmation" to `codeNavi.md` Execute phase. |
| **Risk Level** | 🟡 LOW-MEDIUM |

---

### CATEGORY D — Stack Incompatibilities and Contradictions

---

#### FIND-011
| Field | Detail |
|-------|--------|
| **ID** | FIND-011 |
| **File & Line** | `frontend-architecture.md` — Lines 126-127 |
| **Issue** | **Legacy state management recommendations not aligned with project stack.** The file recommends "Redux Toolkit for complex applications" and "Zustand for simpler state management" as global state options. Neither Redux Toolkit nor Zustand is in the stack defined in `context.md §7`. The authorised stack specifies TanStack Query for server state and React Hook Form + Zod for form state. No global client-side state manager is sanctioned. |
| **Impact** | An agent following `frontend-architecture.md` might introduce Redux or Zustand as a dependency, adding unjustified complexity and creating a dependency not in the approved stack. This directly contradicts the `agents.md §3` principle "Domínio independente de FastAPI/Next.js" and the general "avoid unnecessary complexity" philosophy. |
| **Proposed Remediation** | Replace Redux Toolkit/Zustand mention with: "For server state: TanStack Query. For form state: React Hook Form + Zod. For complex local component state: useReducer. Avoid introducing global state libraries without explicit architectural decision." |
| **Risk Level** | 🟠 MEDIUM |

---

#### FIND-012
| Field | Detail |
|-------|--------|
| **ID** | FIND-012 |
| **File & Line** | `ui-ux.md` — Lines 47-52 (Mobile-First Design section) vs. `context.md` — Lines 214-216 |
| **Issue** | **Mobile-first vs. desktop-first contradiction.** `ui-ux.md` explicitly mandates mobile-first design: "Design for mobile devices first, then scale up." `context.md §8` explicitly mandates the opposite: "responsiva, mas **desktop-first** para utilização interna." This is a direct contradiction. |
| **Impact** | Agents following `ui-ux.md` will build mobile-first layouts. The product is an internal enterprise tool designed desktop-first. Mobile-first CSS cascade ordering, breakpoint strategy, and component prioritization decisions will all be inverted from what the product requires. |
| **Proposed Remediation** | Update `ui-ux.md` Mobile-First Design section to reflect: "This is a desktop-first application. Design for 1440px desktop first, then ensure 390px mobile does not break critical flows. Use Tailwind's responsive modifiers (md:, lg:) in the desktop-down direction." |
| **Risk Level** | 🔴 HIGH |

---

#### FIND-013
| Field | Detail |
|-------|--------|
| **ID** | FIND-013 |
| **File & Line** | `frontend.md` — Line 35 |
| **Issue** | **Svelte/non-React syntax leakage.** The rule states: "Use 'class:' instead of the tertiary operator in class tags whenever possible." The `class:` directive is a **Svelte** syntax construct. It does not exist in React or Next.js. In React/JSX, conditional classes are handled via template literals, `clsx`, or `cn()` utilities. |
| **Impact** | An agent following this rule literally will write Svelte-style `class:active={isActive}` syntax inside JSX files, causing TypeScript/JSX compilation errors. This is a clear legacy/cross-project contamination. |
| **Proposed Remediation** | Replace with: "Use `cn()` (from `shadcn/ui` / `clsx` + `tailwind-merge`) for conditional class composition instead of inline ternary strings." |
| **Risk Level** | 🔴 HIGH |

---

#### FIND-014
| Field | Detail |
|-------|--------|
| **ID** | FIND-014 |
| **File & Line** | `frontend.md` — Line 38 |
| **Issue** | **Contradictory component declaration style.** `frontend.md` line 38 says: "Use consts instead of functions, for example, 'const toggle = () =>'." `frontend-architecture.md` line 60 says: "Use the `function` keyword for component definitions, not arrow functions." These are directly opposite instructions for the same scenario. |
| **Impact** | Non-deterministic agent behaviour: agents may use either arrow functions or function declarations for components, resulting in an inconsistent codebase. The `function` keyword approach in `frontend-architecture.md` is generally preferred for React components (better stack traces, hoisting) and aligns with modern community standards. |
| **Proposed Remediation** | Resolve the conflict explicitly. Recommended resolution: use `function` keyword for named React components (per `frontend-architecture.md`), use `const` arrow functions for utility functions, event handlers, and hooks internal to components. Remove the ambiguous statement from `frontend.md`. |
| **Risk Level** | 🟠 MEDIUM |

---

#### FIND-015
| Field | Detail |
|-------|--------|
| **ID** | FIND-015 |
| **File & Line** | `frontend-architecture.md` — Line 93 |
| **Issue** | **Framer Motion not in approved stack.** The file recommends: "Use Framer Motion library for the animations of components." Framer Motion is not listed in `context.md §7` stack, and `context.md §8` explicitly discourages excessive animations ("sem excesso de animações"). |
| **Impact** | Introducing Framer Motion adds a significant bundle-size dependency for an enterprise data-heavy application that intentionally minimises animations. Contradicts product philosophy. |
| **Proposed Remediation** | Replace with: "Use short, interruptible CSS transitions via Tailwind utilities (`transition-*`, `duration-*`). Do not introduce animation libraries. If complex animation is needed, raise as an architectural decision in ADR before implementing." |
| **Risk Level** | 🟡 LOW-MEDIUM |

---

#### FIND-016
| Field | Detail |
|-------|--------|
| **ID** | FIND-016 |
| **File & Line** | `frontend.md` — Line 39 |
| **Issue** | **"Don't use semicolons" in TypeScript context is ambiguous and potentially harmful.** This rule may have been inherited from a JavaScript/ESLint-no-semi configuration in a different project. TypeScript projects typically use semicolons or enforce one style through ESLint/Prettier config. Imposing no-semicolons through a rule file (rather than the formatter) creates conflict: if the project's Prettier config uses semicolons, agents will produce code that Prettier rewrites on every save. |
| **Impact** | Formatting churn, potential lint/prettier conflicts, confusion if the actual `.prettierrc` or ESLint config says otherwise. |
| **Proposed Remediation** | Remove from the rule file. Semicolon style should be governed by the project's `.prettierrc` / `.eslintrc` configuration alone, not by agent rules. Add a note: "Formatting is enforced by Prettier; do not override with manual style preferences." |
| **Risk Level** | 🟡 LOW-MEDIUM |

---

### CATEGORY E — Legacy / Obsolete / Underspecified Patterns

---

#### FIND-017
| Field | Detail |
|-------|--------|
| **ID** | FIND-017 |
| **File & Line** | `context-guard.md` — Lines 5-8 |
| **Issue** | **Dangerously underspecified mandatory context rule.** The rule tells agents to read `context.md` and `agents.md` before acting. However: (1) It does not list all mandatory pre-read files specified in `agents.md §0` (which lists 6 documents including `docs/requirements.md`, `docs/stack-and-guardrails.md`, `docs/testing-tdd.md`). (2) It provides no enforcement gate — there is no "if you haven't read these, stop" consequence. (3) It uses relative paths with no anchor, making it ambiguous for agents that may resolve paths differently. |
| **Impact** | Agents may consider reading just the two listed files sufficient, skipping the other 4 mandatory documents in `agents.md §0`. This defeats the purpose of the guard. |
| **Proposed Remediation** | Expand `context-guard.md` to list all 6 mandatory pre-read files from `agents.md §0`. Add explicit paths relative to the workspace root. Add an enforcement statement: "Do not write or modify any code until all of the above have been confirmed read in the current session." |
| **Risk Level** | 🟠 MEDIUM |

---

#### FIND-018
| Field | Detail |
|-------|--------|
| **ID** | FIND-018 |
| **File & Line** | `graphify.md` — Lines 8-14 (always_on) |
| **Issue** | **Graphify rule is `always_on` but references conditionally existing assets.** The rule says "when `graphify-out/graph.json` exists, first run `graphify query`". `graphify-out/` exists and `graph.json` is present, but `graphify-out/wiki/` does **not** exist. The rule instructs: "If graphify-out/wiki/index.md exists, navigate it instead of reading raw files" — this is currently a dead branch but not a critical failure. More importantly, the `always_on` trigger means every agent, for every task (including simple documentation edits), must first query the graph. This adds unnecessary overhead for non-code tasks. |
| **Impact** | Minor overhead for always_on tasks; potential confusion when `graphify query` CLI is not available in the agent's environment. The missing wiki directory is a documentation gap, not a breaking issue. |
| **Proposed Remediation** | Change trigger from `always_on` to `glob` matching code file extensions, so it activates only for code-related tasks. Document that `graphify-out/wiki/` is not yet generated and remove or conditionalise that instruction. |
| **Risk Level** | 🟡 LOW |

---

## Autonomy vs. Human Approval Conflict Analysis

```
┌─────────────────────────────────┬──────────────────────────┬────────────────────────────────┐
│ Rule                            │ Autonomy Granted         │ Conflicts With                 │
├─────────────────────────────────┼──────────────────────────┼────────────────────────────────┤
│ cotarco-git-workflow.md         │ Auto commit + push       │ workspace.md §5, context.md §7 │
│ codeNavi.md (Plan→Execute)      │ Self-authorising after   │ workspace.md §5 (needs         │
│                                 │ presenting plan          │ confirmation)                  │
│ git-commit-rules.md             │ Model decides commit     │ No push gate specified         │
│                                 │ message format           │                                │
│ workspace.md §5                 │ STOPS — requires human   │ cotarco-git-workflow.md        │
│                                 │ confirmation             │ (auto-push)                    │
│ context.md §5 Rule 7            │ BLOCKS — no critical ops │ cotarco-git-workflow.md        │
│                                 │ without explicit approval│ (auto-push without gate)       │
└─────────────────────────────────┴──────────────────────────┴────────────────────────────────┘
```

**Verdict:** The highest-risk autonomy conflict is the `git push` in `cotarco-git-workflow.md`. It bypasses the human confirmation gate required by `workspace.md §5` and the explicit approval gate required by `context.md`. No other rule file explicitly reinstates a push approval gate. This should be remediated as highest priority in this category.

---

## Git / Commit Workflow Conflict Analysis

Four sources define commit behaviour with the following incompatibilities:

| Dimension | `cotarco-git-workflow.md` | `git-commit-rules.md` | `frontend.md` | `agents.md` |
|-----------|--------------------------|----------------------|---------------|-------------|
| **Format** | `[Type]: Desc` (brackets) | `type: desc` (colon) | `type: desc` | `type: desc` |
| **Allowed types** | feat, fix, ui, refactor, test, chore | feat, fix, refactor ONLY | feat, fix, chore, docs, style, refactor, perf, test | feat, fix, refactor, test, docs, chore, security |
| **Message length** | Not specified | < 50 chars short + detailed body | Not specified | "Evitar commits gigantes" |
| **Language** | English | Not specified | English (imperative) | Not specified |
| **Body required?** | No | Yes (newline + detailed) | Optional body | Not specified |
| **Staging** | `git add .` (all files) | Not specified | Not specified | Avoid giant commits |
| **Push** | Automatic | Not specified | Not specified | Not specified |

**Canonical recommendation:** `agents.md §9` should be the single source of truth for commit conventions, as it is the project's primary agent governance document. All other files should either defer to it or be removed.

---

## Legacy / Obsolete Patterns Summary

| Pattern | Found In | Origin Diagnosis |
|---------|----------|-----------------|
| `cotarco-client/` directory path | `frontend.md`, `frontend-architecture.md`, `nextjs.md`, `ui-ux.md` | Pre-scaffold placeholder or renamed/restructured directory — workspace never had this path |
| `class:` Svelte directive | `frontend.md` L35 | Copied from a Svelte project rule or generic AI template; incompatible with React/JSX |
| Redux Toolkit / Zustand recommendation | `frontend-architecture.md` L126-127 | Generic frontend template not customised to Cotarco's approved stack |
| Framer Motion recommendation | `frontend-architecture.md` L93 | Generic template — contradicts "sem excesso de animações" product principle |
| Mobile-first design mandate | `ui-ux.md` L47-52 | Generic mobile-first template — contradicts explicit desktop-first requirement |
| No-semicolons rule | `frontend.md` L39 | Likely from a JS/Vue/Svelte project; conflicts with TypeScript project's formatter |
| `[Type]` bracket commit format | `cotarco-git-workflow.md` L6 | Legacy commit convention, not Conventional Commits standard |
| `git add .` staging | `cotarco-git-workflow.md` L10 | Convenience shortcut from a single-developer workflow; violates atomic commit principle |
| Only feat/fix/refactor types | `git-commit-rules.md` L7 | Truncated Conventional Commits — incomplete for a full project lifecycle |

---

## Recommendations Priority Matrix

| Priority | Finding IDs | Action |
|----------|-------------|--------|
| **P0 — Immediate** | FIND-001, FIND-002, FIND-003, FIND-004 | Fix all dead glob paths to match actual frontend directory once created; use `always_on` as interim |
| **P0 — Immediate** | FIND-013 | Remove Svelte `class:` syntax from `frontend.md` |
| **P0 — Immediate** | FIND-012 | Fix mobile-first vs desktop-first contradiction |
| **P1 — High** | FIND-005, FIND-007 | Consolidate commit type list and format under `agents.md` as single source of truth |
| **P1 — High** | FIND-008, FIND-009 | Remove autonomous `git push` from `cotarco-git-workflow.md` |
| **P2 — Medium** | FIND-006 | Replace `git add .` with scoped staging instructions |
| **P2 — Medium** | FIND-011 | Remove Redux/Zustand from state management recommendations |
| **P2 — Medium** | FIND-014 | Resolve function vs. arrow function component declaration conflict |
| **P2 — Medium** | FIND-017 | Expand `context-guard.md` to list all 6 mandatory pre-read documents |
| **P3 — Low** | FIND-010 | Add explicit "await human confirmation" to codeNavi Execute phase |
| **P3 — Low** | FIND-015 | Remove Framer Motion recommendation |
| **P3 — Low** | FIND-016 | Remove no-semicolons rule (defer to Prettier config) |
| **P3 — Low** | FIND-018 | Change `graphify.md` trigger from `always_on` to code-file glob |

---

## Conclusion

The rules system is architecturally sound in intent but has accumulated significant technical debt from generic AI templates, cross-project contamination (Svelte syntax, Redux, mobile-first patterns), and an early-phase workspace where the frontend directory has not yet been scaffolded. The dead glob issue alone means that **approximately 16,000 bytes (≈60%) of the rule content is currently inert and never activates**. Resolving the P0 and P1 findings would restore the system to functional coverage and eliminate the most dangerous behavioural contradictions.

---

*Report generated by Rules Auditor Subagent. Read-only audit — no existing files were modified.*
