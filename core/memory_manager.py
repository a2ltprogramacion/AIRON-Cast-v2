"""
AIRON-Cast — Memory Manager
============================
Punto único de escritura hacia airon.sqlite.
Ningún agente escribe directamente en la DB — todo pasa por aquí.

Uso:
    from core.memory_manager import MemoryManager
    mm = MemoryManager()
    mm.create_project(slug="web-site-authority", ...)
    mm.update_task_status(task_id=3, new_status="IN_PROGRESS", agent="frontend")
"""

import sqlite3
import json
import hashlib
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

# Ruta a la base de datos — relativa a la raíz del proyecto
DEFAULT_DB_PATH = Path(__file__).parent / "airon.sqlite"
SCHEMA_PATH = Path(__file__).parent / "airon_cast_schema.sql"


class MemoryManagerError(Exception):
    """Error controlado del MemoryManager."""
    pass


class MemoryManager:
    """
    Interfaz centralizada para todas las operaciones de escritura y lectura
    en airon.sqlite. Garantiza integridad referencial, logging automático
    y checkpoint antes de cada operación crítica.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        db_path_str = str(db_path) if db_path else str(DEFAULT_DB_PATH)
        self.db_path = db_path_str if db_path_str == ":memory:" else Path(db_path_str)
        self._memory_conn = None
        self._ensure_db()

    # ------------------------------------------------------------------
    # CONEXIÓN
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        if self.db_path == ":memory:":
            if not self._memory_conn:
                self._memory_conn = sqlite3.connect(":memory:", check_same_thread=False)
                self._memory_conn.row_factory = sqlite3.Row
                self._memory_conn.execute("PRAGMA foreign_keys = ON")
            return self._memory_conn

        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row       # Filas como diccionarios
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn


    def _ensure_db(self):
        """Crea la DB desde el schema si no existe."""
        # Si es :memory:, siempre ejecutamos el schema
        is_memory = str(self.db_path) == ":memory:"
        if is_memory or not self.db_path.exists():
            if not SCHEMA_PATH.exists():
                raise MemoryManagerError(
                    f"Schema no encontrado: {SCHEMA_PATH}. "
                    "Asegúrate de que core/airon_cast_schema.sql existe."
                )
            with self._connect() as conn:
                conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
            if not is_memory:
                print(f"[MemoryManager] DB inicializada: {self.db_path}")


    # ------------------------------------------------------------------
    # PROYECTOS
    # ------------------------------------------------------------------

    def create_project(
        self,
        slug: str,
        name: str,
        project_type: str,
        active_workflow: str,
        client: str = "interno",
        priority: int = 5,
        notes: Optional[str] = None,
    ) -> int:
        """
        Registra un nuevo proyecto. Devuelve el ID asignado.
        Lanza MemoryManagerError si el slug ya existe.
        """
        root_path = str(Path("output") / slug) + "/"
        with self._connect() as conn:
            try:
                cur = conn.execute(
                    """
                    INSERT INTO projects
                        (slug, name, client, project_type, active_workflow, root_path, priority, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """,
                    (slug, name, client, project_type, active_workflow,
                     root_path, priority, notes),
                )
                project_id = cur.lastrowid
                self._log(
                    conn,
                    project_id=project_id,
                    agent_name="system",
                    action_type="WORKFLOW_START",
                    action_detail=f"Proyecto creado: {slug}",
                    outcome="SUCCESS",
                )
                return project_id
            except sqlite3.IntegrityError:
                raise MemoryManagerError(
                    f"El slug '{slug}' ya existe en projects."
                )

    def update_project_status(self, slug: str, status: str) -> None:
        """Actualiza el estado de un proyecto."""
        valid = {"DRAFT", "ACTIVE", "PAUSED", "REVIEW", "COMPLETED", "ARCHIVED"}
        if status not in valid:
            raise MemoryManagerError(f"Estado inválido: {status}. Válidos: {valid}")
        with self._connect() as conn:
            conn.execute(
                "UPDATE projects SET status = ? WHERE slug = ?",
                (status, slug),
            )

    def get_project(self, slug: str) -> Optional[dict]:
        """Devuelve el proyecto como dict o None si no existe."""
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM projects WHERE slug = ?", (slug,)
            ).fetchone()
            return dict(row) if row else None

    # ------------------------------------------------------------------
    # TAREAS
    # ------------------------------------------------------------------

    def create_task(
        self,
        project_id: int,
        title: str,
        assigned_agent: str,
        description: Optional[str] = None,
        priority: int = 5,
        dependencies: Optional[list] = None,
        parent_task_id: Optional[int] = None,
        suggested_model: Optional[str] = None,
    ) -> int:
        """
        Crea una tarea en estado LOCKED.
        Las dependencias son lista de task IDs. Devuelve el ID creado.
        """
        deps_json = json.dumps(dependencies or [])
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO tasks
                    (project_id, title, description, assigned_agent,
                     priority, dependencies, parent_task_id, status, suggested_model)
                VALUES (?, ?, ?, ?, ?, ?, ?, 'LOCKED', ?)
                """,
                (project_id, title, description, assigned_agent,
                 priority, deps_json, parent_task_id, suggested_model),
            )
            task_id = cur.lastrowid
            self._log(
                conn,
                project_id=project_id,
                task_id=task_id,
                agent_name=assigned_agent,
                action_type="TASK_START",
                action_detail=f"Tarea creada: {title}",
                outcome="PENDING",
            )
            return task_id

    def unlock_task(self, task_id: int) -> bool:
        """
        Mueve la tarea de LOCKED a READY si todas sus dependencias
        están en COMPLETED. Devuelve True si se desbloqueó.
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT dependencies, status, project_id FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

            if not row:
                raise MemoryManagerError(f"Tarea {task_id} no encontrada.")

            if row["status"] != "LOCKED":
                return False

            deps = json.loads(row["dependencies"] or "[]")
            if deps:
                placeholders = ",".join("?" * len(deps))
                completed = conn.execute(
                    f"""
                    SELECT COUNT(*) as cnt FROM tasks
                    WHERE id IN ({placeholders}) AND status = 'COMPLETED'
                    """,
                    deps,
                ).fetchone()["cnt"]

                if completed < len(deps):
                    return False  # Dependencias aún no completas

            conn.execute(
                "UPDATE tasks SET status = 'READY' WHERE id = ?", (task_id,)
            )
            self._log(
                conn,
                project_id=row["project_id"],
                task_id=task_id,
                agent_name="orchestrator",
                action_type="TASK_START",
                action_detail="Tarea desbloqueada: dependencias cumplidas",
                outcome="SUCCESS",
            )
            return True

    def update_task_status(
        self,
        task_id: int,
        new_status: str,
        agent_name: str,
        model_used: Optional[str] = None,
        error_message: Optional[str] = None,
    ) -> None:
        """
        Actualiza el estado de una tarea. Gestiona reintentos automáticamente.
        Si llega a 3 fallos consecutivos → estado FAILED + log de error.
        """
        valid = {
            "LOCKED", "READY", "IN_PROGRESS", "REVIEW",
            "APPROVED", "COMPLETED", "FAILED", "SKIPPED"
        }
        if new_status not in valid:
            raise MemoryManagerError(f"Estado inválido: {new_status}")

        with self._connect() as conn:
            row = conn.execute(
                "SELECT project_id, retry_count, max_retries, title FROM tasks WHERE id = ?",
                (task_id,),
            ).fetchone()

            if not row:
                raise MemoryManagerError(f"Tarea {task_id} no encontrada.")

            update_fields = {"status": new_status, "model_used": model_used}
            action_type = "TASK_COMPLETE" if new_status == "COMPLETED" else "TASK_START"
            outcome = "SUCCESS"

            if new_status == "IN_PROGRESS":
                update_fields["started_at"] = datetime.now(timezone.utc).isoformat()

            if new_status == "COMPLETED":
                update_fields["completed_at"] = datetime.now(timezone.utc).isoformat()

            if new_status == "FAILED":
                retry_count = row["retry_count"] + 1
                action_type = "TASK_FAIL"
                outcome = "FAILURE"

                if retry_count < row["max_retries"]:
                    # Aún tiene reintentos — vuelve a READY
                    new_status = "READY"
                    update_fields["status"] = "READY"
                    update_fields["retry_count"] = retry_count
                    action_type = "TASK_RETRY"
                    outcome = "PENDING"
                else:
                    update_fields["retry_count"] = retry_count

            conn.execute(
                f"""
                UPDATE tasks SET
                    status = :status,
                    model_used = COALESCE(:model_used, model_used),
                    started_at = COALESCE(:started_at, started_at),
                    completed_at = COALESCE(:completed_at, completed_at),
                    retry_count = COALESCE(:retry_count, retry_count)
                WHERE id = :task_id
                """,
                {
                    "status": update_fields.get("status", new_status),
                    "model_used": update_fields.get("model_used"),
                    "started_at": update_fields.get("started_at"),
                    "completed_at": update_fields.get("completed_at"),
                    "retry_count": update_fields.get("retry_count"),
                    "task_id": task_id,
                },
            )
            self._log(
                conn,
                project_id=row["project_id"],
                task_id=task_id,
                agent_name=agent_name,
                action_type=action_type,
                action_detail=f"Tarea '{row['title']}' → {new_status}",
                outcome=outcome,
                model_used=model_used,
                error_message=error_message,
            )

    # ------------------------------------------------------------------
    # ARTEFACTOS
    # ------------------------------------------------------------------

    def register_artifact(
        self,
        task_id: int,
        project_id: int,
        file_path: str,
        file_type: str,
        metadata: Optional[dict] = None,
    ) -> int:
        """
        Registra un artefacto generado y calcula su checksum SHA256.
        file_path debe ser la ruta absoluta al archivo en disco.
        Devuelve el ID del artefacto creado.
        """
        abs_path = Path(file_path)
        if not abs_path.exists():
            raise MemoryManagerError(
                f"Artefacto no encontrado en disco: {file_path}"
            )

        checksum = self._sha256(abs_path)
        rel_path = str(abs_path)
        meta_json = json.dumps(metadata or {})

        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO artifacts
                    (task_id, project_id, file_path, file_type, checksum,
                     checksum_verified, metadata)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (task_id, project_id, rel_path, file_type, checksum, meta_json),
            )
            artifact_id = cur.lastrowid
            self._log(
                conn,
                project_id=project_id,
                task_id=task_id,
                agent_name="system",
                action_type="ARTIFACT_CREATE",
                action_detail=f"Artefacto registrado: {rel_path} [{checksum[:8]}...]",
                outcome="SUCCESS",
            )
            return artifact_id

    def verify_artifact(self, artifact_id: int) -> bool:
        """
        Verifica que el checksum en disco coincida con el registrado.
        Actualiza checksum_verified: 1=ok, 2=alterado.
        Devuelve True si íntegro, False si fue modificado.
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT file_path, checksum, project_id, task_id FROM artifacts WHERE id = ?",
                (artifact_id,),
            ).fetchone()

            if not row:
                raise MemoryManagerError(f"Artefacto {artifact_id} no encontrado.")

            current = self._sha256(Path(row["file_path"]))
            is_valid = current == row["checksum"]
            verified_code = 1 if is_valid else 2

            conn.execute(
                "UPDATE artifacts SET checksum_verified = ?, verified_at = ? WHERE id = ?",
                (verified_code, datetime.now(timezone.utc).isoformat(), artifact_id),
            )
            self._log(
                conn,
                project_id=row["project_id"],
                task_id=row["task_id"],
                agent_name="system",
                action_type="ARTIFACT_VERIFY",
                action_detail=f"Artefacto {artifact_id}: {'OK' if is_valid else 'ALTERADO'}",
                outcome="SUCCESS" if is_valid else "FAILURE",
            )
            return is_valid

    # ------------------------------------------------------------------
    # CHECKPOINTS
    # ------------------------------------------------------------------

    def write_checkpoint(
        self,
        project_id: int,
        task_id: int,
        agent_name: str,
        step_number: int,
        step_description: str,
        state_snapshot: dict,
    ) -> int:
        """
        Escribe un checkpoint ANTES de ejecutar el paso.
        state_snapshot es el contenido actual del state.json del proyecto.
        Devuelve el ID del checkpoint creado.
        """
        snapshot_json = json.dumps(state_snapshot, ensure_ascii=False)
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO checkpoints
                    (project_id, task_id, agent_name, step_number,
                     step_description, state_snapshot, is_recovery_point)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (project_id, task_id, agent_name, step_number,
                 step_description, snapshot_json),
            )
            checkpoint_id = cur.lastrowid
            self._log(
                conn,
                project_id=project_id,
                task_id=task_id,
                agent_name=agent_name,
                action_type="CHECKPOINT_WRITE",
                action_detail=f"Checkpoint paso {step_number}: {step_description}",
                outcome="SUCCESS",
            )
            return checkpoint_id

    def get_last_checkpoint(self, project_id: int) -> Optional[dict]:
        """Devuelve el último checkpoint recuperable del proyecto."""
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM checkpoints
                WHERE project_id = ? AND is_recovery_point = 1
                ORDER BY created_at DESC LIMIT 1
                """,
                (project_id,),
            ).fetchone()
            return dict(row) if row else None

    # ------------------------------------------------------------------
    # ESTADO DEL PROYECTO (state.json)
    # ------------------------------------------------------------------

    def write_state_json(self, project_slug: str, state: dict) -> None:
        """
        Persiste el state.json del proyecto en output/[slug]/state.json.
        Crea el directorio si no existe.
        """
        path = Path("output") / project_slug / "state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(
            json.dumps(state, indent=2, ensure_ascii=False),
            encoding="utf-8",
        )

    def read_state_json(self, project_slug: str) -> Optional[dict]:
        """Lee el state.json del proyecto. Devuelve None si no existe."""
        path = Path("output") / project_slug / "state.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # VISTAS / CONSULTAS RÁPIDAS
    # ------------------------------------------------------------------

    def get_project_status(self, slug: Optional[str] = None) -> list[dict]:
        """
        Devuelve el estado de todos los proyectos activos (o uno específico).
        Usa la vista v_project_status.
        """
        with self._connect() as conn:
            if slug:
                rows = conn.execute(
                    "SELECT * FROM v_project_status WHERE slug = ?", (slug,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM v_project_status").fetchall()
            return [dict(r) for r in rows]

    def get_ready_tasks(self, project_slug: Optional[str] = None) -> list[dict]:
        """Devuelve tareas en estado READY listas para ejecutar."""
        with self._connect() as conn:
            if project_slug:
                rows = conn.execute(
                    "SELECT * FROM v_ready_tasks WHERE project = ?",
                    (project_slug,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM v_ready_tasks").fetchall()
            return [dict(r) for r in rows]

    def get_integrity_alerts(self) -> list[dict]:
        """Devuelve artefactos con checksum alterado."""
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM v_integrity_alerts").fetchall()
            return [dict(r) for r in rows]

    def get_execution_logs(self, project_id: int, limit: int = 200) -> list[dict]:
        """Obtiene los logs de ejecución de un proyecto ordenados cronológicamente."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM execution_logs
                WHERE project_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """,
                (project_id, limit)
            ).fetchall()
            return [dict(r) for r in rows]

    def get_compressed_context(self, project_id: int) -> str:
        """
        Obtiene los logs del proyecto y los pasa por el TrajectoryCompressor
        para devolver un contexto optimizado en tokens.
        """
        from core.trajectory_compressor import TrajectoryCompressor
        logs = self.get_execution_logs(project_id)
        compressor = TrajectoryCompressor()
        return compressor.compress_logs(logs)

    # ------------------------------------------------------------------
    # LOG (uso interno)
    # ------------------------------------------------------------------

    def _log(
        self,
        conn: sqlite3.Connection,
        project_id: int,
        agent_name: str,
        action_type: str,
        action_detail: str,
        outcome: str,
        task_id: Optional[int] = None,
        model_used: Optional[str] = None,
        error_message: Optional[str] = None,
        duration_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
    ) -> None:
        """Registra una entrada en execution_logs. Uso exclusivo interno."""
        conn.execute(
            """
            INSERT INTO execution_logs
                (project_id, task_id, agent_name, action_type, action_detail,
                 outcome, model_used, error_message, duration_ms, tokens_used)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (project_id, task_id, agent_name, action_type, action_detail,
             outcome, model_used, error_message, duration_ms, tokens_used),
        )

    # ------------------------------------------------------------------
    # UTILIDADES
    # ------------------------------------------------------------------

    @staticmethod
    def _sha256(path: Path) -> str:
        """Calcula el checksum SHA256 de un archivo."""
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
