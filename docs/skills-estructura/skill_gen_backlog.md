# skill_gen_backlog
# Agent: agent_pm
# Version: 1.0
# Pattern: Deterministic (SKILL.md + scripts/)

---

## DESCRIPTION
Generates a prioritized project backlog by consolidating all user
stories, tickets, and acceptance criteria for a workflow phase.
Activate when: all US and TK artifacts for a phase are complete.
Do NOT activate mid-workflow — requires all stories and tickets complete.
Do NOT create new stories or tickets — consolidates only what exists.

---

## INPUT CONTRACT
{
  "task_id":     "{str}",
  "workflow_id": "{str}",
  "phase":       "{str}",
  "sort_by":     "priority | creation_order"
}

---

## EXECUTION FLOW

STEP 1 — COLLECT ARTIFACTS
  Call: python scripts/collect_artifacts.py
        --workflow_id "{workflow_id}"
        --types "user_story,ticket,acceptance_criteria"
  Returns: all PM artifacts for this workflow.

STEP 2 — VALIDATE COMPLETENESS
  For each user story verify:
    - Has at least 1 linked ticket
    - Has at least 1 linked acceptance criteria
  If missing: flag in output.incomplete_items. Continue.

STEP 3 — BUILD BACKLOG STRUCTURE
  Group by priority: high → medium → low
  Within each priority: sort by sort_by parameter.

STEP 4 — GENERATE SUMMARY
  Total counts: stories, tickets, criteria.
  Complexity score: high×3 + medium×2 + low×1

---

## SCRIPTS
### collect_artifacts.py
Queries SQLite artifacts for all PM artifacts in workflow.
EXIT 0: artifacts collected (JSON)
EXIT 1: no artifacts found
EXIT 2: SQLite unavailable

---

## OUTPUT FORMAT
{
  "agent":   "agent_pm",
  "task_id": "{task_id}",
  "skill":   "skill_gen_backlog",
  "status":  "completed | failed",
  "output": {
    "backlog_id": "BKL-{workflow_id}",
    "phase":      "{phase}",
    "content":    "{complete backlog document}",
    "summary": {
      "stories":    {int},
      "tickets":    {int},
      "criteria":   {int},
      "complexity": {int},
      "incomplete": {int}
    },
    "incomplete_items": ["{US-ID} — missing: {what}"]
  },
  "tokens":  {int},
  "error":   null | "{description}"
}
