# skill_gen_decap_config
# Agent: agent_frontend
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates Decap CMS config.yml for landing/web_app projects.
Input: collections[]. Output: public/admin/config.yml. Skipped for api/automation.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_frontend AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_frontend",
  "task_id": "{task_id}",
  "skill":   "skill_gen_decap_config",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
