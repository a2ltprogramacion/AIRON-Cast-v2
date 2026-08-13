# skill_gen_copy_landing
# Agent: agent_writer
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates conversion-oriented landing copy: hero, value_prop, features, social_proof, faq, cta.
In Spanish. social_proof uses placeholders.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_writer AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_writer",
  "task_id": "{task_id}",
  "skill":   "skill_gen_copy_landing",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
