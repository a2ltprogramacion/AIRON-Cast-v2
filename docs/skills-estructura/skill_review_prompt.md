# skill_review_prompt
# Agent: agent_reviewer
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Reviews GHL bot prompts against 9-section standard, tone, and business alignment.
Verdict: APPROVED | APPROVED_MINOR | REJECTED.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_reviewer AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_reviewer",
  "task_id": "{task_id}",
  "skill":   "skill_review_prompt",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
