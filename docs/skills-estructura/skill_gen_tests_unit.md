# skill_gen_tests_unit
# Agent: agent_backend
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Generates Django unit tests with factory_boy: factories.py, test_models, test_serializers, test_views.
Input: app_name + scope. Maps to AC coverage.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_backend AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_backend",
  "task_id": "{task_id}",
  "skill":   "skill_gen_tests_unit",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
