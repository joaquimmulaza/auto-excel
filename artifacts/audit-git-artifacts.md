# Git & Artifacts Audit Report
## Cotarco Commercial Manager — Repository: `joaquimmulaza/auto-excel`

**Audit Date:** 2026-09-25  
**Auditor:** Git & Artifacts Auditor (Subagent 2)  
**Repository Root:** `c:\Users\MARKETING DESIGNER01\Downloads\up_prices`  
**Remote:** `https://github.com/joaquimmulaza/auto-excel.git`  
**Branch:** `main` (up to date with origin/main)

---

## 1. Executive Summary

> [!CAUTION]
> The repository is tracking **552 node_modules files** and **85 Graphify-related files** (including 64 binary-equivalent cache files) that have **no business being version-controlled**. This inflates the pack size unnecessarily and introduces severe CI/CD, onboarding, and cross-platform portability problems. Immediate remediation is strongly recommended.

| Category | Severity | Status |
|---|---|---|
| `node_modules` tracked in Git | 🔴 Critical | 552 files tracked |
| Graphify cache files tracked | 🔴 Critical | 64 cache JSON files tracked |
| Graphify generated outputs tracked | 🟡 Medium | `graph.html`, `graph.json`, dated snapshots |
| Graphify internal marker files tracked | 🟡 Medium | `.graphify_*` hidden files |
| `.gitignore` severely incomplete | 🔴 Critical | Only 7 Excel extension patterns; missing ~15 critical categories |
| `.gitattributes` incomplete | 🟡 Medium | Only 1 merge strategy line; missing EOL, binary, and LFS configs |
| Unstaged modification to tracked file | 🟢 Low | `.agents/rules/context-guard.md` has local edits |
| Line-ending inconsistency (LF→CRLF) | 🟡 Medium | Git warning on context-guard.md |
| No `.env` or secrets found tracked | ✅ Pass | No sensitive files found |
| No `.bak`, `.zip`, or `.tmp` files found | ✅ Pass | No extraneous backup files |

**Pack size:** `3.90 MiB` (already bloated from the committed node_modules and Graphify caches).

---

## 2. Current Git Status & Repository Hygiene Overview

### 2.1 Git Status
```
On branch main
Your branch is up to date with 'origin/main'.

Changes not staged for commit:
  modified:   .agents/rules/context-guard.md

Untracked files:
  artifacts/
```

**Key observations:**
- One tracked file has local modifications: `.agents/rules/context-guard.md`
  - Git also emits a **CRLF warning** on this file: `LF will be replaced by CRLF the next time Git touches it`
  - This indicates an EOL inconsistency — the file was committed with LF line endings but the Windows working copy is writing CRLF
- The `artifacts/` directory (where audit reports live) is correctly untracked but is **not in `.gitignore`** — it will appear as untracked noise on every `git status` call

### 2.2 Commit History
```
9955662 update repo
3cdef93 update tables titles
40d34e7 Adiciona .gitignore para ficheiros Excel e atualiza projeto
0045715 first commit
```

- Only **4 commits** total — a very young repository
- Commit `40d34e7` added the `.gitignore` but it was limited to Excel file extensions only
- The `node_modules` and Graphify files were already introduced in earlier commits, before the `.gitignore` was put in place or because the patterns were never added

### 2.3 Total Tracked File Inventory Summary

| Category | File Count |
|---|---|
| `node_modules/**` (all of `.agents/skills/playwright-skill/node_modules/`) | **552** |
| `graphify-out/**` (outputs, caches, markers) | **85** |
| `.agents/**` excluding node_modules (skills, rules, workflows) | **153** |
| `cotarco-commercial-manager/**` (project docs) | ~30 |
| Root-level files (`main.py`, `.gitignore`, etc.) | ~10 |
| **Total tracked** | **~821** |

---

## 3. Detailed Findings: `.agents/skills/**/node_modules/**`

### 3.1 Scope
Only one skill has a `node_modules` directory tracked:
```
.agents/skills/playwright-skill/node_modules/
```

### 3.2 Packages Tracked
Two npm packages and their full compiled library trees are committed to Git:

| Package | Location |
|---|---|
| `playwright` | `.agents/skills/playwright-skill/node_modules/playwright/` |
| `playwright-core` | `.agents/skills/playwright-skill/node_modules/playwright-core/` |

