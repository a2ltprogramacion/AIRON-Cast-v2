#!/usr/bin/env python3
"""
Completion Validator Hook — OpenCode ⊕ AIRON-Cast Fusion
Valida que existan artefactos registrados antes de permitir COMPLETED.
Se ejecuta como hook post-tool-call para acciones 'complete'/'finish'.
"""
import sys
import os
import json
import sqlite3
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(REPO_ROOT))

def validate_artifacts_for_task(task_id: int, project_slug: str = None) -> tuple[bool, str]:
    """
    Verifica que la tarea tenga al menos 1 artefacto registrado.
    Returns: (ok, message)
    """
    try:
        # Get project_id from task if slug not provided
        conn = sqlite3.connect(str(REPO_ROOT / "central_intelligence.db"))
        c = conn.cursor()
        
        if project_slug:
            pid = c.execute('SELECT id FROM projects WHERE slug = ?', (project_slug,)).fetchone()
            if not pid:
                return False, f"Proyecto no encontrado: {project_slug}"
            pid = pid[0]
        else:
            row = c.execute('SELECT project_id FROM tasks WHERE id = ?', (task_id,)).fetchone()
            if not row:
                return False, f"Tarea {task_id} no encontrada"
            pid = row[0]
        
        # Count artifacts for this task
        count = c.execute(
            'SELECT COUNT(*) FROM artifacts WHERE task_id = ?', (task_id,)
        ).fetchone()[0]
        
        conn.close()
        
        if count == 0:
            return False, f"Tarea {task_id}: NO hay artefactos registrados. Debe generar al menos 1 artefacto antes de completar."
        
        return True, f"OK: {count} artefacto(s) registrado(s)"
        
    except Exception as e:
        return False, f"Error validando artefactos: {e}"

def main():
    if len(sys.argv) < 3:
        print("Usage: completion_validator.py <task_id> <action> [project_slug]", file=sys.stderr)
        sys.exit(1)
    
    task_id = int(sys.argv[1])
    action = sys.argv[2].lower()
    project_slug = sys.argv[3] if len(sys.argv) > 3 else None
    
    # Solo validar en acciones de completado
    if action not in ('complete', 'finish', 'approve'):
        sys.exit(0)
    
    ok, msg = validate_artifacts_for_task(task_id, project_slug)
    
    if not ok:
        print(f"BLOCKED: {msg}", file=sys.stderr)
        sys.exit(1)
    
    print(f"VALIDATED: {msg}")
    sys.exit(0)

if __name__ == "__main__":
    main()