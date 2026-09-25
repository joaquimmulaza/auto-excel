---
trigger: model_decision
description: Apply this rule when a task is successfully completed and all tests are green, ready for commit and push.
---

Commit messages in English with the pattern [Type]: Description.

Types: feat, fix, ui, refactor, test, chore.

Flow: git add . -> git commit -m "..." -> git push.

Prohibition: Never commit if there are failing tests.