Additionally:
- `.agents/skills/playwright-skill/node_modules/.bin/` — binary symlinks/wrappers (`playwright`, `playwright-core`, and their `.cmd` / `.ps1` Windows variants)
- `.agents/skills/playwright-skill/node_modules/.package-lock.json` — internal lock file

### 3.3 Sub-directory Distribution (playwright-core alone spans)
```
playwright-core/lib/cli/
playwright-core/lib/client/
playwright-core/lib/generated/
playwright-core/lib/mcpBundleImpl/
playwright-core/lib/protocol/
playwright-core/lib/remote/
playwright-core/lib/server/  (chromium, firefox, webkit, bidi, electron, android...)
playwright-core/lib/vite/htmlReport/
playwright-core/lib/vite/recorder/
playwright-core/lib/vite/traceViewer/
playwright-core/types/
```

### 3.4 Tracked Package Manifests
```
.agents/skills/playwright-skill/package.json          ← CORRECT to track
.agents/skills/playwright-skill/package-lock.json     ← CORRECT to track
.agents/skills/playwright-skill/node_modules/.package-lock.json   ← should NOT be tracked
.agents/skills/playwright-skill/node_modules/playwright/package.json    ← should NOT be tracked
.agents/skills/playwright-skill/node_modules/playwright-core/package.json  ← should NOT be tracked
```

### 3.5 Impact Assessment

> [!CAUTION]
> **552 tracked node_modules files is the single most serious Git hygiene violation in this repository.**

- **Repository bloat:** Every clone must download and check out ~552 compiled JS files, binary stubs, and type definitions that can be trivially regenerated with `npm install`
- **Cross-platform compatibility:** The `.bin/` directory contains Windows `.cmd` and `.ps1` scripts that are wrong on Linux/macOS and vice-versa — these will cause CI/CD failures when the project eventually moves to GitHub Actions on Linux runners
- **Security risk:** Pinning vendored package files directly in Git bypasses integrity checks that a clean `npm install` from `package-lock.json` provides
- **Merge conflicts:** Any update to playwright will generate hundreds of file-level conflicts in git history

### 3.6 Why `package.json` and `package-lock.json` ARE correct to track
- `.agents/skills/playwright-skill/package.json` — defines dependencies; **keep**
- `.agents/skills/playwright-skill/package-lock.json` — reproducible install lock; **keep**

---

## 4. Detailed Findings: `graphify-out/**` and Graphify Generated Files

### 4.1 Overview
Graphify is a code-graph analysis tool used by the AI agent environment. Its output directory `graphify-out/` is **fully tracked** in Git with **85 files** across several categories:

### 4.2 File Categories Within `graphify-out/`

#### 4.2.1 Internal Marker / State Files (Hidden, Should NOT be tracked)
```
graphify-out/.graphify_analysis.json
graphify-out/.graphify_detect.json
graphify-out/.graphify_labels.json
graphify-out/.graphify_labels.json.sig    ← signature/integrity file, tool-internal
graphify-out/.graphify_python             ← tool runtime marker
graphify-out/.graphify_root               ← tool runtime marker
graphify-out/.graphify_semantic_marker    ← tool runtime marker
```
These are internal Graphify runtime state files. They serve no collaborative or historical purpose and should be ignored.

#### 4.2.2 AST Cache Files — 30 files (Should NOT be tracked)
```
graphify-out/cache/ast/v0.9.67-s4/<SHA256>.json  (×30 files)
```
- Content-addressable AST (Abstract Syntax Tree) cache entries, keyed by SHA-256 hash of source files
- Pure derivative/computed data; fully regenerated when Graphify runs
- Version-pinned path (`v0.9.67-s4`) means a Graphify update will create an entirely new set of files

#### 4.2.3 Semantic Cache Files — 34 files (Should NOT be tracked)
```
graphify-out/cache/semantic/p5e80268fecd6/<SHA256>.json  (×34 files)
graphify-out/cache/last_query_stamp
graphify-out/cache/stat-index.json
```
- Semantic/embedding vectors for source files, keyed by SHA-256
- `last_query_stamp` — timestamp file; changes on every run
- `stat-index.json` — file stat index; changes on every run
- All are pure tool runtime caches

#### 4.2.4 Human-Readable Generated Outputs (Debatable — possibly keep one, not dated duplicates)
```
graphify-out/GRAPH_REPORT.md      ← latest report (arguably useful to keep)
graphify-out/graph.json           ← 365 KB graph data file
graphify-out/graph.html           ← 335 KB self-contained interactive visualization
graphify-out/manifest.json
```
- `graph.json` (365 KB) and `graph.html` (335 KB) are generated output files
- They are regenerated on every Graphify analysis run
- **700 KB of generated binary-equivalent data that changes on every run is poor Git hygiene**
- `.gitattributes` currently has `graphify-out/graph.json merge=graphify` — this suggests an intent to manage merges but does not prevent bloat

