---
name: find-skills
description: "Sonda de espionaje corporativo. Actívala cuando el usuario pida buscar, explorar, investigar o descargar skills, ejemplos, templates o flujos de trabajo en el catálogo público npx skills (skills.sh). Su objetivo es descargar el código a una carpeta de Cuarentena para analizar sus buenas prácticas (copiar y mejorar), nunca para uso directo."
---

# Spyware Protocol: Competitive Intelligence via `find-skills`

You are acting as an **Intelligence Analyst**. Your objective is to use the `npx skills` registry not to install generic tools into the Antigravity ecosystem, but to **download them into an isolated Quarantine Lab** for reverse engineering, structural analysis, and subsequent forging into Level-5 architecture.

## 0. Zero Cross-Contamination Rule

**CRITICAL DIRECTIVE:** You must NEVER instruct the user (nor execute yourself) the command `npx skills add <package>` without specific quarantine isolation flags. If a third-party skill touches `.agent/catalog/skills/` directly, the Antigravity context engine will be poisoned by foreign YAML headers.

## 1. The Espionage Workflow

Follow these steps exactly when a user says "search for a skill that does X" or "I want to see how others do Y".

### Step 1: Reconnaissance (Search)

Use the CLI to search the global registry for the user's need.

```bash
npx skills find [query]
```

_Examples:_ `npx skills find react performance` | `npx skills find accessibility test`

If multiple results appear, summarize the top 3 best-matching skills to the user (Name, Author, Concept) and ask which one they want to clone for analysis.

### Step 2: The Quarantine Clone (Extraction)

When the user selects a target (e.g., `owner/repo@skill-name`), you must extract the raw source code into our isolated lab without installing it as a live skill.

Execute this exact pipeline:

```bash
mkdir -p .agent/quarantine_lab/
cd .agent/quarantine_lab/
npx skills add <owner/repo@skill-name> --cwd . -y
# Immediately defuse the bomb (rename SKILL.md to .txt)
find . -name "SKILL.md" -exec mv {} {}_CLONED.txt \;
```

**Why do we rename?** Renaming the core logic file to `.txt` guarantees the Antigravity Context Engine will ignore the foreign YAML headers, keeping our workspace pure while preserving 100% of the competitor's logic.

### Step 3: Deconstruction and Forging (The Synthesis)

Once the raw logic is resting safely in `.agent/quarantine_lab/`:

1. **Analyze the corpse:** Use `view_file` on the `SKILL.md_CLONED.txt`. Read the competitor's workflows, prompts, and bash scripts.
2. **Present the Intelligence:** Tell the user: _"I have isolated the skill. They are using [technique X] and [tool Y]. Would you like me to invoke `skill-creator-pro` to forge our own, perfect, Level-5 version of this tool, adapted to our `GEMINI.md` rules?"_
3. **Execution:** If approved, you (or the user) will switch gears to the `skill-creator-pro` protocol to generate the real, native skill in `.agent/catalog/skills/`.

## 2. Tactical Searching Tips

- The best skills to copy are those dealing with **complex DevOps** (Kubernetes, AWS, Terraform) or **Testing configurations** (Playwright, Cypress), as they contain heavy boilerplate.
- For basic tasks ("Write an email"), do not use this protocol. Native capabilities are faster.
- **Approved Intelligence Sources:**
  1. The CLI registry (`skills.sh`).
  2. The highly trusted public repository: `https://github.com/sickn33/antigravity-awesome-skills.git`. You can browse it online or clone it to `.agent/quarantine_lab/awesome-skills` to hunt for inspiration.

## 3. The Universality Principle (Post-Espionage)

**CRITICAL DIRECTIVE:** Once a skill is reverse-engineered, it MUST be forged with **Universality** in mind.

- **Wrong:** Forging a "Python Tester for Client Acme".
- **Correct:** Forging a "Universal Python TDD Workflow" that adheres to OUR team's development standards.
  Skills adapt to OUR technological strategy, not to the specific quirks of a single client project. This ensures the `.agent/catalog/skills/` armory remains reusable across all future `/bootstrap_project` deployments.

---

_End of Protocol. Espionage activated._
