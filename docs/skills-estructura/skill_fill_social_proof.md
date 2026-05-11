# skill_fill_social_proof
# Agent: agent_writer
# Version: 1.0
# Pattern: Template

---

## DESCRIPTION
Replaces social proof placeholders in landing copy with
real client-provided data: testimonials and statistics.
Activate when: operator has provided real social proof data
and landing copy exists in task_memory with [PLACEHOLDER] markers.
Do NOT invent data. Do NOT activate without real client input.
Do NOT replace placeholders with other placeholders.

---

## INPUT CONTRACT
{
  "task_id":             "{str}",
  "workflow_id":         "{str}",
  "landing_artifact_id": "{str}",
  "social_proof": {
    "testimonials": [
      {
        "quote": "{real quote}",
        "name":  "{real name}",
        "role":  "{real role/company}"
      }
    ],
    "stats": [
      {
        "number": "{real number or percentage}",
        "label":  "{what it measures}"
      }
    ]
  }
}

---

## EXECUTION FLOW

STEP 1 — RETRIEVE LANDING COPY
  Query SQLite artifacts WHERE id = landing_artifact_id.
  Extract social_proof section from content.

STEP 2 — VALIDATE INPUT DATA
  For each testimonial verify:
    [] quote does not match pattern [...]
    [] name does not match pattern [NOMBRE]
    [] role does not match pattern [CARGO]
  For each stat verify:
    [] number does not match pattern [DATO]
  If any placeholder found in input: STOP.
  Report: real data required in all fields.

STEP 3 — REPLACE PLACEHOLDERS
  Replace [PLACEHOLDER] testimonials with provided data.
  Replace [DATO] stats with provided numbers.
  Preserve all other copy sections unchanged.

STEP 4 — VALIDATE RESULT
  Verify no [...] patterns remain in social_proof section.
  If any remain: report as incomplete fill.

---

## OUTPUT FORMAT
{
  "agent":   "agent_writer",
  "task_id": "{task_id}",
  "skill":   "skill_fill_social_proof",
  "status":  "completed | failed",
  "output": {
    "landing_artifact_id": "{str}",
    "social_proof_filled": true | false,
    "testimonials_count":  {int},
    "stats_count":         {int},
    "placeholders_remaining": {int},
    "content":             "{updated landing copy}"
  },
  "tokens":  {int},
  "error":   null | "{description}"
}
