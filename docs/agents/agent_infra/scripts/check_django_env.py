#!/usr/bin/env python3
# agents/agent_infra/scripts/check_django_env.py
# Forge Stack Engine — Django environment validator
# Version: 1.0
#
# Validates that the Django project directory is safe to run
# a development server. Hard-blocks if production DB is detected.
#
# Called by skill_manage_devserver STEP 1.
#
# Exit codes:
#   0 — environment is safe (development or test)
#   1 — BLOCKED: production DB detected or unsafe configuration
#   2 — ERROR: project_dir not found or missing settings

import argparse
import os
import sys
from pathlib import Path


# ── Production signals ────────────────────────────────────────────────────────
# Any of these patterns in DATABASE_URL or DB_HOST indicates production.
# Conservative list — false positives are safer than false negatives.

PRODUCTION_HOST_PATTERNS = [
    "rds.amazonaws.com",
    "postgres.render.com",
    "db.supabase.co",
    "neon.tech",
    "cockroachlabs.cloud",
    "elephantsql.com",
    "aiven.io",
    "planetscale.com",
]

PRODUCTION_ENV_SIGNALS = [
    ("DEBUG",           "False"),   # Django production signal
    ("ENVIRONMENT",     "production"),
    ("ENVIRONMENT",     "prod"),
    ("DJANGO_ENV",      "production"),
    ("DJANGO_ENV",      "prod"),
    ("APP_ENV",         "production"),
    ("APP_ENV",         "prod"),
]


def load_env_file(project_dir: Path) -> dict:
    """
    Loads .env file from project_dir into a dict.
    Returns empty dict if .env does not exist.
    Does NOT set os.environ — read-only inspection.
    """
    env_file = project_dir / ".env"
    if not env_file.exists():
        return {}
    env = {}
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, _, value = line.partition("=")
        env[key.strip()] = value.strip().strip('"').strip("'")
    return env


def check_production_db(env: dict) -> tuple[bool, str]:
    """
    Returns (is_production, reason).
    Checks DATABASE_URL and individual DB_* variables.
    """
    database_url = env.get("DATABASE_URL", "").lower()

    for pattern in PRODUCTION_HOST_PATTERNS:
        if pattern in database_url:
            return True, f"DATABASE_URL contains production host: {pattern}"

    db_host = env.get("DB_HOST", env.get("PGHOST", "")).lower()
    for pattern in PRODUCTION_HOST_PATTERNS:
        if pattern in db_host:
            return True, f"DB_HOST contains production host: {pattern}"

    return False, ""


def check_production_signals(env: dict) -> tuple[bool, str]:
    """
    Returns (is_production, reason).
    Checks environment variable signals.
    """
    # Merge .env with actual os.environ — os.environ takes precedence
    effective = {**env, **{k: v for k, v in os.environ.items()}}

    for key, prod_value in PRODUCTION_ENV_SIGNALS:
        actual = effective.get(key, "").lower().strip()
        if actual == prod_value.lower():
            return True, f"{key}={actual} signals production environment"

    return False, ""


def check_sqlite_only(env: dict) -> bool:
    """
    Returns True if the project uses SQLite (always safe for dev server).
    Forge Stack Engine projects use SQLite internally — not for the project DB.
    This is a fast-pass for automation projects.
    """
    database_url = env.get("DATABASE_URL", "").lower()
    return "sqlite" in database_url or database_url == ""


def validate_project_dir(project_dir: Path) -> tuple[bool, str]:
    """
    Returns (is_valid, error_message).
    Checks that project_dir contains a Django manage.py.
    """
    if not project_dir.exists():
        return False, f"project_dir not found: {project_dir}"
    if not project_dir.is_dir():
        return False, f"project_dir is not a directory: {project_dir}"
    if not (project_dir / "manage.py").exists():
        return False, f"manage.py not found in: {project_dir}"
    return True, ""


def main():
    parser = argparse.ArgumentParser(
        description="Forge Stack Engine — Django environment validator"
    )
    parser.add_argument(
        "--project_dir", required=True,
        help="Path to Django project root (must contain manage.py)"
    )
    parser.add_argument(
        "--verbose", action="store_true",
        help="Print detailed check results"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    # Check 1 — project directory exists and has manage.py
    valid, err = validate_project_dir(project_dir)
    if not valid:
        print(f"ERROR: {err}", file=sys.stderr)
        sys.exit(2)

    # Load .env
    env = load_env_file(project_dir)

    if args.verbose:
        print(f"[ check_django_env ]")
        print(f"  project_dir: {project_dir}")
        print(f"  .env loaded: {len(env)} variables")

    # Fast-pass for SQLite projects
    if check_sqlite_only(env):
        if args.verbose:
            print("  DB type: SQLite — safe for development server")
            print("  Result: SAFE\n")
        sys.exit(0)

    # Check 2 — production DB host
    is_prod_db, reason_db = check_production_db(env)
    if is_prod_db:
        print(f"BLOCKED: {reason_db}", file=sys.stderr)
        print("Development server is not safe to run against production DB.",
              file=sys.stderr)
        sys.exit(1)

    # Check 3 — environment variable signals
    is_prod_env, reason_env = check_production_signals(env)
    if is_prod_env:
        print(f"BLOCKED: {reason_env}", file=sys.stderr)
        print("Development server is not safe in production environment.",
              file=sys.stderr)
        sys.exit(1)

    if args.verbose:
        print("  DB type: PostgreSQL (non-production host)")
        print("  Environment signals: none detected")
        print("  Result: SAFE\n")

    sys.exit(0)


if __name__ == "__main__":
    main()
