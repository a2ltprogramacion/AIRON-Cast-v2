# skill_gen_wireframe_spec
# Agent: agent_uxui
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates wireframe specifications per screen: layout, sections, components, responsive.
Input: flow_id + screen_ids. Output: WFS-{id}.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_uxui AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_uxui",
  "task_id": "{task_id}",
  "skill":   "skill_gen_wireframe_spec",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
