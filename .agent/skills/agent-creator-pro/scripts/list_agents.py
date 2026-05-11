#!/usr/bin/env python3
import os
import sys
import re

def list_agents(directory):
    if not os.path.exists(directory) or not os.path.isdir(directory):
        print(f"Error: Directory '{directory}' does not exist.", file=sys.stderr)
        sys.exit(1)

    print(f"Agents found in {directory}:\n")
    print(f"{'Role Name'.ljust(25)} | {'Upstream -> Downstream'.ljust(40)} | Objective")
    print("-" * 120)

    for filename in os.listdir(directory):
        if filename.endswith(".md"):
            filepath = os.path.join(directory, filename)
            with open(filepath, 'r') as f:
                content = f.read()

            role_match = re.search(r'-\s*\*\*Role Name:\*\*\s*(.+)', content)
            obj_match = re.search(r'-\s*\*\*Primary Objective:\*\*\s*(.+)', content)
            up_match = re.search(r'-\s*\*\*Upstream:\*\*\s*(.+)', content)
            down_match = re.search(r'-\s*\*\*Downstream:\*\*\s*(.+)', content)

            role = role_match.group(1).strip() if role_match else filename.replace('.md', '')
            obj = obj_match.group(1).strip() if obj_match else "N/A"
            up = up_match.group(1).strip() if up_match else "?"
            down = down_match.group(1).strip() if down_match else "?"
            
            # Truncate objective if too long
            obj = (obj[:50] + '...') if len(obj) > 50 else obj
            handoff = f"{up} -> {down}"

            print(f"{role.ljust(25)} | {handoff.ljust(40)} | {obj}")

if __name__ == "__main__":
    target_dir = sys.argv[1] if len(sys.argv) > 1 else ".agent/catalog/agents/"
    list_agents(target_dir)
