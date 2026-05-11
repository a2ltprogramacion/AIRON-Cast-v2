# skill_context7_resolve
# Agent: agent_backend,agent_frontend,agent_ghl
# Version: 1.0
# Pattern: External MCP

---

## DESCRIPTION
Retrieves current documentation via Context7 MCP. No credentials sent.
Input: library + query. Output: current docs snippet.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_backend,agent_frontend,agent_ghl AGENT.md for prerequisites and RAG access.

---

## EXECUTION FLOW
1. Retrieve required context from task_memory / project_context via RAG + HyDE
2. Validate input completeness and prerequisites
3. Execute generation following pattern: External MCP
4. Validate output structure
5. Return JSON output contract

---

## OUTPUT FORMAT
{
  "agent":   "agent_backend,agent_frontend,agent_ghl",
  "task_id": "{task_id}",
  "skill":   "skill_context7_resolve",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
