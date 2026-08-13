#!/usr/bin/env python3
# journal_write.py — AIRON‑Cast (v3.0.0)
# Escritor unificado de memoria institucional.
# Tipos task/problem/adr/pattern/field → workspace/<project>/journal/entries/
#
# Usage:
#   python .agents/skills/journal-writer/scripts/journal_write.py \
#     --type task --project-slug landing-01 \
#     --payload '{"agent_name": "orchestrator", ...}'

import os
import sys
import json
import re
import argparse
from datetime import datetime, timezone


# ─── Campos requeridos por tipo ──────────────────────────────────────────────

REQUIRED_FIELDS = {
    "task": [
        "agent_name", "task_description", "skills_used",
        "duration_minutes", "output_artifacts", "notes"
    ],
    "problem": [
        "title", "context", "root_cause", "solution",
        "mitigation", "affected_components", "severity", "recurrence_risk"
    ],
    "adr": [
        "title", "context", "decision", "alternatives_considered",
        "reasoning", "consequences", "status"
    ],
    "pattern": [
        "title", "description", "evidence",
        "recommendation", "applies_to", "first_seen"
    ],
    "field": [
        "skill_or_agent", "project_context", "usage_description",
        "outcome", "friction_points", "suggested_improvement", "operator_rating"
    ],
}

VALID_TYPES = set(REQUIRED_FIELDS.keys())


# ─── Helpers ─────────────────────────────────────────────────────────────────

def find_project_root(start: str) -> str:
    current = os.path.abspath(start)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, "central_intelligence.db")):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start)


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r'[^\w\s-]', '', text)
    text = re.sub(r'[\s_]+', '-', text)
    text = re.sub(r'-+', '-', text)
    return text[:50].strip('-')


def render_template(template_path: str, payload: dict, timestamp: str) -> str:
    with open(template_path, "r", encoding="utf-8") as f:
        content = f.read()

    payload["timestamp"] = timestamp

    def replace_field(match):
        key = match.group(1).strip()
        value = payload.get(key)
        if value is None:
            return f"{{{{MISSING:{key}}}}}"
        if isinstance(value, list):
            return "\n".join(f"- {item}" for item in value)
        return str(value)

    return re.sub(r'\{\{(\w+)\}\}', replace_field, content)


