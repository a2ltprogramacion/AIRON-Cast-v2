#!/usr/bin/env python3
import sys
import os
import argparse

def check_protocol_token():
    token_path = os.path.join(os.getcwd(), ".agent", "memory", ".protocol_active")
    if not os.path.exists(token_path):
        print("ERROR: Protocol token not found. You MUST execute forge-ignition.md before creating an agent profile.", file=sys.stderr)
        sys.exit(10)

def generate_profile(args):
    template = f"""# Agent Profile: {args.name}

## 1. Core Identity
- **Role Name:** {args.name}
- **Primary Objective:** {args.goal}

## 2. Authorized Scope & Constraints
- **Allowed:**
  - {args.allowed if args.allowed else 'None specified.'}
- **Prohibited:**
  - {args.prohibited}

## 3. Assigned Skills
"""
    skills = args.skills.split(',') if args.skills else []
    if skills:
        for skill in skills:
            template += f"- {skill.strip()}\n"
    else:
        template += "- None\n"

    template += f"""
## 4. Orchestration & Handoff Protocol
- **Upstream:** {args.upstream}
- **Downstream:** {args.downstream}
- **Trigger Condition:** {args.trigger}
- **Handoff Phrase (Success):** "{args.handoff}"
"""
    if args.handoff_fail:
        template += f'- **Handoff Phrase (Failure):** "{args.handoff_fail}"\n'

    return template

def main():
    parser = argparse.ArgumentParser(description="Generate an Agent Profile (.md)")
    parser.add_argument("--name", required=True, help="Role Name exactly as it will appear")
    parser.add_argument("--goal", required=True, help="Primary Objective")
    parser.add_argument("--allowed", help="Allowed actions")
    parser.add_argument("--prohibited", required=True, help="Prohibited actions")
    parser.add_argument("--skills", help="Comma-separated list of assigned skills")
    parser.add_argument("--upstream", required=True, help="Who gives this agent work")
    parser.add_argument("--downstream", required=True, help="Who this agent passes work to")
    parser.add_argument("--trigger", required=True, help="Condition that starts the agent")
    parser.add_argument("--handoff", required=True, help="Success handoff phrase")
    parser.add_argument("--handoff-fail", help="Failure handoff phrase")
    parser.add_argument("--output", required=True, help="Output directory or file path")
    parser.add_argument("--force", action="store_true", help="Overwrite if file exists")

    args = parser.parse_args()

    check_protocol_token()

    # Determine exact output file path
    if os.path.isdir(args.output):
        out_path = os.path.join(args.output, f"{args.name}.md")
    else:
        out_path = args.output
        if not out_path.endswith('.md'):
            out_path += '.md'

    # Check for overwrite
    if os.path.exists(out_path) and not args.force:
        print(f"Error: {out_path} already exists. Use --force to overwrite.", file=sys.stderr)
        sys.exit(1)

    # Generate content
    content = generate_profile(args)

    # Write file
    try:
        os.makedirs(os.path.dirname(out_path) or '.', exist_ok=True)
        with open(out_path, 'w') as f:
            f.write(content)
        print(f"Successfully generated agent profile: {out_path}")
    except Exception as e:
        print(f"Failed to write file: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