#### 4.2.5 Dated Snapshot Directory (Redundant with root-level files)
```
graphify-out/2026-09-25/.graphify_analysis.json
graphify-out/2026-09-25/.graphify_labels.json
graphify-out/2026-09-25/.graphify_semantic_marker
graphify-out/2026-09-25/GRAPH_REPORT.md
graphify-out/2026-09-25/graph.json
graphify-out/2026-09-25/manifest.json
```
- A per-date snapshot directory duplicating root-level outputs
- Will accumulate new date-stamped directories on every analysis run, growing indefinitely
- `graph.html` is absent here but present at root — inconsistent snapshot

### 4.3 What `.graphifyignore` Currently Does
```
.agents/
```
The `.graphifyignore` only prevents Graphify from *analysing* the `.agents/` directory. It does **not** control what Git tracks — `.graphifyignore` is a Graphify tool configuration file, not a `.gitignore` entry.

### 4.4 `.gitattributes` Current State
```
graphify-out/graph.json merge=graphify
```
- Only one line; defines a custom merge driver for `graph.json`
- **No `text=auto` or `eol` settings** — this is the root cause of the LF→CRLF warning on `.agents/rules/context-guard.md`
- **No `binary` attributes** for binary or large JSON blobs
- **No Git LFS configuration** — large generated files are stored directly in the object database

---

## 5. Inventory of Unnecessarily Tracked or Unignored Files

### 5.1 Files That Should Be Removed from Git Index (Priority: 🔴 Critical)

| Pattern | Count | Reason |
|---|---|---|
| `.agents/skills/playwright-skill/node_modules/**` | 552 | npm dependencies; fully reproducible via `npm install` |
| `graphify-out/cache/**` | 64 | Tool runtime caches; purely derivative data |
| `graphify-out/.graphify_*` | 7 | Tool internal state/marker files |
| `graphify-out/cache/last_query_stamp` | 1 | Timestamp; changes on every run |
| `graphify-out/cache/stat-index.json` | 1 | Stat index; changes on every run |

### 5.2 Files With Debatable Tracking (Priority: 🟡 Medium)

| File / Pattern | Count | Recommendation |
|---|---|---|
| `graphify-out/graph.json` | 1 | Consider ignoring; 365 KB generated file that changes on every run |
| `graphify-out/graph.html` | 1 | Consider ignoring; 335 KB generated file |
| `graphify-out/manifest.json` | 1 | Consider ignoring; generated manifest |
| `graphify-out/GRAPH_REPORT.md` | 1 | Consider keeping only if used as persistent project documentation |
| `graphify-out/2026-09-25/**` | 6 | Consider ignoring entire dated snapshot dirs |

### 5.3 Files That Should Be Added to `.gitignore` Going Forward (Priority: 🟡 Medium)

| Pattern | Reason |
|---|---|
| `artifacts/` | Agent-generated audit reports; not source code |
| `*.log` | Log files |
| `__pycache__/` | Python bytecode cache |
| `*.pyc`, `*.pyo`, `*.pyd` | Python compiled files |
| `.pytest_cache/` | pytest cache |
| `.mypy_cache/` | mypy type-checker cache |
| `.ruff_cache/` | ruff linter cache |
| `dist/`, `build/` | Build artifacts |
| `.next/` | Next.js build output |
| `.vercel/` | Vercel deployment cache |
| `coverage/`, `.coverage`, `htmlcov/` | Test coverage reports |
| `*.env`, `.env.*` (except `.env.example`) | Environment/secret files |
| `node_modules/` (global) | All npm dependency directories |
| `graphify-out/cache/` | Graphify caches |
| `graphify-out/.graphify_*` | Graphify internal markers |
| `graphify-out/*/` | Dated snapshot subdirectories |
| `graphify-out/*.json` | Generated JSON outputs (debatable, see §5.2) |
| `graphify-out/*.html` | Generated HTML outputs |

---

## 6. Recommended Changes for `.gitignore` and `.gitattributes`

### 6.1 Proposed Replacement `.gitignore`

