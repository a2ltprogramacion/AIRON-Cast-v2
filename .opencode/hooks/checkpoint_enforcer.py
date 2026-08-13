#!/usr/bin/env python3
"""
Checkpoint Enforcer Hook — OpenCode ⊕ AIRON-Cast Fusion
Fuerza checkpoint (Engram mem_save) antes de writes/edits destructivos.
"""
import sys
import os
import json
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

# Tool calls que requieren checkpoint obligatorio
DESTRUCTIVE_TOOLS = {"write", "edit", "bash"}

# Patrones de operaciones irreversibles en bash
IRREVERSIBLE_BASH_PATTERNS = [
    "rm ", "del ", "rmdir", "rd ",
    "mv ", "move ",
    ">", ">>",  # redirección que sobrescribe
    "truncate",
    "dd ",
    "format",
    "mkfs",
    "drop table", "drop database",
    "delete from",
    "update ",
    "alter table",
]

def is_destructive_bash(command):
    """Detecta si un comando bash es potencialmente irreversible."""
    cmd_lower = command.lower()
    return any(pattern in cmd_lower for pattern in IRREVERSIBLE_BASH_PATTERNS)

def enforce_checkpoint(tool_name, tool_args):
    """Determina si requiere checkpoint y lo ejecuta."""
    if tool_name not in DESTRUCTIVE_TOOLS:
        return True, ""
    
    if tool_name == "bash":
        command = tool_args.get("command", "")
        if not is_destructive_bash(command):
            return True, ""
    
    # Requiere checkpoint - intentar via Engram mem_save
    # TODO: Llamada real a Engram MCP
    checkpoint_data = {
        "type": "pre_write_checkpoint",
        "tool": tool_name,
        "args_summary": str(tool_args)[:200],
        "agent": os.environ.get("OPENCODE_AGENT", "orchestrator"),
    }
    
    print(f"CHECKPOINT_REQUIRED:{json.dumps(checkpoint_data)}")
    return True, ""

def main():
    if len(sys.argv) < 2:
        sys.exit(0)
    
    tool_name = sys.argv[1]
    tool_args = {}
    if len(sys.argv) > 2:
        try:
            tool_args = json.loads(sys.argv[2])
        except:
            pass
    
    ok, msg = enforce_checkpoint(tool_name, tool_args)
    if not ok:
        print(f"BLOCKED: {msg}", file=sys.stderr)
        sys.exit(1)
    
    sys.exit(0)

if __name__ == "__main__":
    main()