import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional

from core.memory_manager import MemoryManager


class HITLGateway:
    """
    Gestor de escalaciones Human-in-the-Loop.
    """

    # Condiciones válidas según manifest.json
    VALID_REASONS = {
        "Tres fallos consecutivos en la misma tarea",
        "STOP_LOSS activado",
        "RFC pendiente de aprobación",
        "Cambio arquitectural detectado",
        "Integridad de artefacto comprometida (checksum_verified = 2)",
        "Ambigüedad en spec.md que afecte decisiones irreversibles",
    }

    def __init__(self, mm: Optional[MemoryManager] = None):
        """
        Inicializa el gateway.

        Args:
            mm: Instancia de MemoryManager (si no se proporciona, se crea una nueva).
        """
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

        # Obtener proyecto
        project = self.mm.get_project(project_slug)
        if not project:
            raise ValueError(f"Proyecto {project_slug} no encontrado")

        # Obtener tarea
        # Nota: MemoryManager no tiene get_task, usamos consulta directa
        import sqlite3
        conn = sqlite3.connect(self.mm.db_path)
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
        self._log_execution(project_slug, task_id, agent_name, "HITL_ESCALATION", context)

        # 3. Actualizar state.json
        state = self.mm.read_state_json(project_slug) or {}
        state["estado"] = "PAUSED"
        state["hitl_reason"] = reason
        state["hitl_timestamp"] = datetime.now().isoformat()
        self.mm.write_state_json(project_slug, state)

        # 4. Generar archivo HITL_*.md
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        output_dir = Path("output") / project_slug
        output_dir.mkdir(parents=True, exist_ok=True)
        report_path = output_dir / f"HITL_{timestamp}.md"
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

        # Opcional: notificar por algún medio (consola por ahora)
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
        # Obtener tarea para obtener project_slug
        import sqlite3
        conn = sqlite3.connect(self.mm.db_path)
        conn.row_factory = sqlite3.Row
        cur = conn.cursor()
        cur.execute("SELECT project_id FROM tasks WHERE id = ?", (task_id,))
        task = cur.fetchone()
        conn.close()
        if not task:
            raise ValueError(f"Tarea {task_id} no encontrada")

        project = self.mm.get_project_by_id(task["project_id"])
        if not project:
            raise ValueError(f"Proyecto con ID {task['project_id']} no encontrado")

        project_slug = project["slug"]

        # Registrar resolución en execution_logs
        self._log_execution(
            project_slug, task_id, approved_by, "HITL_RESOLUTION",
            {"decision": decision, "approved_by": approved_by, "new_state": new_state}
        )

        # Actualizar estado de tarea
        self.mm.update_task_status(task_id, new_state, approved_by, "hitl_gateway")

        # Actualizar state.json (quitar PAUSED)
        state = self.mm.read_state_json(project_slug) or {}
        if state.get("estado") == "PAUSED":
            state["estado"] = "RUNNING"
            del state["hitl_reason"]
            del state["hitl_timestamp"]
        self.mm.write_state_json(project_slug, state)

        print(f"[HITL] Tarea {task_id} resuelta por {approved_by}, pasa a {new_state}")

    def _log_execution(self, project_slug: str, task_id: int, agent_name: str,
                       action_type: str, details: Dict) -> None:
        """Inserta un registro en execution_logs."""
        # Obtener project_id desde slug
        import sqlite3
        conn = sqlite3.connect(self.mm.db_path)
        cur = conn.cursor()
        cur.execute("SELECT id FROM projects WHERE slug = ?", (project_slug,))
        row = cur.fetchone()
        if not row:
            conn.close()
            raise ValueError(f"Proyecto {project_slug} no encontrado")
        project_id = row[0]
        cur.execute(
            "INSERT INTO execution_logs (project_id, task_id, agent_name, action_type, details, timestamp) "
            "VALUES (?, ?, ?, ?, ?, ?)",
            (project_id, task_id, agent_name, action_type, json.dumps(details), datetime.now().isoformat()),
        )
        conn.commit()
        conn.close()


if __name__ == "__main__":
    import tempfile
    import sqlite3

    # Configurar base de datos temporal
    db_fd, db_path = tempfile.mkstemp()
    os.close(db_fd)
    mm = MemoryManager(db_path)

    # Crear esquema base (simulado, porque memory_manager.py normalmente lo crea)
    # Pero para pruebas rápidas, creamos tablas mínimas.
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()
    cur.executescript("""
        CREATE TABLE projects (
            id INTEGER PRIMARY KEY,
            slug TEXT UNIQUE,
            name TEXT,
            status TEXT,
            root_path TEXT
        );
        CREATE TABLE tasks (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            title TEXT,
            assigned_agent TEXT,
            status TEXT,
            description TEXT,
            priority INTEGER,
            dependencies TEXT
        );
        CREATE TABLE execution_logs (
            id INTEGER PRIMARY KEY,
            project_id INTEGER,
            task_id INTEGER,
            agent_name TEXT,
            action_type TEXT,
            details TEXT,
            timestamp TEXT
        );
    """)
    conn.commit()

    # Insertar proyecto de prueba
    cur.execute("INSERT INTO projects (slug, name, status, root_path) VALUES (?, ?, ?, ?)",
                ("test-proj", "Test Project", "RUNNING", "/fake/path"))
    project_id = cur.lastrowid
    # Insertar tarea de prueba
    cur.execute("INSERT INTO tasks (project_id, title, assigned_agent, status, description, priority, dependencies) "
                "VALUES (?, ?, ?, ?, ?, ?, ?)",
                (project_id, "Test Task", "orchestrator", "LOCKED", "desc", 1, "[]"))
    task_id = cur.lastrowid
    conn.commit()
    conn.close()

    # Simular escalación
    gateway = HITLGateway(mm)
    context = {"error": "Intentos fallidos: 3", "last_output": "..."}
    try:
        gateway.escalate("test-proj", task_id, "orchestrator",
                         "Tres fallos consecutivos en la misma tarea", context)
        print("Escalación realizada")

        # Verificar que se generó el archivo HITL
        report_dir = Path("output/test-proj")
        reports = list(report_dir.glob("HITL_*.md"))
        assert len(reports) == 1, "No se generó el reporte"
        print("Reporte generado:", reports[0])

        # Simular resolución
        gateway.resolve(task_id, "Se corrige el error y se reintenta", "Argenis")
        # Verificar estado de tarea
        conn = sqlite3.connect(db_path)
        cur = conn.cursor()
        cur.execute("SELECT status FROM tasks WHERE id = ?", (task_id,))
        new_status = cur.fetchone()[0]
        assert new_status == "READY", f"Estado esperado READY, obtuvo {new_status}"
        conn.close()
        print("Resolución exitosa, tarea en READY")
    finally:
        # Limpiar
        import shutil
        shutil.rmtree("output/test-proj", ignore_errors=True)
        os.unlink(db_path)