```gitignore
# ============================================================
# EXCEL / COMMERCIAL TABLE FILES
# ============================================================
*.xlsx
*.xls
*.xlsm
*.xlsb
*.xltx
*.xltm
*.xlam
*.csv
# Excel temporary lock files
~$*

# ============================================================
# NODE MODULES
# ============================================================
node_modules/

# ============================================================
# PYTHON ARTIFACTS
# ============================================================
__pycache__/
*.py[cod]
*$py.class
*.pyo
.pytest_cache/
.mypy_cache/
.ruff_cache/
*.egg-info/
dist/
build/
.eggs/
.tox/
.coverage
.coverage.*
htmlcov/
coverage.xml

# ============================================================
# ENVIRONMENT / SECRETS
# ============================================================
.env
.env.*
!.env.example
!.env.template
*.secret
*.secrets

# ============================================================
# JAVASCRIPT / TYPESCRIPT BUILD ARTIFACTS
# ============================================================
.next/
out/
.nuxt/
.cache/
.parcel-cache/
.turbo/
*.tsbuildinfo

# ============================================================
# VERCEL / DEPLOYMENT
# ============================================================
.vercel/

# ============================================================
# GRAPHIFY OUTPUTS AND CACHES
# ============================================================
# Cache directories — always regenerated
graphify-out/cache/
# Internal Graphify state/marker files
graphify-out/.graphify_*
# Dated snapshot subdirectories — accumulate indefinitely
graphify-out/[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]/
# Generated binary outputs (large, regeneratable)
graphify-out/*.json
graphify-out/*.html
# NOTE: Keep graphify-out/GRAPH_REPORT.md if used as persistent docs

# ============================================================
# AGENT ARTIFACTS AND REPORTS
# ============================================================
artifacts/

# ============================================================
# OS / EDITOR FILES
# ============================================================
.DS_Store
Thumbs.db
*.swp
*.swo
*~
.vscode/settings.json
.idea/

# ============================================================
# LOGS
# ============================================================
*.log
logs/
npm-debug.log*
yarn-debug.log*
yarn-error.log*

# ============================================================
# TEMPORARY FILES
# ============================================================
*.bak
*.tmp
*.temp
tmp/
temp/
```

### 6.2 Proposed Replacement `.gitattributes`

```gitattributes
# ============================================================
# DEFAULT BEHAVIOR — normalize line endings
# ============================================================
* text=auto eol=lf

# ============================================================
# FORCE LF FOR SCRIPTS (avoids CRLF breakage on Linux CI)
# ============================================================
*.sh text eol=lf
*.bash text eol=lf
*.py text eol=lf
*.js text eol=lf
*.ts text eol=lf
*.tsx text eol=lf
*.json text eol=lf
*.md text eol=lf
*.yaml text eol=lf
*.yml text eol=lf
*.toml text eol=lf
*.env text eol=lf

# ============================================================
# WINDOWS SCRIPTS — keep CRLF
# ============================================================
*.cmd text eol=crlf
*.bat text eol=crlf
*.ps1 text eol=crlf

# ============================================================
# BINARY FILES — no diff, no merge
# ============================================================
*.xlsx binary
*.xls binary
*.xlsm
*.xlsb binary
*.png binary
*.jpg binary
*.jpeg binary
*.gif binary
*.ico binary
*.woff binary
*.woff2 binary
*.ttf binary
*.eot binary
*.zip binary
*.tar.gz binary
*.tgz binary

# ============================================================
# GRAPHIFY — custom merge strategy for graph output
# ============================================================
graphify-out/graph.json merge=graphify

# ============================================================
# LARGE GENERATED FILES — mark as generated (linguist)
# ============================================================
graphify-out/** linguist-generated=true
.agents/skills/playwright-skill/node_modules/** linguist-generated=true
```

---

## 7. Proposed Remediation Steps (DO NOT EXECUTE — Reference Only)

> [!IMPORTANT]
> All commands below are **proposed only**. They must be reviewed and approved by the development team before execution. Run them in order. Back up your repository first (`git bundle create ../backup.bundle --all`).

### Step 0 — Create a Safety Backup
```powershell
# From the repo root
git bundle create ..\cotarco-backup-before-cleanup.bundle --all
```

### Step 1 — Remove `node_modules` from Git Index (Keep on Disk)
```bash
# Untrack all node_modules without deleting local files
git rm -r --cached .agents/skills/playwright-skill/node_modules/
```

