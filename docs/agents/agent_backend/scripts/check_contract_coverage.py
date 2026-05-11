#!/usr/bin/env python3
# agents/agent_backend/scripts/check_contract_coverage.py
# La Forja — Verify API endpoints are implemented
# Version: 1.0 — BL.017
# Reads from SQLite artifacts, not disk paths

import argparse
import json
import sys
import sqlite3


def get_implemented_endpoints(workflow_id, db_path):
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    row = conn.execute(
        """SELECT a.content FROM artifacts a
           JOIN tasks t ON a.task_id = t.id
           WHERE a.workflow_id=? AND t.skill='skill_gen_django_app'
           ORDER BY a.fecha DESC LIMIT 1""",
        (workflow_id,)
    ).fetchone()
    conn.close()
    if not row: return []
    try:
        content = json.loads(row["content"])
        return content.get("endpoints_covered", [])
    except Exception:
        return []


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--workflow_id",    required=True)
    parser.add_argument("--app_name",       required=True)
    parser.add_argument("--endpoints_json", required=True)
    parser.add_argument("--db_path",        default="./db/forge.db")
    args = parser.parse_args()

    required    = json.loads(args.endpoints_json)
    implemented = get_implemented_endpoints(args.workflow_id, args.db_path)
    gaps        = [e for e in required if e not in implemented]

    if gaps:
        print(f"UNCOVERED endpoints ({len(gaps)}):")
        for g in gaps: print(f"  - {g}")
        sys.exit(1)

    print(f"OK: all {len(required)} endpoints covered")
    sys.exit(0)


if __name__ == "__main__":
    main()
