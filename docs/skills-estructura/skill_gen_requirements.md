# skill_gen_requirements
# Agent: agent_infra
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Generates pinned requirements.txt + requirements-dev.txt from tech stack definition.
No network required — uses stack_versions.md reference.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_infra AGENT.md for prerequisites and RAG access.

---

## EXECUTION FLOW
1. Retrieve required context from task_memory / project_context via RAG + HyDE
2. Validate input completeness and prerequisites
3. Execute generation following pattern: Deterministic
4. Validate output structure
5. Return JSON output contract

---

## OUTPUT FORMAT
{
  "agent":   "agent_infra",
  "task_id": "{task_id}",
  "skill":   "skill_gen_requirements",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
