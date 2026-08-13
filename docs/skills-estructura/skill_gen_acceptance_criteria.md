# skill_gen_acceptance_criteria
# Agent: agent_pm
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates Given/When/Then acceptance criteria for development tickets.
Each criterion gets ID: AC-NNN.
Minimum per ticket: 2 positive scenarios + 1 negative scenario.
Activate when: TK-NNN exists in task_memory.
Do NOT generate criteria without a parent ticket.

---

## INPUT CONTRACT
{
  "task_id":     "{str}",
  "workflow_id": "{str}",
  "tk_id":       "TK-NNN",
  "context":     "{str} — business rules or constraints"
}

---

## EXECUTION FLOW

STEP 1 — RETRIEVE TICKET
  Query task_memory:
    filter: { workflow_id: workflow_id,
              skill: "skill_gen_ticket" }
  Find ticket with id = tk_id.
  If not found: STOP.

STEP 2 — IDENTIFY SCENARIOS
  From ticket description and context identify:
    Positive: happy path, edge cases that should pass
    Negative: invalid input, unauthorized access, boundary violations
  Minimum: 2 positive + 1 negative.

STEP 3 — GENERATE CRITERIA
  Format per criterion:
    ID:       AC-NNN
    Parent:   TK-NNN
    Type:     positive | negative
    Given:    {initial context / state}
    When:     {user action or system event}
    Then:     {expected observable outcome}

STEP 4 — VALIDATE
  □ Each criterion is independently verifiable
  □ "Then" describes observable behavior, not implementation
  □ At least 1 negative scenario present

---

## OUTPUT FORMAT
{
  "agent":   "agent_pm",
  "task_id": "{task_id}",
  "skill":   "skill_gen_acceptance_criteria",
  "status":  "completed | failed",
  "output": {
    "parent_ticket": "TK-NNN",
    "criteria": [
      {
        "id":     "AC-NNN",
        "type":   "positive | negative",
        "given":  "{str}",
        "when":   "{str}",
        "then":   "{str}"
      }
    ],
    "count": {
      "positive": {int},
      "negative": {int},
      "total":    {int}
    }
  },
  "tokens":  {int},
  "error":   null | "{description}"
}
