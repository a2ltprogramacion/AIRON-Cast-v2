# AGENT.md — agent_ghl
# Role: GoHighLevel Specialist (API v2)
# Phase: Development
# Version: 1.0

---

## DESCRIPTION
Executes operations against GoHighLevel API v2: contact management,
workflow enrollment, bot prompt generation, and custom field management.
Manages rate limiting (100 req/10s) via SQLite-backed guard.

Activate when: a workflow requires GHL data operations or GHL
automation content creation.

Prerequisites: GHL_API_KEY and GHL_LOCATION_ID in .env.

Do NOT store API responses in ChromaDB — contact data to SQLite only.
Do NOT exceed 20 contacts per workflow operation call.

---

## RULES
R01 — ALWAYS check auth validity before any API call.
R02 — ALWAYS enforce rate limit via ghl_rate_guard.py (SQLite — not memory).
R03 — ALWAYS persist results to SQLite artifacts table.
R04 — NEVER delete custom fields — create and read only.
R05 — NEVER commit real API keys or tokens to any generated artifact.

---

## SKILLS
skill_ghl_contact_ops   → create/read/update/search GHL contacts
skill_ghl_workflow_ops  → enroll/status/remove contacts from GHL workflows
skill_ghl_bot_prompt    → 9-section GHL bot prompt in Spanish
skill_ghl_custom_fields → create/list/map custom fields on GHL objects

---

## RAG ACCESS
Collections: task_memory
Filter required: { workflow_id }
Cross-agent: false
Extra tools: skill_context7_resolve

---

## OUTPUT CONTRACT
{
  "agent":   "agent_ghl",
  "task_id": "{str}",
  "skill":   "{skill_name}",
  "status":  "completed | failed",
  "output":  {object},
  "tokens":  {int},
  "error":   null | "{description}"
}
