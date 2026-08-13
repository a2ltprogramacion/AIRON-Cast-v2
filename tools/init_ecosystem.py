#!/usr/bin/env python3
"""
init_ecosystem.py — AIRON‑Cast Ecosystem Initializer

Creates and initializes central_intelligence.db by executing
the complete schema from core/airon_cast_schema.sql.

Usage:
    python tools/init_ecosystem.py
"""

import sqlite3
import sys
from pathlib import Path

SCHEMA_FILE = Path(__file__).resolve().parent.parent / "core" / "airon_cast_schema.sql"
DB_PATH = Path(__file__).resolve().parent.parent / "central_intelligence.db"


def main():
    if not SCHEMA_FILE.exists():
        print(f"ERROR: Schema file not found: {SCHEMA_FILE}", file=sys.stderr)
        sys.exit(1)

    schema = SCHEMA_FILE.read_text(encoding="utf-8")

    if DB_PATH.exists():
        print(f"[INFO] Database already exists: {DB_PATH}")
        resp = input("Overwrite? (y/N): ").strip().lower()
        if resp != "y":
            print("Aborted.")
            sys.exit(0)
        DB_PATH.unlink()

    conn = sqlite3.connect(str(DB_PATH))
    try:
        conn.executescript(schema)
        conn.commit()
    except sqlite3.Error as e:
        print(f"ERROR: Failed to execute schema: {e}", file=sys.stderr)
        conn.close()
        DB_PATH.unlink(missing_ok=True)
        sys.exit(1)

    # Verificar que las tablas principales existen
    tables = conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table' AND name NOT LIKE 'sqlite_%' ORDER BY name"
    ).fetchall()
    conn.close()

    print(f"[OK] Database initialized: {DB_PATH}")
    print(f"[INFO] Tables created: {', '.join(t[0] for t in tables)}")
    print("[INFO] Ecosystem ready.")


if __name__ == "__main__":
    main()