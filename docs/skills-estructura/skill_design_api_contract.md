# skill_design_api_contract
# Agent: agent_architect
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Designs REST API contracts: endpoints, methods, request/response schemas, auth.
Input: arch_id + schema_id + resources[]. Output: API-{id} with endpoints[].

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_architect AGENT.md for prerequisites and RAG access.

---

## EXECUTION FLOW
1. Retrieve required context from task_memory / project_context via RAG + HyDE
2. Validate input completeness and prerequisites
3. Execute generation following pattern: Template
4. Validate output structure
5. Return JSON output contract

---

## OUTPUT FORMAT
{
  "agent":   "agent_architect",
  "task_id": "{task_id}",
  "skill":   "skill_design_api_contract",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
