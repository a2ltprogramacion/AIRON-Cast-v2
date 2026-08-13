#!/usr/bin/env python3
"""
db_ops.py — AIRON‑Cast Database Operations CLI

Provides common database operations for the Operator:
- List projects and their status
- Inspect tasks, checkpoints, and execution logs
- Force task status changes
- View model usage statistics

Usage:
    python tools/db_ops.py projects
    python tools/db_ops.py tasks --project-slug landing-01
    python tools/db_ops.py checkpoints --project-slug landing-01
    python tools/db_ops.py force-status --task-id 5 --status READY
    python tools/db_ops.py model-usage --agent-name orchestrator
"""

import os
import sys
import sqlite3
import argparse
from datetime import datetime, timezone


DB_FILENAME = "central_intelligence.db"


def find_project_root(start: str) -> str:
    current = os.path.abspath(start)
    for _ in range(10):
        if os.path.exists(os.path.join(current, "AGENTS.md")):
            return current
        if os.path.exists(os.path.join(current, DB_FILENAME)):
            return current
        parent = os.path.dirname(current)
        if parent == current:
            break
        current = parent
    return os.path.abspath(start)


def get_db_path() -> str:
    root = find_project_root(os.getcwd())
    return os.path.join(root, DB_FILENAME)


def get_connection():
    db_path = get_db_path()
    if not os.path.exists(db_path):
        print(f"ERROR: Database not found: {db_path}", file=sys.stderr)
        sys.exit(1)
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def cmd_projects(args):
    conn = get_connection()
    rows = conn.execute("SELECT slug, name, status, priority, updated_at FROM projects ORDER BY priority DESC").fetchall()
    if not rows:
        print("No projects found.")
        return
    print(f"{'Slug':<25} {'Name':<30} {'Status':<12} {'Priority':<10} {'Updated'}")
    print("-" * 100)
    for r in rows:
        print(f"{r['slug']:<25} {r['name']:<30} {r['status']:<12} {r['priority']:<10} {r['updated_at']}")
    conn.close()


def cmd_tasks(args):
    conn = get_connection()
    if args.project_slug:
        project = conn.execute("SELECT id FROM projects WHERE slug = ?", (args.project_slug,)).fetchone()
        if not project:
            print(f"ERROR: Project not found: {args.project_slug}", file=sys.stderr)
            sys.exit(1)
        rows = conn.execute(
            "SELECT id, title, assigned_agent, status, priority, retry_count FROM tasks WHERE project_id = ? ORDER BY priority DESC, created_at ASC",
            (project["id"],)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT t.id, t.title, t.assigned_agent, t.status, t.priority, t.retry_count, p.slug FROM tasks t JOIN projects p ON p.id = t.project_id ORDER BY p.slug, t.priority DESC"
        ).fetchall()

    if not rows:
        print("No tasks found.")
        return
    print(f"{'ID':<5} {'Slug/Project':<25} {'Title':<35} {'Agent':<22} {'Status':<14} {'Prio':<5} {'Retries'}")
    print("-" * 120)
    for r in rows:
        slug = r["slug"] if "slug" in r.keys() else args.project_slug
        print(f"{r['id']:<5} {slug:<25} {r['title'][:33]:<35} {r['assigned_agent'] or '-':<22} {r['status']:<14} {r['priority']:<5} {r['retry_count']}")
    conn.close()


def cmd_checkpoints(args):
    conn = get_connection()
    if args.project_slug:
        project = conn.execute("SELECT id FROM projects WHERE slug = ?", (args.project_slug,)).fetchone()
        if not project:
            print(f"ERROR: Project not found: {args.project_slug}", file=sys.stderr)
            sys.exit(1)
        rows = conn.execute(
            "SELECT id, agent_name, step_number, step_description, created_at FROM checkpoints WHERE project_id = ? ORDER BY created_at DESC LIMIT ?",
            (project["id"], args.limit)
        ).fetchall()
    else:
        rows = conn.execute(
            "SELECT c.id, c.agent_name, c.step_number, c.step_description, c.created_at, p.slug FROM checkpoints c JOIN projects p ON p.id = c.project_id ORDER BY c.created_at DESC LIMIT ?",
            (args.limit,)
        ).fetchall()

    if not rows:
        print("No checkpoints found.")
        return
    print(f"{'ID':<5} {'Slug':<25} {'Agent':<22} {'Step':<6} {'Description':<40} {'Created'}")
    print("-" * 120)
    for r in rows:
        slug = r["slug"] if "slug" in r.keys() else args.project_slug
        desc = (r["step_description"] or "")[:38]
        print(f"{r['id']:<5} {slug:<25} {r['agent_name']:<22} {r['step_number']:<6} {desc:<40} {r['created_at']}")
    conn.close()


