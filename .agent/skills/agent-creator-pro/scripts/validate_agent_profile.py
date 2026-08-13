#!/usr/bin/env python3
import sys
import os
import re

def check_journal_evidence(component_name):
    journal_dir = os.path.join(os.getcwd(), ".agent", "memory", "journal")
    if not os.path.exists(journal_dir):
        return False
    for entry in os.listdir(journal_dir):
        path = os.path.join(journal_dir, entry)
        if os.path.isfile(path):
            with open(path, 'r', encoding='utf-8') as f:
                if f"FORGED: {component_name}" in f.read():
                    return True
    return False

def validate_agent(file_path):
    if not os.path.exists(file_path):
        print(f"Fatal Error: File not found: {file_path}", file=sys.stderr)
        return False

    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    errors = []
    warnings = []

    # 1. Format: Begins with # Agent Profile:
    if not re.search(r'^# Agent Profile:\s*(.+)$', content, re.MULTILINE):
        errors.append("Missing or malformed '# Agent Profile: <Role Name>' header.")

    # 2. Section Checks
    sections = [
        "## 1. Core Identity",
        "## 2. Authorized Scope & Constraints",
        "## 3. Assigned Skills",
        "## 4. Orchestration & Handoff Protocol"
    ]
    for section in sections:
        if section not in content:
            errors.append(f"Missing mandatory section: '{section}'")

    # 3. Core Identity fields
    if not re.search(r'-\s*\*\*Role Name:\*\*\s*(.+)', content):
        errors.append("Missing or empty '- **Role Name:**' field.")
    if not re.search(r'-\s*\*\*Primary Objective:\*\*\s*(.+)', content):
        errors.append("Missing or empty '- **Primary Objective:**' field.")

    # 4. Scope fields
    if not re.search(r'-\s*\*\*Allowed:\*\*', content):
        errors.append("Missing '- **Allowed:**' section.")
    if not re.search(r'-\s*\*\*Prohibited:\*\*', content):
        errors.append("Missing '- **Prohibited:**' section.")

    # 5. Skills (just warn if "None")
    if re.search(r'## 3\. Assigned Skills\s*-\s*None', content):
        warnings.append("Agent has no assigned skills ('None'). Ensure this is intentional.")

    # 6. Orchestration fields
    orchestration_fields = [
        r'-\s*\*\*Upstream:\*\*\s*(.+)',
        r'-\s*\*\*Downstream:\*\*\s*(.+)',
        r'-\s*\*\*Trigger Condition:\*\*\s*(.+)',
        r'-\s*\*\*Handoff Phrase \(Success\):\*\*\s*(.+)'
    ]
    for pattern in orchestration_fields:
        if not re.search(pattern, content):
            errors.append(f"Missing required Orchestration field: {pattern.replace(r'\\s*', ' ').replace(r'(.+)', '')}")

    # Output results
    if warnings:
        for w in warnings:
            print(f"Warning: {w}", file=sys.stderr)
    
    if errors:
        for e in errors:
            print(f"Error: {e}", file=sys.stderr)
        print("Validation FAILED.", file=sys.stderr)
        return False

    name_match = re.search(r'^# Agent Profile:\s*(.+)$', content, re.MULTILINE)
    agent_name = name_match.group(1).strip() if name_match else os.path.basename(file_path).replace('.md', '')

    if not check_journal_evidence(agent_name):
        print(f"Error: No journal entry found for this agent. It must have 'FORGED: {agent_name}' in the journal.", file=sys.stderr)
        print("Validation FAILED.", file=sys.stderr)
        return False

    print("Validation PASSED.")
    return True

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: validate_agent_profile.py <path_to_agent.md>", file=sys.stderr)
        sys.exit(1)
    
    file_path = sys.argv[1]
    success = validate_agent(file_path)
    sys.exit(0 if success else 1)
