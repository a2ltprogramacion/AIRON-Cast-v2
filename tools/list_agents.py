#!/usr/bin/env python3
"""
list_agents.py — AIRON‑Cast Agent Lister.

Lists all agent profiles in a directory with their key metadata:
role, upstream, downstream, and primary objective.

Usage:
    python tools/list_agents.py ./.agents/profiles/
    python tools/list_agents.py  # defaults to ./.agents/profiles/
"""

import os
import sys
import re
import yaml


def extract_frontmatter(content: str) -> dict:
    """Extract YAML frontmatter from a markdown file."""
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


def extract_field(content: str, pattern: str) -> str:
    """Extract the first match of a regex pattern from content."""
    m = re.search(pattern, content)
    return m.group(1).strip() if m else "?"


def list_agents(directory: str) -> None:
    if not os.path.isdir(directory):
        print(f"ERROR: Directory not found: {directory}", file=sys.stderr)
        sys.exit(1)

    agents = []
    for fname in sorted(os.listdir(directory)):
        if not fname.endswith(".md"):
            continue
        filepath = os.path.join(directory, fname)
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        fm = extract_frontmatter(content)
        role = fm.get("role", fname.replace(".md", ""))
        objective = extract_field(content, r'\*\*Objetivo:\*\*\s*(.+)')
        upstream = extract_field(content, r'\*\*Upstream:\*\*\s*(.+)')
        downstream = extract_field(content, r'\*\*Downstream:\*\*\s*(.+)')

        agents.append({
            "role": role,
            "upstream": upstream,
            "downstream": downstream,
            "objective": (objective[:50] + '...') if len(objective) > 50 else objective
        })

    if not agents:
        print("No agent profiles found.")
        return

    # Print table
    header = f"{'Role':<25} | {'Upstream -> Downstream':<40} | Objective"
    print(header)
    print("-" * len(header))
    for a in agents:
        handoff = f"{a['upstream']} -> {a['downstream']}"
        print(f"{a['role']:<25} | {handoff:<40} | {a['objective']}")


if __name__ == "__main__":
    if len(sys.argv) > 1:
        target_dir = sys.argv[1]
    else:
        # Default to .agents/profiles/ from project root
        target_dir = os.path.join(os.getcwd(), ".agents", "profiles")
    list_agents(target_dir)