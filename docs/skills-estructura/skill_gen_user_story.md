# skill_gen_user_story
# Agent: agent_pm
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates user stories in standard format "As a / I want / So that"
from project objectives and stakeholder inputs.
Each story gets a unique ID: US-NNN.
Activate when: a new feature or module needs to be scoped before
ticket breakdown.
Do NOT create tickets or acceptance criteria — stories only.
Do NOT assign story points or estimates.

---

## INPUT CONTRACT
{
  "task_id":      "{str}",
  "workflow_id":  "{str}",
  "objective":    "{str} — what the feature must achieve",
  "actor":        "{str} — who uses this feature",
  "scope":        "{str} — module or feature name",
  "priority":     "high | medium | low"
}

---

## EXECUTION FLOW

STEP 1 — RETRIEVE EXISTING STORIES
  Query task_memory:
    filter: { workflow_id: workflow_id,
              skill: "skill_gen_user_story" }
  Determine next available US-NNN sequence number.
  If no stories exist: start at US-001.

STEP 2 — DECOMPOSE OBJECTIVE
  Break objective into atomic user needs.
  Each need = one user story.
  Maximum 5 stories per skill call.
  If more needed: split into multiple calls.

STEP 3 — GENERATE EACH STORY
  Format:
    ID:       US-NNN
    Title:    {3-7 words describing the feature}
    Story:    As a {actor}, I want {capability},
              so that {benefit}.
    Priority: {high | medium | low}
    Notes:    {any constraints or clarifications}

STEP 4 — VALIDATE
  For each story verify:
    □ Actor clearly identified
    □ Capability is specific (not vague)
    □ Benefit describes user value, not system behavior
    □ Story is independent (not dependent on another US)

---

## OUTPUT FORMAT
{
  "agent":   "agent_pm",
  "task_id": "{task_id}",
  "skill":   "skill_gen_user_story",
  "status":  "completed | failed",
  "output": {
    "stories": [
      {
        "id":       "US-NNN",
        "title":    "{str}",
        "actor":    "{str}",
        "want":     "{str}",
        "so_that":  "{str}",
        "priority": "high | medium | low",
        "notes":    "{str | null}"
      }
    ],
    "count": {int}
  },
  "tokens":  {int},
  "error":   null | "{description}"
}
