# skill_run_tests
# Agent: agent_tester
# Version: 1.0
# Pattern: Deterministic

---

## DESCRIPTION
Executes Django test suite. Maps results to AC coverage.
Verdict: PASSED | PASSED_WITH_GAPS | FAILED | TIMEOUT. timeout_s min=60.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_tester AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_tester",
  "task_id": "{task_id}",
  "skill":   "skill_run_tests",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
