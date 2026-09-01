#!/usr/bin/env python3
"""
validate_agent_profile.py — AIRON‑Cast Agent Profile Validator.

Validates an agent profile `.md` file against the AIRON‑Cast standard.
Checks frontmatter YAML and mandatory sections.

Usage:
    python tools/validate_agent_profile.py ./.agents/profiles/orchestrator.md
    python tools/validate_agent_profile.py --dir ./.agents/profiles/
"""

import argparse
import os
import re
import sys
import yaml

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass


# Mandatory frontmatter fields
REQUIRED_FRONTMATTER = ["role", "circle", "scope", "version"]
VALID_SCOPES = {"restricted", "elevated"}
VALID_CIRCLES = {0, 1, 2, 3}


def extract_frontmatter(content: str) -> dict | None:
    """Extract YAML frontmatter between --- markers."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def validate_frontmatter(fm: dict) -> list[str]:
    """Validate frontmatter fields, return list of errors."""
    errors = []
    if not isinstance(fm, dict):
        return ["Frontmatter is not a valid YAML dictionary."]

    for field in REQUIRED_FRONTMATTER:
        if field not in fm:
            errors.append(f"Missing required frontmatter field: '{field}'")

    if "circle" in fm and fm["circle"] not in VALID_CIRCLES:
        errors.append(f"'circle' must be one of {VALID_CIRCLES}, got: {fm['circle']}")

    if "scope" in fm and fm["scope"] not in VALID_SCOPES:
        errors.append(f"'scope' must be one of {VALID_SCOPES}, got: {fm['scope']}")

    if "version" in fm and not re.match(r'^\d+\.\d+\.\d+$', str(fm["version"])):
        errors.append(f"'version' must be SemVer X.Y.Z, got: {fm['version']}")

    return errors


def validate_sections(content: str) -> list[str]:
    """Check for mandatory sections in the profile body."""
    errors = []
    sections = [
        (r'##\s+1\.\s+Identidad Central', "1. Identidad Central"),
        (r'##\s+2\.\s+Jurisdicción', "2. Jurisdicción"),
        (r'##\s+\d+\.\s+Skills Asignadas', "Skills Asignadas"),
        (r'##\s+\d+\.\s+Flujo de Trabajo', "Flujo de Trabajo"),
        (r'##\s+\d+\.\s+Contrato de Salida', "Contrato de Salida"),
    ]
    for pattern, name in sections:
        if not re.search(pattern, content):
            errors.append(f"Missing mandatory section: '{name}'")
    return errors


def validate_file(filepath: str) -> tuple[list[str], list[str]]:
    """Validate a single agent profile. Returns (errors, warnings)."""
    errors = []
    warnings = []

    if not os.path.isfile(filepath):
        return [f"File not found: {filepath}"], []

    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()

    # Frontmatter
    fm = extract_frontmatter(content)
    if fm is None:
        errors.append("Missing or invalid YAML frontmatter.")
    else:
        errors.extend(validate_frontmatter(fm))

    # Sections
    errors.extend(validate_sections(content))

    # Length check
    lines = content.split('\n')
    if len(lines) < 15:
        errors.append("Profile too short (less than 15 lines). Likely incomplete.")
    elif len(lines) > 300:
        warnings.append(f"Profile exceeds 300 lines ({len(lines)} lines). Consider moving details to references/.")

    return errors, warnings


def main():
    parser = argparse.ArgumentParser(
        description="AIRON‑Cast — Validate agent profile."
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--path", help="Path to a single .md file")
    group.add_argument("--dir", help="Directory with .md files to validate recursively")
    args = parser.parse_args()

    if args.path:
        files = [args.path]
    else:
        files = []
        for root, _, filenames in os.walk(args.dir):
            for fname in filenames:
                if fname.endswith(".md"):
                    files.append(os.path.join(root, fname))

    total_errors = 0
    for fpath in sorted(files):
        errors, warnings = validate_file(fpath)
        status = "✅ VALID" if not errors else "❌ FAILED"
        print(f"\n{status}  {fpath}")
        for e in errors:
            print(f"  ❌ {e}")
        for w in warnings:
            print(f"  ⚠️  {w}")
        if errors:
            total_errors += 1

    print(f"\n{'='*60}")
    print(f"SUMMARY: {len(files)} file(s) checked, {total_errors} with fatal errors.")
    print(f"{'='*60}")
    sys.exit(1 if total_errors > 0 else 0)


if __name__ == "__main__":
    main()