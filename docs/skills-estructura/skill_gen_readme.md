# skill_gen_readme
# Agent: agent_docs
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates complete README.md for developer onboarding.
Sections: stack, prereqs, install, env vars, structure, arch, workflow, commands, license.

---

## INPUT CONTRACT
See docs/F3_SKILLS.md for full input contract.
Refer to agent agent_docs AGENT.md for prerequisites and RAG access.

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
  "agent":   "agent_docs",
  "task_id": "{task_id}",
  "skill":   "skill_gen_readme",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
