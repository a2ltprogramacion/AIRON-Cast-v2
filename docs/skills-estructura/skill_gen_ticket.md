# skill_gen_ticket
# Agent: agent_pm
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Generates development tickets from user stories.
Each ticket traces to a parent US-NNN and gets ID: TK-NNN.
Activate when: user stories exist in task_memory for the workflow.
Do NOT generate tickets without a parent US-NNN.
Do NOT assign to specific developers.

---

## INPUT CONTRACT
{
  "task_id":     "{str}",
  "workflow_id": "{str}",
  "us_id":       "US-NNN",
  "ticket_type": "feature | bug | task | spike",
  "scope":       "{str} — what this ticket covers"
}

---

## EXECUTION FLOW

STEP 1 — RETRIEVE PARENT STORY
  Query task_memory:
    filter: { workflow_id: workflow_id,
              skill: "skill_gen_user_story" }
  Find story with id = us_id.
  If not found: STOP. Report missing parent story.

STEP 2 — DETERMINE NEXT ID
  Query task_memory for existing TK-NNN in workflow.
  Assign next sequential ID.

STEP 3 — GENERATE TICKET
  Format:
    ID:          TK-NNN
    Parent:      US-NNN
    Title:       {imperative verb + object, 5-10 words}
    Type:        {feature | bug | task | spike}
    Description: {what must be built/fixed/researched}
    Scope:       {specific files, modules, or components affected}
    Definition of Done: {measurable completion criteria}

STEP 4 — VALIDATE
  □ Title starts with imperative verb
  □ Parent US-NNN exists in task_memory
  □ Definition of Done is measurable

---

## OUTPUT FORMAT
{
  "agent":   "agent_pm",
  "task_id": "{task_id}",
  "skill":   "skill_gen_ticket",
  "status":  "completed | failed",
  "output": {
    "ticket": {
      "id":          "TK-NNN",
      "parent_us":   "US-NNN",
      "title":       "{str}",
      "type":        "{str}",
      "description": "{str}",
      "scope":       "{str}",
      "dod":         "{str}"
    }
  },
  "tokens":  {int},
  "error":   null | "{description}"
}
