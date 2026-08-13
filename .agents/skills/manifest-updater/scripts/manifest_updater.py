#!/usr/bin/env python3
# manifest_updater.py — AIRON‑Cast
# Atomic manifest management: init, add, update, deprecate, validate.
# All writes are atomic: read → modify in memory → validate → write.
# Usage: python manifest_updater.py --operation <op> --kind <kind> [options]

import os
import sys
import json
import re
import argparse
import shutil
from datetime import datetime, timezone
from collections import defaultdict


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

VALID_OPERATIONS = {"init", "add", "update", "deprecate", "validate"}
VALID_KINDS      = {"agent", "skill"}
VALID_STATUSES   = {"active", "draft", "deprecated", "pending_validation"}
VALID_TYPES      = {"backend", "frontend", "integration", "utility"}
VALID_SCOPES     = {"restricted", "elevated"}

SEMVER_RE = re.compile(r'^\d+\.\d+\.\d+$')
KEBAB_RE  = re.compile(r'^[a-z0-9][a-z0-9-]*[a-z0-9]$')

MANIFEST_PATH = "manifest.json"


# ---------------------------------------------------------------------------
# Project root resolution
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Manifest I/O
# ---------------------------------------------------------------------------

def load_manifest(root: str) -> dict:
    path = os.path.join(root, MANIFEST_PATH)
    if not os.path.exists(path):
        print(f"ERROR: Manifest not found: {path}\n"
              "       Run --operation init first.", file=sys.stderr)
        sys.exit(7)
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"ERROR: Invalid JSON in {path}: {e}", file=sys.stderr)
        sys.exit(3)


def save_manifest(root: str, data: dict, dry_run: bool = False) -> None:
    path = os.path.join(root, MANIFEST_PATH)
    data["last_updated"] = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    if dry_run:
        print("\n[DRY RUN] Changes that would be applied:")
        print(json.dumps(data, indent=2, ensure_ascii=False))
        return

    tmp_path = path + ".tmp"
    backup_path = path + ".bak"

    try:
        if os.path.exists(path):
            shutil.copy2(path, backup_path)

        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
            f.write("\n")

        os.replace(tmp_path, path)
        print(f"[Manifest] Saved: {path}")

    except Exception as e:
        if os.path.exists(backup_path):
            shutil.copy2(backup_path, path)
        if os.path.exists(tmp_path):
            os.remove(tmp_path)
        print(f"ERROR: Failed to write {path}: {e}", file=sys.stderr)
        sys.exit(3)


def init_manifest(root: str, dry_run: bool = False) -> None:
    path = os.path.join(root, MANIFEST_PATH)
    if os.path.exists(path) and not dry_run:
        print(f"ERROR: Manifest already exists: {path}\n"
              "       Use --operation validate to audit it.", file=sys.stderr)
        sys.exit(2)

    data = {
        "ecosystem": "AIRON-Cast",
        "version": "1.0.0",
        "last_updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "agents": [],
        "skills": []
    }

    if not dry_run:
        os.makedirs(os.path.dirname(path) if os.path.dirname(path) else ".", exist_ok=True)

    save_manifest(root, data, dry_run)
    if not dry_run:
        print(f"[Manifest] Initialized: {path}")


# ---------------------------------------------------------------------------
# Component validation
# ---------------------------------------------------------------------------

def get_component_list(data: dict, kind: str) -> list:
    return data.get("agents" if kind == "agent" else "skills", [])


def set_component_list(data: dict, kind: str, components: list) -> None:
    key = "agents" if kind == "agent" else "skills"
    data[key] = components


def validate_component(comp: dict, kind: str) -> list[str]:
    errors = []

    if "name" not in comp:
        errors.append("Missing required field: 'name'")
    elif not KEBAB_RE.match(comp["name"]):
        errors.append(f"'name' must be kebab-case: {comp['name']}")

    if "version" not in comp:
        errors.append("Missing required field: 'version'")
    elif not SEMVER_RE.match(str(comp["version"])):
        errors.append(f"'version' must be SemVer X.Y.Z: {comp['version']}")

    if comp.get("kind", kind) != kind:
        errors.append(f"'kind' must be '{kind}'")

    if "status" in comp and comp["status"] not in VALID_STATUSES:
        errors.append(f"'status' invalid: {comp['status']}")

    if "type" in comp and comp["type"] not in VALID_TYPES:
        errors.append(f"'type' invalid: {comp['type']}")

    if "scope" in comp and comp["scope"] not in VALID_SCOPES:
        errors.append(f"'scope' invalid: {comp['scope']}")

    if "path" not in comp:
        errors.append("Missing required field: 'path'")

    if "description" not in comp:
        errors.append("Missing required field: 'description'")

    return errors


