# skill_gen_email_sequence
# Agent: agent_writer
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates email sequences: welcome/nurture/conversion/reactivation.
Max 5 emails. Always includes [UNSUBSCRIBE_LINK]. No ALL CAPS in subjects.

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
  "skill":   "skill_gen_email_sequence",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