def cmd_force_status(args):
    conn = get_connection()
    task = conn.execute("SELECT id, title, status FROM tasks WHERE id = ?", (args.task_id,)).fetchone()
    if not task:
        print(f"ERROR: Task not found: {args.task_id}", file=sys.stderr)
        sys.exit(1)

    print(f"Task {task['id']}: '{task['title']}'")
    print(f"Current status: {task['status']} → New status: {args.status}")
    print("Proceed? (y/N): ", end="")
    confirmation = input().strip().lower()
    if confirmation != "y":
        print("Aborted.")
        conn.close()
        return

    conn.execute(
        "UPDATE tasks SET status = ?, updated_at = ? WHERE id = ?",
        (args.status, datetime.now(timezone.utc).isoformat(), args.task_id)
    )
    conn.commit()
    print(f"Task {args.task_id} status updated to: {args.status}")
    conn.close()


def cmd_model_usage(args):
    conn = get_connection()
    query = "SELECT agent_name, model_name, model_role, tokens_input, tokens_output, latency_ms, success, created_at FROM model_usage WHERE 1=1"
    params = []
    if args.agent_name:
        query += " AND agent_name = ?"
        params.append(args.agent_name)
    if args.project_slug:
        query += " AND project_id = (SELECT id FROM projects WHERE slug = ?)"
        params.append(args.project_slug)
    query += " ORDER BY created_at DESC LIMIT ?"
    params.append(args.limit)

    rows = conn.execute(query, params).fetchall()
    if not rows:
        print("No model usage records found.")
        return
    print(f"{'Agent':<22} {'Model':<30} {'Role':<10} {'Input':<8} {'Output':<8} {'Latency':<8} {'OK':<4} {'Created'}")
    print("-" * 110)
    for r in rows:
        print(f"{r['agent_name']:<22} {r['model_name']:<30} {r['model_role']:<10} {r['tokens_input']:<8} {r['tokens_output']:<8} {r['latency_ms'] or '-':<8} {r['success']:<4} {r['created_at']}")
    conn.close()


def main():
    parser = argparse.ArgumentParser(description="AIRON‑Cast Database Operations CLI")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # projects
    subparsers.add_parser("projects", help="List all projects")

    # tasks
    p_tasks = subparsers.add_parser("tasks", help="List tasks")
    p_tasks.add_argument("--project-slug", help="Filter by project slug")

    # checkpoints
    p_checkpoints = subparsers.add_parser("checkpoints", help="List checkpoints")
    p_checkpoints.add_argument("--project-slug", help="Filter by project slug")
    p_checkpoints.add_argument("--limit", type=int, default=20, help="Max rows (default: 20)")

    # force-status
    p_force = subparsers.add_parser("force-status", help="Force task status change")
    p_force.add_argument("--task-id", type=int, required=True, help="Task ID")
    p_force.add_argument("--status", required=True, help="New status")

    # model-usage
    p_model = subparsers.add_parser("model-usage", help="View model usage records")
    p_model.add_argument("--agent-name", help="Filter by agent")
    p_model.add_argument("--project-slug", help="Filter by project")
    p_model.add_argument("--limit", type=int, default=20, help="Max rows (default: 20)")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    commands = {
        "projects": cmd_projects,
        "tasks": cmd_tasks,
        "checkpoints": cmd_checkpoints,
        "force-status": cmd_force_status,
        "model-usage": cmd_model_usage,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()