def validate_manifest_integrity(data: dict, root: str) -> tuple[list[str], list[str]]:
    errors   = []
    warnings = []

    for key in ("ecosystem", "version", "agents", "skills"):
        if key not in data:
            errors.append(f"Top-level key missing: '{key}'")

    seen_names = {}

    for kind in ("agents", "skills"):
        components = data.get(kind, [])
        for i, comp in enumerate(components):
            name = comp.get("name", f"entry#{i}")
            prefix = f"[{kind}][{name}]"

            comp_errors = validate_component(comp, kind.rstrip("s"))
            for e in comp_errors:
                errors.append(f"{prefix} {e}")

            name_lower = name.lower()
            if name_lower in seen_names:
                errors.append(f"{prefix} Duplicate name. Already at position {seen_names[name_lower]}")
            else:
                seen_names[name_lower] = i

            path = comp.get("path", "")
            if path:
                full_path = os.path.join(root, path.lstrip("./"))
                if not os.path.exists(full_path):
                    errors.append(f"{prefix} Path does not exist: {path}")
                else:
                    entry_file = "SKILL.md" if kind == "skills" else os.path.basename(path)
                    entry_path = full_path if kind == "agents" else os.path.join(full_path, entry_file)
                    if not os.path.exists(entry_path):
                        errors.append(f"{prefix} Entry file not found at: {path}")

    # Cross-component dependency check
    all_active = set()
    for kind in ("agents", "skills"):
        for comp in data.get(kind, []):
            if comp.get("status") == "active":
                all_active.add(comp["name"])

    for kind in ("agents", "skills"):
        for comp in data.get(kind, []):
            deps = comp.get("dependencies", {})
            internal = deps.get("internal", []) if isinstance(deps, dict) else []
            for dep in internal:
                dep_name = dep.get("name") if isinstance(dep, dict) else dep
                if dep_name and dep_name not in all_active:
                    warnings.append(
                        f"[{comp.get('name')}] Dependency '{dep_name}' not found in active components."
                    )

    # Cycle detection
    cycle = find_cycle(data)
    if cycle:
        errors.append(f"[CYCLE] Circular dependency: {' → '.join(cycle)}")

    return errors, warnings


def find_cycle(data: dict) -> list[str] | None:
    graph = {}
    for kind in ("agents", "skills"):
        for comp in data.get(kind, []):
            name = comp.get("name")
            if not name:
                continue
            deps = comp.get("dependencies", {})
            internal = deps.get("internal", []) if isinstance(deps, dict) else []
            graph[name] = [d.get("name") if isinstance(d, dict) else d for d in internal]

    visited = set()
    rec_stack = set()
    path = []

    def dfs(node):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        for neighbor in graph.get(node, []):
            if neighbor not in visited:
                result = dfs(neighbor)
                if result:
                    return result
            elif neighbor in rec_stack:
                cycle_start = path.index(neighbor)
                return path[cycle_start:] + [neighbor]
        path.pop()
        rec_stack.discard(node)
        return None

    for node in graph:
        if node not in visited:
            result = dfs(node)
            if result:
                return result
    return None


# ---------------------------------------------------------------------------
# Operations
# ---------------------------------------------------------------------------

def op_add(data: dict, kind: str, component: dict, root: str) -> dict:
    errors = validate_component(component, kind)
    if errors:
        print("ERROR: Component failed schema validation:", file=sys.stderr)
        for e in errors:
            print(f"  ✗ {e}", file=sys.stderr)
        sys.exit(3)

    components = get_component_list(data, kind)
    existing = [c for c in components if c.get("name", "").lower() == component["name"].lower()]
    if existing:
        print(f"ERROR: '{component['name']}' already exists. Use --operation update.", file=sys.stderr)
        sys.exit(2)

    path = component.get("path", "")
    if path:
        full_path = os.path.join(root, path.lstrip("./"))
        if not os.path.exists(full_path):
            print(f"ERROR: Path does not exist: {path}\n"
                  "       Deploy the component before registering it.", file=sys.stderr)
            sys.exit(4)

    if "dependencies" not in component:
        component["dependencies"] = {"internal": [], "external": []}

    components.append(component)
    set_component_list(data, kind, components)
    print(f"[Manifest] Added {kind}: {component['name']} v{component.get('version', '?')}")
    return data


