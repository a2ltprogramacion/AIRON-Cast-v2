# Architecture Presentation Protocol (Forge Specific)

**Purpose:** To present a structured, physically accurate blueprint of the intended AI Component (or Payload) to the Operator, ensuring strict adherence to A2LT structural rules before invoking the actual generators.

## 1. Design Document Structure (The Forge Blueprint)

Present the design using the following structure. It must map exactly to how the filesystem will be modified.

````
# Meta-Design: [Component Name]

## 1. Taxonomy & Location
- **Type:** [Skill / Agent / Workflow / Payload]
- **Target Directory:** `.agent/[core|catalog]/[type]/[name]/`

## 2. Activation & Identity (Frontmatter)
- **Name:** `[kebab-case-name]`
- **Description/Trigger:** `[Exact Spanish trigger phrase and conditions]`
- **Hard-Gates / Anti-Patterns:** What this component is explicitly forbidden from doing.

## 3. Deep Domain Structure (File Tree)
```text
[name]/
├── SKILL.md (or AGENT.md)
├── scripts/
│   └── [script_name.py] (if Deterministic)
└── references/
    └── [reference_name.md] (if Deep Domain)
````

## 4. Code & Logic Strategy

- **If Scripting:** How will it handle dependencies (autogenerate `.env`) and Exit Codes?
- **LLM Handoff (MANDATORY):** Explicitly state the preparation of the `deepseek_payload.md`. DeepSeek generation is NEVER optional for Forge construction in order to guarantee maximum code density and bypass Antigravity's brevity bias.

## 5. Ecosystem QA Plan

- Explicit confirmation that `validate_skill_structure.py` (or agent equivalent) will be run.
- Edge cases to test in the Sandbox (`quarantine_lab/`) before handoff.

## 6. Operator Approval

- [ ] Awaiting Operator Sign-off.

```

## 2. Presentation Technique

- **Do NOT execute `write_to_file` or `run_command` to create the component yet.**
- Present the blueprint visually in the chat or save it incrementally to `task.md` / `journal/`.
- Ask: _"Does this structure and trigger mechanism avoid collisions with our existing catalog?"_
- Affirm: _"I will now prepare the `deepseek_payload.md` for this architecture following the mandatory Anti-Brevity Handoff directive."_

## 3. YAGNI Enforcement (Forge Level)

- Actively strip references or scripts that aren't strictly necessary for the V1 of the skill.
- If a skill can be a High Freedom (single Markdown) instead of a Deep Domain, propose the simpler version first. Minimizing token context is the highest priority in the Forge.

## 4. Incremental Validation & Sign‑Off

- Require explicit Operator text: "Aprobado", "Procede", or "Ejecuta".
- Once approved, immediately transition to the implementation phase (e.g., invoking `skill-creator-pro` or writing the files directly if bypass is authorized).

## 5. Transition to Implementation (The "Build" Phase)

- Upon sign-off, transition to **EXECUTION** mode.
- Materialize the exact directory tree presented.
- Run the mandatory QA scripts.
- Log the operation in High-Density English in the `.agent/memory/journal/`.
```
