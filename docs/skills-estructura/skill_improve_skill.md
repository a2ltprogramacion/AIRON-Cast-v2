# skill_improve_skill
# Agent: agent_forge
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Generates skill improvement proposals with failure type classification.
Outputs structured improvement plan.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_forge AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_forge",
  "task_id": "{task_id}",
  "skill":   "skill_improve_skill",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