def load_task_counter(journal_dir: str) -> dict:
    counter_path = os.path.join(journal_dir, ".task-counter.json")
    default = {
        "total_tasks": 0,
        "report_threshold": 10,
        "last_report_at": 0,
        "last_report_file": None
    }
    if not os.path.exists(counter_path):
        return default
    try:
        with open(counter_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        for k, v in default.items():
            data.setdefault(k, v)
        return data
    except Exception:
        return default


def save_task_counter(journal_dir: str, counter: dict) -> None:
    counter_path = os.path.join(journal_dir, ".task-counter.json")
    with open(counter_path, "w", encoding="utf-8") as f:
        json.dump(counter, f, indent=2, ensure_ascii=False)


def check_duplicate(entries_dir: str, entry_type: str, slug: str) -> str | None:
    if not os.path.exists(entries_dir):
        return None
    for fname in os.listdir(entries_dir):
        if slug in fname.lower() and fname.endswith(".md"):
            return fname
    return None


def next_adr_number(entries_dir: str) -> int:
    if not os.path.exists(entries_dir):
        return 1
    max_num = 0
    for fname in os.listdir(entries_dir):
        match = re.match(r'ADR-(\d+)', fname)
        if match:
            max_num = max(max_num, int(match.group(1)))
    return max_num + 1


# ─── Routing por tipo ────────────────────────────────────────────────────────

def resolve_output_path(
    entry_type: str,
    payload: dict,
    entries_dir: str,
    timestamp_str: str
) -> tuple[str, str]:
    date_str = timestamp_str[:8]

    if entry_type == "task":
        agent = slugify(payload.get("agent_name", "unknown"))
        filename = f"{timestamp_str}_task_{agent}.md"

    elif entry_type == "problem":
        title_slug = slugify(payload.get("title", "unknown"))
        filename = f"{timestamp_str}_problem_{title_slug}.md"

    elif entry_type == "adr":
        adr_num = next_adr_number(entries_dir)
        title_slug = slugify(payload.get("title", "decision"))
        filename = f"ADR-{adr_num:03d}-{title_slug}-{date_str}.md"

    elif entry_type == "pattern":
        title_slug = slugify(payload.get("title", "unknown"))
        filename = f"{timestamp_str}_pattern_{title_slug}.md"

    elif entry_type == "field":
        component = slugify(payload.get("skill_or_agent", "unknown"))
        filename = f"{timestamp_str}_field_{component}.md"

    else:
        filename = f"{timestamp_str}_{entry_type}_unknown.md"

    return entries_dir, filename


# ─── Escritor principal ──────────────────────────────────────────────────────

def write_entry(
    entry_type: str,
    payload: dict,
    project_slug: str,
    project_root: str,
    force: bool = False
) -> tuple[str, bool]:
    if entry_type not in VALID_TYPES:
        print(
            f"ERROR: Invalid entry type: '{entry_type}'. "
            f"Valid: {sorted(VALID_TYPES)}",
            file=sys.stderr
        )
        sys.exit(1)

    # Validar campos requeridos
    required = REQUIRED_FIELDS[entry_type]
    missing = [f for f in required if f not in payload or payload[f] == ""]
    if missing:
        print(
            f"ERROR: Missing required fields for type '{entry_type}': {missing}",
            file=sys.stderr
        )
        sys.exit(2)

    # Timestamp
    timestamp_str = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")

    # Directorio del journal del proyecto
    workspace_dir = os.path.join(project_root, "workspace", project_slug, "journal")
    entries_dir = os.path.join(workspace_dir, "entries")
    os.makedirs(entries_dir, exist_ok=True)

    # Resolver nombre de archivo
    output_dir, filename = resolve_output_path(entry_type, payload, entries_dir, timestamp_str)
    entry_path = os.path.join(output_dir, filename)

    # Verificar duplicados
    existing = check_duplicate(output_dir, entry_type, slugify(
        payload.get("agent_name", payload.get("title", ""))
    ))
    if existing and not force:
        print(
            f"WARNING: Similar entry exists: {existing}\n"
            "         Use --force to create an additional entry.",
            file=sys.stderr
        )
        sys.exit(4)

    # Renderizar template
    skill_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path = os.path.join(skill_dir, "assets", "templates", f"{entry_type}.md")

    if not os.path.exists(template_path):
        print(f"ERROR: Template not found: {template_path}", file=sys.stderr)
        sys.exit(3)

    rendered = render_template(template_path, payload, timestamp_str)

    unfilled = re.findall(r'\{\{MISSING:(\w+)\}\}', rendered)
    if unfilled:
        print(f"WARNING: Unfilled placeholders: {unfilled}", file=sys.stderr)

    # Escribir entrada
    with open(entry_path, "w", encoding="utf-8") as f:
        f.write(rendered)

    print(f"[Journal] [{entry_type.upper()}] {filename}")

    # Actualizar contador si es tipo task
    report_triggered = False
    if entry_type == "task":
        counter = load_task_counter(workspace_dir)
        counter["total_tasks"] += 1

        tasks_since_report = counter["total_tasks"] - counter["last_report_at"]
        if tasks_since_report >= counter["report_threshold"]:
            report_triggered = True
            print(
                f"[Journal] Report threshold reached "
                f"({tasks_since_report} tasks since last report). "
                f"Run journal_report.py to generate analysis."
            )
            counter["last_report_at"] = counter["total_tasks"]

        save_task_counter(workspace_dir, counter)

    return entry_path, report_triggered


# ─── CLI ─────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="AIRON‑Cast Journal — Write institutional memory entries."
    )
    parser.add_argument(
        "--type",
        required=True,
        choices=list(VALID_TYPES),
        help="Entry type: task | problem | adr | pattern | field"
    )
    parser.add_argument(
        "--payload",
        required=True,
        help="JSON string with entry fields."
    )
    parser.add_argument(
        "--project-slug",
        required=True,
        help="Project slug (e.g., landing-01)."
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Allow creating entry even if similar slug exists."
    )
    args = parser.parse_args()

    project_root = find_project_root(os.getcwd())

    try:
        payload = json.loads(args.payload)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in --payload: {e}", file=sys.stderr)
        sys.exit(1)

    entry_path, report_triggered = write_entry(
        entry_type=args.type,
        payload=payload,
        project_slug=args.project_slug,
        project_root=project_root,
        force=args.force
    )

    result = {
        "entry_path": entry_path,
        "report_triggered": report_triggered
    }
    print(json.dumps(result))
    sys.exit(0)


if __name__ == "__main__":
    main()