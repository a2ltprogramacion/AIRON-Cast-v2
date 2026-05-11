# skill_ghl_custom_fields
# Agent: agent_ghl
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Creates/lists/maps custom fields on GHL contacts or opportunities.
Never deletes. Always checks for duplicates before creating.

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
  "skill":   "skill_ghl_custom_fields",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
