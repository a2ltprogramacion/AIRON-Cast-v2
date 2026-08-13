# Forge Exploration Protocol: Meta-Requirement Extraction

**Purpose:** To define the exact parameters, boundaries, and dependencies of a new AI Component (Skill, Agent, Workflow) before it is physically written to the `Skills-A2LT` repository.

## 1. Contextual Meta-Inquiry

- **Ecosystem Scan:** Use `list_dir` and `grep_search` on `.agent/core/` and `.agent/catalog/` to ensure no component with a similar name or purpose already exists (Collision Detection).
- **Memory Review:** Search `.agent/memory/journal/` for past entries related to the domain you are about to build. (e.g., if building an API skill, read past API failures).

## 2. Phased Questioning for Meta-Programming

Deliver questions sequentially to the Operator. Use the following taxonomy:

### A. Taxonomy & Placement

- “Will this component reside in `core/` (tooling for Antigravity) or `catalog/` (deployable product for clients)?”
- “Is this an Agent (role), a Skill (tool), or a Workflow (process)?”

### B. Architectural Pattern (For Skills)

- “Based on the constraints, should this be a **High Freedom** (Markdown only), **Deterministic** (with Python/Bash scripts), or **Deep Domain** (with references/ directory) pattern?”
- **MANDATORY DIRECTIVE:** “Acknowledge that the **DeepSeek Handoff** (Bi-Modelo) is strictly REQUIRED for all component generation (Meta-Programming) to counteract the Agent's inherent brevity bias. Do NOT ask if it is needed; affirm its execution.”

### C. Input Contract & Interactions (For Agents & Skills)

- “What specific `description` (trigger keywords) will guarantee focus and prevent misfiring?”
- “If it's a deterministic skill, what parameters (Input Contract) does the script expect via terminal?”
- “Which other existing skills or agents must this new component interact with?”

### D. Payload Assembly Constraints (If applicable)

- “If we are assembling a Payload, which specific agents/skills are going to the client?”
- “Are we absolutely certain no `core/` components are leaking into the `output/.agent/` flat structure?”

### E. Adversarial Probing (Ecosystem Health)

- “If we build this Agent/Skill, could it overlap and confuse the Orchestrator when choosing between this and [Existing Skill X]?”
- “If the script crashes (Exit Code > 0), how does the agent gracefully recover without operator intervention?”

## 3. Documenting the Meta-Design

- Distill the answers into a **Component Blueprint Statement**:
  - Exact file paths to be created.
  - Activation Trigger logic.
  - Dependencies (Python packages, other skills).
  - QA Validation plan (`validate_skill_structure.py` expectation).
- This statement feeds into the **Architecture Presentation Protocol**.

## 4. Transition to Presentation

Proceed to the formal design presentation only when the Taxonomy, Pattern, and Triggers are completely unambiguous.
