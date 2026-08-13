# Quality Checklist for Agent Forging

Mandatory manual QA matrix prior to authenticating a new `.md` Profile in the `.agent/agents/` armory.

### 1. Structural Regex & Parsing

- [ ] Does the file utilize the `.md` extension strictly?
- [ ] Is the absolute header formatted exactly as `# Agent Profile: [Name]`?
- [ ] Does the asset pass automated validation? Execute `python validate_agent_profile.py <file.md>`. Must yield Exit Code 0 with zero warnings.

### 2. Constraint Boundaries (Safety & Scope)

- [ ] Does the agent possess explicit `Prohibited` commands? An agent devoid of restrictions is categorized as an architectural hazard.
- [ ] Do the prohibitions correctly safeguard adjacent modules? (e.g., A Frontend UI tester is strictly prohibited from executing DDL statements against the SQL schema).
- [ ] **[Iterator agents only]** Is the `Iteration Mandate` field populated? An orchestrator agent without an explicit bulk-consumption directive is a latent single-item trap.

### 3. Toolchain Allocation (Assigned Skills)

- [ ] Are the binaries indexed under `Assigned Skills` physically present inside the host `.agent/skills/` directory?
- [ ] Are the assigned skills hyper-relevant to the agent's core identity? Remove unused bloat.

### 4. Geometric Orchestration & Handoff

- [ ] Are the `Upstream` and `Downstream` nodes explicitly declared?
- [ ] Does the `Handoff Phrase (Success)` provide actionable context to the downstream node? (It must transmit runtime variables, compiled file paths, or target ports, not just "Done").
- [ ] If acting as a Gatekeeper, is the `Handoff Phrase (Failure)` declared to safely return execution upstream on error?

### 5. Prompt Engineering QA (Activation Precision)

This section validates that the agent's `Primary Objective` and description are semantically precise enough to be invoked correctly — and NOT invoked incorrectly.

- [ ] **Trigger clarity:** Can the `Primary Objective` be summarized in one sentence that unambiguously distinguishes this agent from its closest neighbor in the armory?
- [ ] **Boundary sharpness:** Are there 1-2 explicit examples of what this agent should REFUSE to do? ("This agent does NOT write backend logic. It does NOT modify SQL schemas.")
- [ ] **Activation examples:** Does the agent profile include at least 2 concrete activation scenarios? Format:
  ```
  Scenario: [realistic situation]
  Trigger: "[exact phrase or condition that wakes this agent]"
  Expected behavior: "[first 2 actions the agent takes]"
  ```
- [ ] **Collision test:** Does the `Primary Objective` remain unambiguous when read alongside the profiles of its 2-3 closest semantic neighbors? If overlap exists, tighten the boundary or merge agents.
- [ ] **Anti-mediocrity gate:** Would this agent's output be distinguishable from a generic LLM response? If not, it lacks sufficient specialization and must be refactored.
