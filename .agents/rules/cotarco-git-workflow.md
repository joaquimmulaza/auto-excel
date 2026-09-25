---
trigger: model_decision
description: Apply this rule when a task is successfully completed and all tests are green, ready for commit.
---

Commit messages in English following Conventional Commits format: `<type>(<scope>): <description>` or `<type>: <description>`.

Canonical Types (per `cotarco-commercial-manager/agents.md §9`): `feat`, `fix`, `refactor`, `test`, `docs`, `chore`, `security`.

Flow:
1. Stage surgically: `git add <specific-files>` (never use `git add .`)
2. Commit: `git commit -m "<type>(<scope>): <description>"`
3. Push gate: Aguardar confirmação humana explícita antes de qualquer git push (require explicit human confirmation before pushing; never push automatically).

Prohibitions:
- Never commit if there are failing tests.
- Never use blanket staging (`git add .` or `git add -A`).
- Never run `git push` automatically without explicit human confirmation.