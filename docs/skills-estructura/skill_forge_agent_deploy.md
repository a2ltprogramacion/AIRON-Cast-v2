# skill_forge_agent_deploy
# Agent: agent_forge
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Deploys new or updated agent. Requires passing audit. Registers in SQLite + ChromaDB.
Runs adapt.py --detect after deploy for multi-env compatibility.

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
  "skill":   "skill_forge_agent_deploy",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
