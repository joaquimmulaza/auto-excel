---
trigger: always_on
---

# General Workspace Rules

These operational rules apply globally to all tasks and interactions within the Cotarco workspace to ensure consistency, maintainability, and clean architecture.

## 1. Zero Guesswork
Never invent or assume behavior. If a feature's behavior or an API's schema is unclear, pause and investigate. Explicitly mention any uncertainties before proceeding.

## 2. Documentation-First Approach
Any non-obvious architecture, data flows, or complex logic discovered during a task must be documented in the `.notebook/` directory. Keep the `context.md` file updated if system-level changes are made.

## 3. Surgical Edits
Keep modifications strictly scoped to the objective. Do not touch unrelated files or refactor surrounding code unless explicitly requested. Match the existing style and conventions perfectly.

## 4. Test-Driven Assurance
Ensure that all existing tests (unit and E2E) continue to pass after any modifications. If modifying features covered by existing tests, update the tests accordingly.

## 5. Explicit Planning
For any task beyond a trivial typo fix, always outline a step-by-step execution plan and wait for the developer's confirmation or verification before executing.

## 6. Meaningful Commits
Commits should be atomic and represent a single logical change. Write descriptive commit messages that explain the *why* alongside the *what*.
