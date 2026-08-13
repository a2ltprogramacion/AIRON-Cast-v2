---
name: yaml-validator
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Validates YAML files against JSON schema. Returns detailed error reports
  with line numbers and suggestions. Essential for validating frontmatter
  in SKILL.md and agent profiles before deployment.
  Trigger phrases: "validate yaml", "yaml check", "schema validation",
  "frontmatter validate", "metadata check".
  Do NOT activate for simple lint checking without schema.
triggers:
  primary: ["validate yaml", "yaml check", "schema validation"]
  secondary: ["frontmatter validate", "metadata check"]
  context: ["quality assurance", "pre-deployment", "AIRON‑Cast validation"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - meta_factory
last_used: 2026-06-03
scope: restricted
---

# YAML Validator — AIRON‑Cast

This skill provides schema-based YAML validation for all AIRON‑Cast
components: skills (`SKILL.md`), agents (`.md` profiles), and configuration
files. It ensures every component complies with the mandatory frontmatter
standard before deployment.

---

## 1. When to Use This Skill

- Validating AIRON‑Cast component frontmatter (SKILL.md, agent profiles)
  against the ecosystem schema
- Pre-deployment audits to catch YAML errors early
- CI/CD pipeline validation before committing to manifest
- Verifying `.env.example` structure
- **Do NOT use when:** YAML is already validated by IDE; for simple lint
  checking without schema

---

## 2. How to Use It

### CLI Invocation

```bash
python scripts/yaml_validator.py --filepath "<path-to-file>" [--strict-mode]
```

### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `--filepath` | string | Yes | Path to the YAML file to validate |
| `--schema-path` | string | No | Path to a custom JSON Schema. If omitted, uses the AIRON‑Cast default schema |
| `--strict-mode` | bool | No | If present, treats warnings as errors |
| `--output-format` | string | No | `json` (default), `text`, or `markdown` |

### Example Success Response

```json
{
  "valid": true,
  "errors": [],
  "warnings": [
    {
      "line": 8,
      "field": "tier",
      "message": "Optional field missing. Assumes tier=all if not specified."
    }
  ],
  "metadata": {
    "name": "yaml-validator",
    "version": "1.0.0",
    "type": "utility"
  }
}
```

### Example Error Response

```json
{
  "valid": false,
  "errors": [
    {
      "line": 3,
      "field": "version",
      "message": "Invalid SemVer. Expected format: MAJOR.MINOR.PATCH",
      "suggestion": "Change '1.0' to '1.0.0'"
    },
    {
      "line": 25,
      "field": "dependencies[0].version",
      "message": "Version range invalid.",
      "suggestion": "Check §3 for proper SemVer range syntax"
    }
  ],
  "warnings": [],
  "metadata": null
}
```

---

## 3. Decision Trees

### Tree 1: What to Do If There Are Errors

```
┌─ Critical errors (malformed YAML)?
│  └─ Yes → Fix YAML syntax
│  └─ No → Continue
├─ Schema errors (missing field)?
│  └─ Yes → Add the required field
│  └─ No → Continue
├─ Warnings (incomplete information)?
│  └─ strict-mode ON → Treat as error
│  └─ strict-mode OFF → Log but don't block
```

### Tree 2: When to Escalate

```
┌─ Custom schema required?
│  └─ Yes → Provide --schema-path to validator
│  └─ No → Use AIRON‑Cast default
├─ Error not in suggestions list?
│  └─ Yes → Escalate to operator with full JSON output
```

---

## 4. AIRON‑Cast Default Schema

The default schema validates the mandatory frontmatter fields required
by the ecosystem:

- `name` — kebab-case, alphanumeric and hyphens
- `version` — SemVer X.Y.Z
- `type` — backend | frontend | integration | utility
- `assigned_agents` — list of agent roles
- `scope` — restricted | elevated
- `description` — minimum 50 characters
- `triggers` — object with primary, secondary, context keys
- `dependencies` — array of dependency objects

---

## 5. Script: `scripts/yaml_validator.py`

The script is located in `scripts/` within this skill directory and
has been migrated from the Legacy ecosystem and adapted for AIRON‑Cast.

### Usage

```bash
python .agents/skills/yaml-validator/scripts/yaml_validator.py \
  --filepath ./.agents/skills/example/SKILL.md \
  --strict-mode
```

### Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Validation passed (no errors, or only warnings if not strict) |
| 1 | Validation failed (errors found) |

### Dependencies

- Python 3.10+
- `pyyaml` (>=6.0)
- `jsonschema` (>=4.17)

If dependencies are missing, the script outputs a JSON error and exits.
Install them with:

```bash
pip install pyyaml jsonschema
```

---

## 6. Limitations and Warnings

- **Security:** The script reads files from disk only. It does not make
  network requests.
- **Performance:** Suitable for files up to 10 MB. Larger files may
  require streaming parsers.
- **Custom schemas:** Must be valid JSON Schema draft-07. The script
  validates the schema itself before applying it.

---

## 🔗 AIRON‑Cast Integration

This skill is consumed by:
- `meta_factory` — to validate frontmatter before deploying new agents or skills.
- `skill-creator-pro` — as part of the pre-deployment validation pipeline.

Generated validation reports can be stored in `workspace/<slug>/reports/`
for project-level audits.