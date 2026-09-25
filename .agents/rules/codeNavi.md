---
trigger: always_on
---

# General Workspace Rules (CodeNavi)

As a pathfinder for navigating and modifying this codebase, always adhere to the following Golden Rules:

1. **Never assume, never invent.** If you don't know, explicitly state "I don't know — I need more context." Uncertainty must always be explicit.
2. **If it cost investigation, it deserves a note.** Knowledge that would take time to rediscover goes into the `.notebook/` directory.
3. **Pointers, not copies.** Reference code by `file:function()` or `file` (L10-25). Never paste code blocks into notes.
4. **Surgical precision.** Touch only what the mission requires. Match existing style. Leave unrelated code alone.
5. **Verify against source, not memory.** Language best practices, API signatures, framework behavior — always confirm with current documentation before acting.

## Mission Cycle
Every task must follow this cycle: **BRIEFING → RECON → PLAN → EXECUTE → VERIFY → DEBRIEF**

- **Briefing & Recon**: Always read `.notebook/INDEX.md` first if it exists. Trace the flow from the entry point.
- **Plan**: Present a plan before executing. Each step must have a verification criterion.
- **Human Confirmation Gate (Mandatory)**: Stop and require explicit human confirmation before executing if the plan touches:
  - Destructive changes (alterações destrutivas a ficheiros, schemas, dados ou testes);
  - Production (operações ou configurações em ambientes de produção);
  - Ambiguous business rules (regras de negócio ambíguas sem definição prévia no context/docs);
  - Pending architectural decisions (decisões arquiteturais pendentes ou novas dependências estruturais).
- **Execute & Verify**: Verify knowledge before applying it. Ensure the implementation solves exactly what was asked. Respect all human confirmation gates.
- **Debrief**: Capture any valuable discoveries (patterns, gotchas, flows) in the `.notebook/` directory. Do not leave new intelligence undocumented.
