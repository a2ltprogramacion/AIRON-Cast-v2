#!/usr/bin/env python3
"""
Pre-Tool Call Hook — OpenCode ⊕ AIRON-Cast Fusion
Valida scope/jurisdiction, inyecta contexto relevante, valida budget antes de cada tool call.
"""
import sys
import json
import os
from pathlib import Path

# Añadir raíz del repo al path
REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from core.service_supervisor import ensure_supervisor_running
except ImportError:
    ensure_supervisor_running = None

# Jurisdicciones por agente (scope → paths permitidos)
JURISDICTIONS = {
    "orchestrator": [".opencode", "workspace", "MISSION_CONTROL.md", "state.json"],
    "pm": ["workspace", "BACKLOG.md", "MISSION_CONTROL.md"],
    "requirements_architect": ["workspace", "BACKLOG.md"],
    "ux-ui_specialist": ["workspace", "src"],
    "writer": ["workspace", "docs", "README.md"],
    "frontend_worker": ["workspace", "src"],
    "backend_specialist": ["workspace", "src"],
    "tester": ["workspace", "tests", "src"],
    "qa_auditor": ["workspace", "src", "tests"],
    "docs": ["workspace", "docs", "README.md"],
    "meta_factory": [".opencode/agents", ".opencode/skills"],
}

# Patrones de decisiones arquitectónicas que requieren ADR
ARCH_DECISION_PATTERNS = [
    "change architecture",
    "change schema",
    "migrate database",
    "change stack",
    "new dependency",
    "refactor core",
]

def get_current_agent():
    """Obtiene el agente actual desde variable de entorno o state."""
    return os.environ.get("OPENCODE_AGENT", "orchestrator")

def get_jurisdiction_paths(agent):
    """Obtiene paths permitidos para el agente."""
    return JURISDICTIONS.get(agent, [])

def validate_path_access(agent, tool_name, tool_args):
    """Valida que el tool no acceda fuera de jurisdicción."""
    if tool_name not in ("read", "write", "edit", "bash", "glob", "grep"):
        return True, ""
    
    allowed_paths = get_jurisdiction_paths(agent)
    if not allowed_paths:
        return True, ""  # Sin restricciones = acceso total
    
    # Extraer paths del tool call
    paths_to_check = []
    if tool_name in ("read", "write", "edit"):
        path = tool_args.get("path") or tool_args.get("file_path")
        if path:
            paths_to_check.append(path)
    elif tool_name == "bash":
        # Para bash, validar directorio de trabajo
        cwd = tool_args.get("cwd", ".")
        paths_to_check.append(cwd)
    
    for path in paths_to_check:
        if not any(Path(path).resolve().is_relative_to(Path(p).resolve()) for p in allowed_paths if os.path.exists(p)):
            return False, f"Acceso fuera de jurisdicción: {path} no está en {allowed_paths}"
    
    return True, ""

def check_arch_decision_requirement(tool_name, tool_args):
    """Detecta si la acción requiere ADR."""
    if tool_name not in ("write", "edit", "bash"):
        return False
    
    content = ""
    if tool_name in ("write", "edit"):
        content = tool_args.get("content") or tool_args.get("new_string", "")
    elif tool_name == "bash":
        content = tool_args.get("command", "")
    
    content_lower = content.lower()
    return any(pattern in content_lower for pattern in ARCH_DECISION_PATTERNS)

def validate_token_budget(tool_args):
    """Valida budget de tokens (placeholder)."""
    # TODO: Integrar con api_router para tracking real
    return True, ""

def main():
    if len(sys.argv) < 2:
        print("Usage: pre_tool_call.py <tool_name> [json_args]", file=sys.stderr)
        sys.exit(1)
    
    tool_name = sys.argv[1]
    tool_args = {}
    if len(sys.argv) > 2:
        try:
            tool_args = json.loads(sys.argv[2])
        except json.JSONDecodeError:
            pass
    
    agent = get_current_agent()
    
    # 1. Validar jurisdicción
    ok, msg = validate_path_access(agent, tool_name, tool_args)
    if not ok:
        print(f"BLOCKED: {msg}", file=sys.stderr)
        sys.exit(1)
    
    # 2. Detectar decisión arquitectónica
    if check_arch_decision_requirement(tool_name, tool_args):
        print("WARNING: Acción detectada como decisión arquitectónica. Requiere ADR (mem_save type='adr')", file=sys.stderr)
    
    # 3. Validar token budget
    ok, msg = validate_token_budget(tool_args)
    if not ok:
        print(f"BLOCKED: {msg}", file=sys.stderr)
        sys.exit(1)
    
    # 4. Asegurar supervisor vivo
    if ensure_supervisor_running:
        try:
            ensure_supervisor_running()
        except Exception:
            pass  # No bloquear por esto
    
    # OK - permitir tool call
    sys.exit(0)

if __name__ == "__main__":
    main()