# skill_review_architecture
# Agent: agent_reviewer
# Version: 1.1
# Pattern: Deterministic

---

## DESCRIPTION
Reviews architecture documents, database schemas, API contracts, and
tech stack definitions for structural consistency, completeness, and
compliance with A2LT standards.

Produces structured findings with APPROVED / APPROVED_MINOR / REJECTED
verdict. Never rewrites or fixes artifacts — reports findings only.

Activate when: agent_architect or agent_pm has produced a design artifact
that requires validation before development begins.

Supported artifact types: architecture | schema | api_contract |
tech_stack | backlog

Do NOT modify artifacts under any circumstance.
Do NOT approve artifacts with CRITICAL findings.
Do NOT generate code, copy, or replacement content.

---

## INPUT CONTRACT
{
  "task_id":       "{str}",
  "workflow_id":   "{str}",
  "artifact_id":   "{str}",
  "artifact_type": "architecture | schema | api_contract | tech_stack | backlog",
  "scope":         "{str} — what specifically to review"
}

---

## EXECUTION FLOW

STEP 1 — RETRIEVE ARTIFACT
  Query SQLite artifacts WHERE id = artifact_id.
  If not found: STOP. Return failed with error "artifact not found".

  Query task_memory (cross-agent, no agent filter):
    filter: { workflow_id: workflow_id }
  Retrieve all prior artifacts from this workflow for context.

STEP 2 — LOAD REVIEW CRITERIA BY TYPE

  If artifact_type = "backlog":
    Criteria to check:
      □ Every user story has at least 1 linked ticket
      □ Every ticket has at least 2 positive + 1 negative AC
      □ All IDs follow format: US-NNN, TK-NNN, AC-NNN
      □ Priority assigned to each story (high | medium | low)
      □ No story describes HOW to build — only WHAT is needed
      □ No ticket references a technology or framework directly

  If artifact_type = "architecture":
    Criteria to check:
      □ All layers declared (presentation, application, domain, infra)
      □ Tech choices match A2LT standard stack
      □ No SQLite as project DB (H001 — hard conflict)
      □ No Astro SSR + Decap CMS combination (H002 — hard conflict)
      □ Dependencies between layers declared explicitly
      □ Auth strategy declared (JWT vs session)

  If artifact_type = "schema":
    Criteria to check:
      □ Every entity has created_at and updated_at unless explicitly excluded
      □ Every FK has corresponding index declared
      □ No circular FK dependencies without DEFERRABLE resolution
      □ All field types valid for PostgreSQL 16
      □ Self-referential FKs declared as NULLABLE DEFERRABLE
      □ No many-to-many without explicit junction table

  If artifact_type = "api_contract":
    Criteria to check:
      □ Every endpoint has method, path, auth, request schema, response schema
      □ Error codes declared (400, 401, 403, 404, 422, 500 minimum)
      □ Pagination strategy declared for list endpoints
      □ No endpoint exposes internal IDs without justification
      □ Auth method consistent across all endpoints (JWT or none)

  If artifact_type = "tech_stack":
    Criteria to check:
      □ All versions pinned (no "latest")
      □ Versions match stack_versions.md reference
      □ No known incompatibilities from compatibility.md
      □ requirements_skeleton present and complete
      □ Node version declared if frontend present

STEP 3 — CLASSIFY FINDINGS

  For each failed criterion assign severity:

  CRITICAL — blocks development, fundamental flaw:
    - Hard conflicts (H001, H002, H003, H004)
    - Missing auth strategy on API contract
    - Circular FKs without resolution
    - User stories describing implementation details

  MAJOR — significant gap, requires revision before proceeding:
    - Missing indexes on FKs
    - Endpoints without error codes
    - Tech versions unpinned
    - Stories without tickets or tickets without AC

  MINOR — improvement recommended, does not block:
    - Naming conventions inconsistent
    - Missing optional fields (pagination, OG tags)
    - Documentation gaps

STEP 4 — DETERMINE VERDICT

  APPROVED:        0 CRITICAL + 0 MAJOR findings
  APPROVED_MINOR:  0 CRITICAL + 1 or more MINOR findings only
  REJECTED:        1 or more CRITICAL findings (regardless of MAJOR/MINOR)
                   OR 3 or more MAJOR findings

  If REJECTED:
    assigned_back_to = originating agent name
    (agent_pm for backlog | agent_architect for architecture/schema/api/stack)

STEP 5 — BUILD OUTPUT
  Compile findings list with severity, location, description.
  Write brief summary narrative.
  Return structured JSON.

---

## OUTPUT FORMAT
{
  "agent":   "agent_reviewer",
  "task_id": "{task_id}",
  "skill":   "skill_review_architecture",
  "status":  "completed | failed",
  "output": {
    "artifact_id":   "{str}",
    "artifact_type": "{str}",
    "verdict":       "APPROVED | APPROVED_MINOR | REJECTED",
    "assigned_back_to": "{agent_name} | null",
    "findings": [
      {
        "finding_id":  "F001",
        "severity":    "CRITICAL | MAJOR | MINOR",
        "criterion":   "{which check failed}",
        "location":    "{section, field, or entity name}",
        "description": "{what is wrong}",
        "action":      "{what the originating agent must fix}"
      }
    ],
    "summary":          "{2-3 sentence narrative of review outcome}",
    "criteria_checked": {int},
    "criteria_passed":  {int}
  },
  "tokens":  {int},
  "error":   null | "{description}"
}
