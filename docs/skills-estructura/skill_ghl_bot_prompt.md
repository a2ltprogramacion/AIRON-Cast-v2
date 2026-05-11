# skill_ghl_bot_prompt
# Agent: agent_ghl
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates GHL bot prompts in 9-section A2LT standard with nested Markdown delimiters.
Always in Spanish. Tone: formal/semiformal/casual.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_ghl AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_ghl",
  "task_id": "{task_id}",
  "skill":   "skill_ghl_bot_prompt",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