### Step 2 — Remove Graphify Cache and Marker Files from Index
```bash
# Remove the cache directories from index (keep local files)
git rm -r --cached graphify-out/cache/
git rm -r --cached graphify-out/.graphify_analysis.json
git rm -r --cached graphify-out/.graphify_detect.json
git rm -r --cached graphify-out/.graphify_labels.json
git rm -r --cached graphify-out/.graphify_labels.json.sig
git rm -r --cached graphify-out/.graphify_python
git rm -r --cached graphify-out/.graphify_root
git rm -r --cached graphify-out/.graphify_semantic_marker
# Remove dated snapshots
git rm -r --cached "graphify-out/2026-09-25/"
```

### Step 3 — Optionally Remove Large Generated Graphify Outputs
```bash
# Only if the team decides these should not be tracked:
git rm --cached graphify-out/graph.json
git rm --cached graphify-out/graph.html
git rm --cached graphify-out/manifest.json
# Keep GRAPH_REPORT.md if it serves as project documentation
```

### Step 4 — Replace `.gitignore` with the Comprehensive Version
Replace the content of `.gitignore` with the proposed content from §6.1.

### Step 5 — Replace `.gitattributes` with the Improved Version
Replace the content of `.gitattributes` with the proposed content from §6.2.

### Step 6 — Fix Line Ending Issue on `context-guard.md`
After setting `* text=auto eol=lf` in `.gitattributes`:
```bash
# Normalize line endings across the repo
git add --renormalize .
```

### Step 7 — Commit the Cleanup
```bash
git add .gitignore .gitattributes
git commit -m "chore: fix git hygiene — ignore node_modules, graphify caches, add comprehensive gitignore and gitattributes"
```

### Step 8 — Rewrite History (Optional but Recommended for Public Repo)
If this is a public repository and you wish to permanently expunge the tracked node_modules from history (reduces clone size significantly):

> [!CAUTION]
> History rewriting is **destructive** and requires force-pushing. All collaborators must re-clone. Coordinate this carefully.

```bash
# Using git filter-repo (install: pip install git-filter-repo)
git filter-repo --path .agents/skills/playwright-skill/node_modules/ --invert-paths
git filter-repo --path graphify-out/cache/ --invert-paths

# Then force push
git push origin main --force-with-lease
```

### Step 9 — Run `npm install` to Restore Local Dependencies After Cleanup
```bash
cd .agents/skills/playwright-skill
npm install
cd ../../..
```

---

## 8. Summary of Violations by Severity

### 🔴 Critical (Must Fix)
1. **552 `node_modules` files tracked** in `.agents/skills/playwright-skill/node_modules/` — these should never enter version control; the `package.json` and `package-lock.json` already provide full reproducibility
2. **64 Graphify cache files tracked** in `graphify-out/cache/` — these are machine-generated, content-addressed cache blobs with no collaborative value
3. **`.gitignore` only covers Excel extensions** — completely missing `node_modules/`, Python artifacts, build outputs, and environment files

### 🟡 Medium (Should Fix)
4. **85 Graphify files tracked total** — including `graph.json` (365 KB) and `graph.html` (335 KB) that regenerate on every analysis run
5. **Dated snapshot directories** (`graphify-out/2026-09-25/`) will accumulate indefinitely in Git history with no retention policy
6. **`.gitattributes` lacks `text=auto eol=lf`** — causing the CRLF warning on `.agents/rules/context-guard.md` and risking line-ending corruption across editors/OSes
7. **`artifacts/` untracked but not in `.gitignore`** — creates noisy `git status` output for all developers

### 🟢 Low (Good Hygiene)
8. **`.agents/rules/context-guard.md` has unstaged local modifications** — should be reviewed and either committed or restored
9. **Only 4 commits** in history — early hygiene fixes are low-cost since there's little history to rewrite

---

## 9. What Is Correctly Configured

- ✅ No `.env` or secrets files are tracked
- ✅ No `.bak`, `.zip`, or `.tmp` files found
- ✅ `package.json` and `package-lock.json` for playwright-skill are correctly tracked
- ✅ All `cotarco-commercial-manager/**` documentation is correctly tracked
- ✅ `.graphifyignore` correctly excludes `.agents/` from Graphify analysis
- ✅ `.gitattributes` has a merge strategy for `graphify-out/graph.json` (though the file itself should ideally be ignored)
- ✅ Remote points to correct GitHub repository

---

*Report generated: 2026-09-25T11:57:00+01:00*  
*Audit mode: READ-ONLY — no files were modified, staged, or committed during this audit*