def op_update(data: dict, kind: str, component: dict) -> dict:
    name = component.get("name", "").lower()
    components = get_component_list(data, kind)
    for i, comp in enumerate(components):
        if comp.get("name", "").lower() == name:
            components[i] = {**comp, **component}
            set_component_list(data, kind, components)
            print(f"[Manifest] Updated {kind}: {comp['name']}")
            return data

    print(f"ERROR: '{component.get('name')}' not found. Use --operation add.", file=sys.stderr)
    sys.exit(1)


def op_deprecate(data: dict, kind: str, name: str) -> dict:
    name_lower = name.lower()
    components = get_component_list(data, kind)

    # Check dependents
    all_components = []
    for k in ("agents", "skills"):
        all_components.extend(data.get(k, []))
    dependents = []
    for comp in all_components:
        if comp.get("status") not in ("active", "draft", "pending_validation"):
            continue
        deps = comp.get("dependencies", {})
        internal = deps.get("internal", []) if isinstance(deps, dict) else []
        for dep in internal:
            dep_name = dep.get("name") if isinstance(dep, dict) else dep
            if dep_name and dep_name.lower() == name_lower:
                dependents.append(comp["name"])

    if dependents:
        print(f"[ALTO] Cannot deprecate '{name}': active dependents: {dependents}", file=sys.stderr)
        sys.exit(5)

    for i, comp in enumerate(components):
        if comp.get("name", "").lower() == name_lower:
            components[i]["status"] = "deprecated"
            set_component_list(data, kind, components)
            print(f"[Manifest] Deprecated {kind}: {comp['name']}")
            return data

    print(f"ERROR: '{name}' not found.", file=sys.stderr)
    sys.exit(1)


def op_validate(data: dict, root: str) -> tuple[list, list]:
    errors, warnings = validate_manifest_integrity(data, root)

    print(f"\n[Manifest] Validating {MANIFEST_PATH}")

    if warnings:
        print(f"\n  Warnings ({len(warnings)}):")
        for w in warnings:
            print(f"    ⚠ {w}")

    if errors:
        print(f"\n  Errors ({len(errors)}):", file=sys.stderr)
        for e in errors:
            print(f"    ✗ {e}", file=sys.stderr)
        print("\n[ALTO] Manifest has fatal errors. Resolve before deployment.", file=sys.stderr)
    else:
        print(f"\n  [Manifest] Validation passed — no fatal errors.")

    return errors, warnings


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="AIRON‑Cast — Manifest management."
    )
    parser.add_argument(
        "--operation",
        required=True,
        choices=list(VALID_OPERATIONS),
        help="Operation to execute."
    )
    parser.add_argument(
        "--kind",
        choices=list(VALID_KINDS),
        default=None,
        help="Component kind: agent | skill (required for add/update/deprecate)."
    )
    parser.add_argument(
        "--component",
        default=None,
        help="JSON string with component data (required for add/update)."
    )
    parser.add_argument(
        "--name",
        default=None,
        help="Component name (required for deprecate)."
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview changes without writing."
    )
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON."
    )
    args = parser.parse_args()

    root = find_project_root(os.getcwd())

    if args.operation == "init":
        init_manifest(root, args.dry_run)
        sys.exit(0)

    if args.operation == "validate":
        data = load_manifest(root)
        errs, warns = op_validate(data, root)
        if args.json_output:
            print(json.dumps({"errors": errs, "warnings": warns}, indent=2, ensure_ascii=False))
        sys.exit(3 if errs else 0)

    if not args.kind:
        print("ERROR: --kind required for this operation.", file=sys.stderr)
        sys.exit(3)

    data = load_manifest(root)

    if args.operation in ("add", "update"):
        if not args.component:
            print("ERROR: --component required for add/update.", file=sys.stderr)
            sys.exit(3)
        try:
            component = json.loads(args.component)
        except json.JSONDecodeError as e:
            print(f"ERROR: Invalid JSON: {e}", file=sys.stderr)
            sys.exit(3)

        if args.operation == "add":
            data = op_add(data, args.kind, component, root)
        else:
            data = op_update(data, args.kind, component)

    elif args.operation == "deprecate":
        if not args.name:
            print("ERROR: --name required for deprecate.", file=sys.stderr)
            sys.exit(3)
        data = op_deprecate(data, args.kind, args.name)

    save_manifest(root, data, args.dry_run)
    sys.exit(0)


if __name__ == "__main__":
    main()