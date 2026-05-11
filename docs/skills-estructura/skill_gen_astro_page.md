# skill_gen_astro_page
# Agent: agent_frontend
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Assembles Astro page files composing generated components into routes.
Input: screen_id + route + layout + data_source. Output: src/pages/{route}.astro.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_frontend AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_frontend",
  "task_id": "{task_id}",
  "skill":   "skill_gen_astro_page",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
