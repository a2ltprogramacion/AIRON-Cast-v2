#!/usr/bin/env python3
"""
Post-Tool Call Hook — OpenCode ⊕ AIRON-Cast Fusion
Registra resultado, valida checksums, actualiza memoria si es write/edit.
"""
import sys
import json
import os
import hashlib
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from core.checksum_verifier import verify_checksum, calculate_checksum
except ImportError:
    verify_checksum = None
    calculate_checksum = None

def calculate_sha256(filepath):
    """Calcula SHA256 de un archivo."""
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def register_artifact(filepath, agent):
    """Registra artefacto en Engram (placeholder)."""
    # TODO: Integrar con memory_manager.register_artifact()
    if calculate_checksum:
        checksum = calculate_checksum(filepath)
        print(f"INFO: Artefacto registrado: {filepath} [{checksum[:16]}...] por {agent}", file=sys.stderr)

def main():
    if len(sys.argv) < 3:
        sys.exit(0)
    
    tool_name = sys.argv[1]
    result = sys.argv[2] if len(sys.argv) > 2 else ""
    
    try:
        result_data = json.loads(result)
    except:
        result_data = {"output": result}
    
    agent = os.environ.get("OPENCODE_AGENT", "orchestrator")
    
    # Si es write/edit, registrar artefacto y validar checksum
    if tool_name in ("write", "edit"):
        filepath = None
        if tool_name == "write":
            filepath = result_data.get("path") or result_data.get("file_path")
        elif tool_name == "edit":
            filepath = result_data.get("path") or result_data.get("file_path")
        
        if filepath and os.path.exists(filepath):
            # Registrar artefacto
            register_artifact(filepath, agent)
            
            # Validar checksum si existe verifier
            if verify_checksum:
                ok = verify_checksum(filepath)
                if not ok:
                    print(f"WARNING: Checksum verification failed for {filepath}", file=sys.stderr)
    
    # Log de ejecución (placeholder para execution_logs)
    print(f"LOG: {agent} | {tool_name} | status=ok", file=sys.stderr)
    
    sys.exit(0)

if __name__ == "__main__":
    main()