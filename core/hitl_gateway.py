"""
AIRON-Cast — HITL Gateway
==========================
Gestor de escalaciones Human-in-the-Loop.
Adaptado del Legacy (2026-06-03): rutas workspace/, columnas execution_logs actualizadas.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from core.memory_manager import MemoryManager


class HITLGateway:
    """Gestor de escalaciones Human-in-the-Loop."""

    # Condiciones válidas según manifest.json actual
    VALID_REASONS = {
        "Tres fallos consecutivos en la misma tarea",
        "STOP_LOSS activado",
        "RFC pendiente de aprobación",
        "Cambio arquitectural detectado",
        "Integridad de artefacto comprometida (checksum_verified = 2)",
        "Ambigüedad que afecte decisiones irreversibles",
    }

    def __init__(self, mm: Optional[MemoryManager] = None):
        self.mm = mm or MemoryManager()

    def escalate(
        self,
        project_slug: str,
        task_id: int,
        agent_name: str,
        reason: str,
        context: Dict[str, Any],
    ) -> None:
        """
        Escala un problema para decisión humana.

        Args:
            project_slug: Slug del proyecto.
            task_id: ID de la tarea.
            agent_name: Nombre del agente que escaló.
            reason: Razón de escalación (debe estar en VALID_REASONS).
            context: Diccionario con información adicional del estado.

        Raises:
            ValueError: Si la razón no es válida o el proyecto/tarea no existen.
        """
        if reason not in self.VALID_REASONS:
            raise ValueError(f"Razón de escalación no válida: {reason}")

        project = self.mm.get_project(project_slug)
        if not project:
            raise ValueError(f"Proyecto {project_slug} no encontrado")

        # Verificar tarea
        import sqlite3
        conn = sqlite3.connect(str(self.mm.db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
        task = cur.fetchone()
        conn.close()
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        # 1. Actualizar estado de tarea a REVIEW
        self.mm.update_task_status(task_id, "REVIEW", agent_name, "hitl_gateway")

        # 2. Registrar en execution_logs
        self._log_execution(project["id"], task_id, agent_name, "HITL_ESCALATION", context, "failure")

        # 3. Actualizar state.json
        state = self.mm.read_state_json(project_slug) or {}
        state["status"] = "PAUSED"
        state["hitl_reason"] = reason
        state["hitl_timestamp"] = datetime.now().isoformat()
        self.mm.write_state_json(project_slug, state)

        # 4. Generar archivo HITL_*.md
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_dir = Path("workspace") / project_slug
        report_dir.mkdir(parents=True, exist_ok=True)
        report_path = report_dir / f"HITL_{timestamp}.md"
        with open(report_path, "w", encoding="utf-8") as f:
            f.write(f"# Escalación HITL\n\n")
            f.write(f"- **Proyecto:** {project_slug}\n")
            f.write(f"- **Tarea ID:** {task_id}\n")
            f.write(f"- **Agente:** {agent_name}\n")
            f.write(f"- **Razón:** {reason}\n")
            f.write(f"- **Timestamp:** {datetime.now().isoformat()}\n\n")
            f.write("## Contexto\n\n```json\n")
            json.dump(context, f, indent=2)
            f.write("\n```\n\n")
            f.write("## Opciones disponibles\n\n")
            f.write("1. Revisar y corregir el problema.\n")
            f.write("2. Aprobar la acción con modificaciones.\n")
            f.write("3. Cancelar la tarea.\n")
            f.write("4. Reintentar con nuevos parámetros.\n")

        print(f"[HITL] Escalación creada: {report_path}")

    def resolve(
        self,
        task_id: int,
        decision: str,
        approved_by: str,
        new_state: str = "READY",
    ) -> None:
        """
        Resuelve una escalación, retomando la tarea.

        Args:
            task_id: ID de la tarea.
            decision: Texto con la decisión tomada.
            approved_by: Nombre del aprobador (usualmente "Argenis").
            new_state: Estado al que se devuelve la tarea (por defecto READY).
        """
        import sqlite3
        conn = sqlite3.connect(str(self.mm.db_path))
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT project_id FROM tasks WHERE id = ?", (task_id,))
        task = cur.fetchone()
        conn.close()
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        # Obtener proyecto por ID
        cur = conn = sqlite3.connect(str(self.mm.db_path))
        cur.row_factory = sqlite3.Row
        cur.execute("SELECT * FROM projects WHERE id = ?", (task["project_id"],))
        project = cur.fetchone()
        conn.close()
        if not project:
            raise ValueError(f"Proyecto con ID {task['project_id']} no encontrado")

        project_slug = project["slug"]

        # Registrar resolución en execution_logs
        self._log_execution(
            project["id"], task_id, approved_by, "HITL_RESOLUTION",
            {"decision": decision, "approved_by": approved_by, "new_state": new_state},
            "success"
        )

        # Actualizar estado de tarea
        self.mm.update_task_status(task_id, new_state, approved_by, "hitl_gateway")

        # Actualizar state.json (quitar PAUSED)
        state = self.mm.read_state_json(project_slug) or {}
        if state.get("status") == "PAUSED":
            state["status"] = "RUNNING"
            state.pop("hitl_reason", None)
            state.pop("hitl_timestamp", None)
        self.mm.write_state_json(project_slug, state)

        print(f"[HITL] Tarea {task_id} resuelta por {approved_by}, pasa a {new_state}")

    def _log_execution(self, project_id: int, task_id: int, agent_name: str,
                       action_type: str, details: Dict, outcome: str = "pending") -> None:
        """Inserta un registro en execution_logs con el esquema actualizado."""
        import sqlite3
        conn = sqlite3.connect(str(self.mm.db_path))
        cur = conn.cursor()
        cur.execute(
            """INSERT INTO execution_logs
               (project_id, task_id, agent_name, action_type, action_detail, outcome, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (project_id, task_id, agent_name, action_type, json.dumps(details), outcome,
             datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()