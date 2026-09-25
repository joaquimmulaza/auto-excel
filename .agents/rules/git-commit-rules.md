---
trigger: model_decision
description: Activate this rule only after all tests have successfully run (green status) and the current technical task has been fully completed, in order to write the final commit message strictly following the style guidelines and prefixes.
---

Commit Messages must have a short description that is less than 50 characters followed by a newline and a more detailed description.
- Commit message must have one of the canonical Conventional Commits prefixes matching `cotarco-commercial-manager/agents.md §9`: "feat: ", "fix: ", "refactor: ", "test: ", "docs: ", "chore: ", "security: " (optional scope allowed in parentheses, e.g., "feat(auth): ")
- Use markdown syntax
- Write concisely using an informal tone
- List significant changes
- Do not use specific names or files from the code
- Do not use phrases like "this commit", "this change", etc.
- Sentences in the detailed description should be separated by newlines
- Mention implications and possible usages of the code changes
- Do not respond as code with ``` at the end of the message