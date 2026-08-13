#!/usr/bin/env python3
# simulate_agent_handoff.py — AIRON‑Cast
# Validates handoff protocol phrases in agent profile markdown files.
# Usage: python simulate_agent_handoff.py <path_to_agent_md>

import sys
import os
import re
import json


def simulate_handoff(agent_path):
    if not os.path.isfile(agent_path):
        print(f"Error: Target {agent_path} not found.", file=sys.stderr)
        return False

    with open(agent_path, 'r', encoding='utf-8') as f:
        content = f.read()

    report = {
        "agent": os.path.basename(agent_path),
        "upstream_valid": False,
        "downstream_valid": False,
        "handoff_success_valid": False,
        "handoff_failure_valid": False,
        "warnings": []
    }

    overall_pass = True

    up_match = re.search(r'-\s*\*\*Upstream:\*\*\s*(.+)', content)
    down_match = re.search(r'-\s*\*\*Downstream:\*\*\s*(.+)', content)
    succ_match = re.search(r'-\s*\*\*Handoff Phrase \(Success\):\*\*\s*(.+)', content)
    fail_match = re.search(r'-\s*\*\*Handoff Phrase \(Failure\):\*\*\s*(.+)', content)

    # Validate Upstream
    if up_match and len(up_match.group(1).strip()) > 3:
        report["upstream_valid"] = True
    else:
        overall_pass = False
        report["warnings"].append("Upstream node undefined or improperly scaled.")

    # Validate Downstream
    if down_match and len(down_match.group(1).strip()) > 3:
        down_target = down_match.group(1).strip()
        report["downstream_valid"] = True

        # Cross-reference against existing agent profiles
        if "OPERADOR" not in down_target.upper() and "USER" not in down_target.upper():
            target_md = os.path.join(
                os.path.dirname(os.path.dirname(os.path.dirname(agent_path))),
                ".agents", "profiles", f"{down_target}.md"
            )
            if not os.path.exists(target_md):
                report["warnings"].append(
                    f"Downstream target '{down_target}' does not exist in .agents/profiles/. "
                    "Assumed to be pending creation."
                )
    else:
        overall_pass = False
        report["warnings"].append("Downstream node undefined.")

    # Validate Success Phrase
    if succ_match and "Handoff to" in succ_match.group(1):
        report["handoff_success_valid"] = True
    else:
        overall_pass = False
        report["warnings"].append(
            "Success Handoff Phrase is missing the 'Handoff to <Next_Agent>' geometric syntax."
        )

    # Validate Fail Phrase
    if fail_match:
        report["handoff_failure_valid"] = True

    print(json.dumps(report, indent=2))
    return overall_pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python simulate_agent_handoff.py <path_to_agent_md>", file=sys.stderr)
        sys.exit(1)

    success = simulate_handoff(sys.argv[1])
    sys.exit(0 if success else 1)