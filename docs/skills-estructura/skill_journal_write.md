# skill_journal_write
# Agent: agent_forge
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Writes institutional memory entries. Types: workflow_run, agent_failure, arch_decision, pattern, improvement.
Indexed in agent_knowledge ChromaDB.

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
  "skill":   "skill_journal_write",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
