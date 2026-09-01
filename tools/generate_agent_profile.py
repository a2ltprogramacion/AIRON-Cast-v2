#!/usr/bin/env python3
"""
generate_agent_profile.py — AIRON‑Cast Agent Profile Generator.

Generates a new agent profile `.md` file with the standard AIRON‑Cast frontmatter
and mandatory sections. Used by meta_factory and agent-creator-pro.

Usage:
    python tools/generate_agent_profile.py \
        --name "backend_specialist" \
        --role "Backend Specialist" \
        --circle 3 \
        --scope restricted \
        --assigned-agents "orchestrator, requirements_architect" \
        --skills "django-patterns, database-architecture" \
        --upstream "orchestrator" \
        --downstream "qa_auditor" \
        --trigger "assigned_agent=backend_specialist, status=READY" \
        --handoff-success "Handoff to Orchestrator: Task [task_id] completed." \
        --handoff-failure "Handoff to Operador: Task [task_id] FAILED after 3 retries." \
        --output ./.agents/profiles/
"""

import argparse
import os
import sys
from datetime import datetime, timezone

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


def sanitize_filename(name: str) -> str:
    """Convert agent name to a valid filename."""
    clean = name.lower().strip()
    clean = ''.join(c if c.isalnum() or c in (' ', '_', '-') else '' for c in clean)
    clean = clean.replace(' ', '_')
    return clean


def parse_list(value: str) -> list:
    """Parse a comma-separated string into a list."""
    if not value:
        return []
    return [item.strip() for item in value.split(',') if item.strip()]


def generate_profile(args) -> str:
    """Generate the Markdown content for an agent profile."""
    now = datetime.now(timezone.utc).strftime('%Y-%m-%d')
    assigned = parse_list(args.assigned_agents)
    skills = parse_list(args.skills)
    skills_table = '\n'.join(f'| {s} | ... |' for s in skills) if skills else '| None | ... |'

    template = f"""---
role: {args.name}
circle: {args.circle}
assigned_agents: {assigned}
scope: {args.scope}
version: 1.0.0
last_used: {now}
---

# {args.role}

## 1. Identidad Central
**Rol:** {args.role}
**Objetivo:** {args.goal}

## 2. Jurisdicción
### Permitido
- ...

### Prohibido
- ...

## 3. Reglas Específicas
**R01:** ...
**R02:** ...

## 4. Skills Asignadas
| Skill | Propósito |
|-------|-----------|
{skills_table}

## 5. Flujo de Trabajo
### Workflow 1: ...
1. ...
2. ...
3. ...

### Escalation Protocol
1. Detect condition
2. Format [ALTO] diagnostic
3. Handoff to operator

## 6. Contrato de Salida
```json
{{
  "agent":   "{args.name}",
  "task_id": "...",
  "status":  "completed | failed",
  "output":  {{}},
  "tokens":  0,
  "error":   null
}}
```

## 7. Handoff
- **Upstream:** {args.upstream}
- **Downstream:** {args.downstream}
- **Trigger:** {args.trigger}
- **Success Phrase:** `"{args.handoff_success}"`
- **Failure Phrase:** `"{args.handoff_failure}"`
"""
    return template


def main():
    parser = argparse.ArgumentParser(
        description="AIRON‑Cast — Generate agent profile."
    )
    parser.add_argument("--name", required=True, help="Agent slug (kebab-case)")
    parser.add_argument("--role", required=True, help="Human-readable role title")
    parser.add_argument("--goal", default="...", help="Primary objective")
    parser.add_argument("--circle", type=int, choices=[0, 1, 2, 3], default=2, help="Authority circle (0-3)")
    parser.add_argument("--scope", choices=["restricted", "elevated"], default="restricted", help="Access scope")
    parser.add_argument("--assigned-agents", default="", help="Comma-separated list of assigned agents")
    parser.add_argument("--skills", default="", help="Comma-separated list of assigned skills")
    parser.add_argument("--upstream", default="orchestrator", help="Upstream agent(s)")
    parser.add_argument("--downstream", default="qa_auditor", help="Downstream agent(s)")
    parser.add_argument("--trigger", default="TASK_READY", help="Activation trigger condition")
    parser.add_argument("--handoff-success", default="Task completed.", help="Success handoff phrase")
    parser.add_argument("--handoff-failure", default="Task FAILED.", help="Failure handoff phrase")
    parser.add_argument("--output", required=True, help="Output directory for .md file")
    parser.add_argument("--force", action="store_true", help="Overwrite existing file")

    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    filename = sanitize_filename(args.name) + ".md"
    filepath = os.path.join(args.output, filename)

    if os.path.exists(filepath) and not args.force:
        print(f"ERROR: File already exists: {filepath}\n"
              "       Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    content = generate_profile(args)
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"[OK] Agent profile generated: {filepath}")
    print(f"[INFO] Timestamp: {datetime.now(timezone.utc).isoformat()}")
    sys.exit(0)


if __name__ == "__main__":
    main()