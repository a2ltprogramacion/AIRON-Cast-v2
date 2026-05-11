# skill_ghl_workflow_ops
# Agent: agent_ghl
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Manages GHL workflow enrollment: enroll/status/remove.
Max 20 contacts per call. Rate guard enforced.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_ghl AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_ghl",
  "task_id": "{task_id}",
  "skill":   "skill_ghl_workflow_ops",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
