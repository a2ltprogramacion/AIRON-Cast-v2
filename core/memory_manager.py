"""
AIRON-Cast — Memory Manager
============================
Punto único de escritura hacia central_intelligence.db.
Ningún agente escribe directamente en la DB — todo pasa por aquí.

Uso:
    from core.memory_manager import MemoryManager
    mm = MemoryManager()
    mm.create_project(slug="landing-01", ...)
    mm.update_task_status(task_id=3, new_status="IN_PROGRESS", agent="frontend_worker")
"""

import sqlite3
import json
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Union

# Ruta a la base de datos — relativa a la raíz del proyecto
DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "central_intelligence.db"
SCHEMA_PATH = Path(__file__).resolve().parent / "airon_cast_schema.sql"


class MemoryManagerError(Exception):
    """Error controlado del MemoryManager."""
    pass


class MemoryManager:
    """
    Interfaz centralizada para todas las operaciones de lectura y escritura
    en central_intelligence.db. Garantiza integridad referencial, logging automático
    y checkpoint antes de cada operación crítica.
    """

    def __init__(self, db_path: Optional[Union[str, Path]] = None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self._ensure_db()

    # ------------------------------------------------------------------
    # CONEXIÓN
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys = ON")
        conn.execute("PRAGMA journal_mode = WAL")
        return conn

    def _ensure_db(self):
        """Crea la DB desde el schema si no existe."""
        if not self.db_path.exists():
            if not SCHEMA_PATH.exists():
                raise MemoryManagerError(
                    f"Schema no encontrado: {SCHEMA_PATH}. "
                    "Ejecuta primero tools/init_ecosystem.py"
                )
            with self._connect() as conn:
                conn.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))
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
        root_path = str(Path("workspace") / slug)
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
                    conn, project_id=project_id, agent_name="system",
                    action_type="workflow_start",
                    action_detail=f"Proyecto creado: {slug}",
                    outcome="success",
                )
                return project_id
            except sqlite3.IntegrityError:
                raise MemoryManagerError(f"El slug '{slug}' ya existe en projects.")

    def update_project_status(self, slug: str, status: str) -> None:
        valid = {"DRAFT", "ACTIVE", "PAUSED", "ARCHIVED", "COMPLETED"}
        if status not in valid:
            raise MemoryManagerError(f"Estado inválido: {status}. Válidos: {valid}")
        with self._connect() as conn:
            conn.execute("UPDATE projects SET status = ? WHERE slug = ?", (status, slug))

    def get_project(self, slug: str) -> Optional[dict]:
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
                conn, project_id=project_id, task_id=task_id,
                agent_name=assigned_agent, action_type="start",
                action_detail=f"Tarea creada: {title}", outcome="pending",
            )
            return task_id

    def unlock_task(self, task_id: int) -> bool:
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
                    """, deps,
                ).fetchone()["cnt"]
                if completed < len(deps):
                    return False
            conn.execute("UPDATE tasks SET status = 'READY' WHERE id = ?", (task_id,))
            self._log(
                conn, project_id=row["project_id"], task_id=task_id,
                agent_name="orchestrator", action_type="start",
                action_detail="Tarea desbloqueada", outcome="success",
            )
            return True

    def update_task_status(
        self, task_id: int, new_status: str, agent_name: str,
        model_used: Optional[str] = None, error_message: Optional[str] = None,
    ) -> None:
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
            action_type = "finish" if new_status == "COMPLETED" else "start"
            outcome = "success"
            if new_status == "IN_PROGRESS":
                update_fields["started_at"] = datetime.now(timezone.utc).isoformat()
            if new_status == "COMPLETED":
                update_fields["completed_at"] = datetime.now(timezone.utc).isoformat()
            if new_status == "FAILED":
                retry_count = row["retry_count"] + 1
                action_type = "error"
                outcome = "failure"
                if retry_count < row["max_retries"]:
                    update_fields["status"] = "READY"
                    update_fields["retry_count"] = retry_count
                    action_type = "start"
                    outcome = "pending"
                else:
                    update_fields["retry_count"] = retry_count
            conn.execute(
                """
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
                conn, project_id=row["project_id"], task_id=task_id,
                agent_name=agent_name, action_type=action_type,
                action_detail=f"Tarea '{row['title']}' → {new_status}",
                outcome=outcome, model_used=model_used, error_message=error_message,
            )

    # ------------------------------------------------------------------
    # ARTEFACTOS
    # ------------------------------------------------------------------

    def register_artifact(
        self, task_id: int, project_id: int, file_path: str,
        file_type: str, metadata: Optional[dict] = None,
    ) -> int:
        abs_path = Path(file_path)
        if not abs_path.exists():
            raise MemoryManagerError(f"Artefacto no encontrado: {file_path}")
        checksum = self._sha256(abs_path)
        meta_json = json.dumps(metadata or {})
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO artifacts
                    (task_id, project_id, file_path, file_type, checksum,
                     checksum_verified, metadata)
                VALUES (?, ?, ?, ?, ?, 1, ?)
                """,
                (task_id, project_id, str(abs_path), file_type, checksum, meta_json),
            )
            artifact_id = cur.lastrowid
            self._log(
                conn, project_id=project_id, task_id=task_id,
                agent_name="system", action_type="artifact_registration",
                action_detail=f"Artefacto: {abs_path} [{checksum[:8]}...]",
                outcome="success",
            )
            return artifact_id

    # ------------------------------------------------------------------
    # ADRs (DECISIONES DE ARQUITECTURA)
    # ------------------------------------------------------------------

    ADR_FILENAME_PATTERN = __import__("re").compile(r"ADR-\d+")
    ADR_TITLE_PATTERN = __import__("re").compile(
        r"^#\s*(ADR-\d+)\s*[·\-:]\s*(.+?)\s*$", __import__("re").MULTILINE
    )

    def is_adr_file(self, file_path: Union[str, Path]) -> bool:
        """True si el nombre del archivo matchea el patron ADR-NNN-*.md."""
        return bool(self.ADR_FILENAME_PATTERN.search(Path(file_path).name))

    def register_adr_from_file(
        self, file_path: Union[str, Path], project_id: int,
        task_id: Optional[int] = None, applied_agents: Optional[list] = None,
    ) -> dict:
        """
        Indexa un archivo ADR en la tabla `adrs` (los triggers del schema
        propagan a `adrs_fts` automaticamente). Si el decision_id ya existe,
        no hace nada.

        Args:
            file_path: ruta al archivo .md del ADR.
            project_id: FK al proyecto.
            task_id: FK a la tarea (opcional, solo para logging).
            applied_agents: lista de agentes afectados por la decision.

        Returns:
            {"inserted": bool, "decision_id": str, "title": str,
             "reason": "ok"|"duplicate"|"parse_error"|"file_missing"}
        """
        abs_path = Path(file_path)
        result = {"inserted": False, "decision_id": None, "title": None, "reason": "ok"}

        if not abs_path.exists():
            result["reason"] = "file_missing"
            return result

        try:
            content = abs_path.read_text(encoding="utf-8")
        except Exception:
            result["reason"] = "parse_error"
            return result

        match = self.ADR_TITLE_PATTERN.search(content)
        if not match:
            result["reason"] = "parse_error"
            return result

        decision_id, title = match.group(1), match.group(2).strip()
        result["decision_id"] = decision_id
        result["title"] = title

        rationale_match = __import__("re").search(
            r"##\s*Decisi[oó]n\s*\n(.*?)(?=\n## |\Z)", content, __import__("re").DOTALL
        )
        rationale = rationale_match.group(1).strip()[:500] if rationale_match else content[:500]
        fts_content = content.replace("\n", " ").strip()
        agents_json = json.dumps(applied_agents or [])

        with self._connect() as conn:
            cur = conn.execute(
                "SELECT id FROM adrs WHERE decision_id = ? AND project_id = ?",
                (decision_id, project_id),
            )
            if cur.fetchone():
                result["reason"] = "duplicate"
                return result

            conn.execute(
                """INSERT INTO adrs
                       (project_id, decision_id, title, rationale,
                        applied_agents, status, fts_content)
                   VALUES (?, ?, ?, ?, ?, 'active', ?)""",
                (project_id, decision_id, title, rationale, agents_json, fts_content),
            )
            self._log(
                conn, project_id=project_id, task_id=task_id,
                agent_name="system", action_type="checkpoint",
                action_detail=f"ADR indexado: {decision_id} - {title[:60]}",
                outcome="success",
            )

        result["inserted"] = True
        return result

    def verify_artifact(self, artifact_id: int) -> bool:
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
                conn, project_id=row["project_id"], task_id=row["task_id"],
                agent_name="system", action_type="qa_review",
                action_detail=f"Artefacto {artifact_id}: {'OK' if is_valid else 'ALTERADO'}",
                outcome="success" if is_valid else "failure",
            )
            return is_valid

    # ------------------------------------------------------------------
    # CHECKPOINTS
    # ------------------------------------------------------------------

    def write_checkpoint(
        self, project_id: int, task_id: int, agent_name: str,
        step_number: int, step_description: str, state_snapshot: str,
    ) -> int:
        with self._connect() as conn:
            cur = conn.execute(
                """
                INSERT INTO checkpoints
                    (project_id, task_id, agent_name, step_number,
                     step_description, state_snapshot, is_recovery_point)
                VALUES (?, ?, ?, ?, ?, ?, 1)
                """,
                (project_id, task_id, agent_name, step_number,
                 step_description, state_snapshot),
            )
            checkpoint_id = cur.lastrowid
            self._log(
                conn, project_id=project_id, task_id=task_id,
                agent_name=agent_name, action_type="checkpoint",
                action_detail=f"Checkpoint paso {step_number}: {step_description}",
                outcome="success",
            )
            return checkpoint_id

    def get_last_checkpoint(self, project_id: int) -> Optional[dict]:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT * FROM checkpoints
                WHERE project_id = ? AND is_recovery_point = 1
                ORDER BY created_at DESC LIMIT 1
                """, (project_id,),
            ).fetchone()
            return dict(row) if row else None

    # ------------------------------------------------------------------
    # ESTADO DEL PROYECTO (state.json)
    # ------------------------------------------------------------------

    def write_state_json(self, project_slug: str, state: dict) -> None:
        path = Path("workspace") / project_slug / "state.json"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(json.dumps(state, indent=2, ensure_ascii=False), encoding="utf-8")

    def read_state_json(self, project_slug: str) -> Optional[dict]:
        path = Path("workspace") / project_slug / "state.json"
        if not path.exists():
            return None
        return json.loads(path.read_text(encoding="utf-8"))

    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE CONTEXTO (MEMORIA HÍBRIDA)
    # ------------------------------------------------------------------

    def build_context_for(self, task_id: int) -> str:
        """
        Construye el paquete de contexto para un agente:
        - Historial comprimido de la sesión
        - ADRs relevantes vía FTS5
        - Feedback anterior para el agente asignado
        - Definición de la tarea actual
        """
        with self._connect() as conn:
            row = conn.execute(
                "SELECT * FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
            if not row:
                raise MemoryManagerError(f"Tarea {task_id} no encontrada.")

            task = dict(row)
            project_id = task["project_id"]
            agent = task["assigned_agent"]

            # 1. Historial comprimido
            compressed = self.get_compressed_context(project_id)

            # 2. ADRs relevantes vía FTS5
            keywords = f"{task['title']} {task.get('description', '')}"
            adrs_context = self._search_adrs(keywords)

            # 3. Feedback anterior para este agente
            feedback_context = self._get_feedback_for(agent)

            # 4. Tarea actual
            task_context = (
                f"=== TAREA ACTUAL ===\n"
                f"ID: {task['id']}\n"
                f"Título: {task['title']}\n"
                f"Agente asignado: {agent}\n"
                f"Descripción: {task.get('description', 'Sin descripción')}\n"
                f"Prioridad: {task.get('priority', 0)}\n"
                f"Dependencias: {task.get('dependencies', '[]')}\n"
                f"Modelo sugerido: {task.get('suggested_model', 'default')}\n"
            )

            # 5. Context7: documentación actualizada de librerías relevantes
            context7_context = self._build_context7_context(task)

            return f"{compressed}\n\n{adrs_context}\n\n{feedback_context}\n\n{context7_context}\n{task_context}"

    def _search_adrs(self, query: str, limit: int = 3) -> str:
        """Busca ADRs relevantes usando FTS5 sobre adrs_fts."""
        with self._connect() as conn:
            try:
                rows = conn.execute(
                    """
                    SELECT decision_id, title, rationale
                    FROM adrs_fts
                    WHERE adrs_fts MATCH ?
                    ORDER BY rank
                    LIMIT ?
                    """, (query, limit),
                ).fetchall()
            except sqlite3.OperationalError:
                return "=== ADRs RELEVANTES ===\n(Sin resultados de búsqueda FTS5)\n"
            if not rows:
                return "=== ADRs RELEVANTES ===\n(Sin ADRs coincidentes)\n"
            lines = ["=== ADRs RELEVANTES ==="]
            for r in rows:
                lines.append(f"[{r['decision_id']}] {r['title']}: {r['rationale'][:200]}...")
            return "\n".join(lines)

    def _get_feedback_for(self, agent: str, limit: int = 3) -> str:
        """Recupera feedback anterior para un agente específico."""
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT error_type, correction, recurrence_count
                FROM feedback_history
                WHERE affected_agent = ?
                ORDER BY recurrence_count DESC
                LIMIT ?
                """, (agent, limit),
            ).fetchall()
            if not rows:
                return "=== FEEDBACK ANTERIOR ===\n(Sin feedback previo para este agente)\n"
            lines = ["=== FEEDBACK ANTERIOR ==="]
            for r in rows:
                lines.append(f"[{r['error_type']}] (x{r['recurrence_count']}): {r['correction'][:200]}...")
            return "\n".join(lines)

    # ------------------------------------------------------------------
    # VISTAS / CONSULTAS RÁPIDAS
    # ------------------------------------------------------------------

    def get_project_status(self, slug: Optional[str] = None) -> list[dict]:
        with self._connect() as conn:
            if slug:
                rows = conn.execute(
                    "SELECT * FROM v_project_status WHERE slug = ?", (slug,)
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM v_project_status").fetchall()
            return [dict(r) for r in rows]

    def get_ready_tasks(self, project_slug: Optional[str] = None) -> list[dict]:
        with self._connect() as conn:
            if project_slug:
                rows = conn.execute(
                    "SELECT * FROM v_ready_tasks WHERE project_slug = ?",
                    (project_slug,),
                ).fetchall()
            else:
                rows = conn.execute("SELECT * FROM v_ready_tasks").fetchall()
            return [dict(r) for r in rows]

    def get_all_project_tasks(self, project_slug: str) -> list[dict]:
        """Todas las tareas del proyecto (cualquier estado).
        Usado por _should_stop() para evaluar S1 (tareas FAILED con
        retry_count >= max_retries) y otras condiciones que requieren
        inspeccionar estados no-READY."""
        with self._connect() as conn:
            rows = conn.execute(
                """SELECT t.* FROM tasks t
                   JOIN projects p ON p.id = t.project_id
                   WHERE p.slug = ?""",
                (project_slug,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_integrity_alerts(self) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute("SELECT * FROM v_integrity_alerts").fetchall()
            return [dict(r) for r in rows]

    def get_execution_logs(self, project_id: int, limit: int = 200) -> list[dict]:
        with self._connect() as conn:
            rows = conn.execute(
                """
                SELECT * FROM execution_logs
                WHERE project_id = ?
                ORDER BY created_at ASC
                LIMIT ?
                """, (project_id, limit),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_compressed_context(self, project_id: int) -> str:
        from core.trajectory_compressor import TrajectoryCompressor
        logs = self.get_execution_logs(project_id)
        compressor = TrajectoryCompressor()
        return compressor.compress_logs(logs)

    # ------------------------------------------------------------------
    # LOG (uso interno)
    # ------------------------------------------------------------------

    def _log(
        self, conn: sqlite3.Connection, project_id: int, agent_name: str,
        action_type: str, action_detail: str, outcome: str,
        task_id: Optional[int] = None, model_used: Optional[str] = None,
        error_message: Optional[str] = None, duration_ms: Optional[int] = None,
        tokens_used: Optional[int] = None,
    ) -> None:
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

    # ------------------------------------------------------------------
    # CONTEXT7 INTEGRATION
    # ------------------------------------------------------------------

    def _query_context7(self, library: str, query: str) -> str:
        """
        Consulta Context7 MCP para obtener documentación actualizada de una librería.
        Usa el protocolo de 2 pasos: resolve-library-id + query-docs.
        """
        import subprocess
        import json
        import sys

        # En Windows, usar shell=True para que encuentre npx en PATH
        use_shell = sys.platform == "win32"

        # Paso 1: resolve-library-id
        try:
            resolve_cmd = [
                "npx", "-y", "@upstash/context7-mcp",
                "resolve-library-id", library
            ]
            result = subprocess.run(
                resolve_cmd, capture_output=True, text=True, timeout=10, shell=use_shell
            )
            if result.returncode != 0:
                return f"[Context7] Error resolviendo librería '{library}': {result.stderr[:200]}"

            # Parse result to get library ID
            library_id = result.stdout.strip()
            if not library_id:
                return f"[Context7] No se encontró ID para '{library}'"
        except Exception as e:
            return f"[Context7] Error en resolve-library-id: {e}"

        # Paso 2: query-docs
        try:
            query_cmd = [
                "npx", "-y", "@upstash/context7-mcp",
                "query-docs", library_id, query
            ]
            result = subprocess.run(
                query_cmd, capture_output=True, text=True, timeout=15, shell=use_shell
            )
            if result.returncode != 0:
                return f"[Context7] Error consultando docs: {result.stderr[:200]}"
            return result.stdout.strip()
        except Exception as e:
            return f"[Context7] Error en query-docs: {e}"

    def _get_relevant_libraries(self, task: dict) -> list[str]:
        """
        Determina qué librerías son relevantes para la tarea basándose en
        el agente asignado y la descripción de la tarea.
        """
        agent = task.get("assigned_agent", "")
        description = task.get("description") or ""
        description = description.lower()
        title = task.get("title", "").lower()
        combined = f"{title} {description}"

        # Mapeo agente -> librerías típicas
        agent_libs = {
            "frontend_worker": ["astro", "tailwindcss", "alpinejs"],
            "backend_specialist": ["django", "djangorestframework"],
            "ux-ui_specialist": ["tailwindcss", "astro"],
            "backend_specialist": ["django", "djangorestframework"],
        }

        libs = set(agent_libs.get(agent, []))

        # Detectar por palabras clave en título/descripción
        keyword_map = {
            "astro": ["astro", "astro.build"],
            "tailwind": ["tailwindcss", "tailwind"],
            "alpine": ["alpinejs", "alpine"],
            "django": ["django", "djangorestframework"],
            "react": ["react"],
            "vue": ["vue"],
            "svelte": ["svelte"],
            "tailwind": ["tailwindcss"],
        }

        for keyword, libs_list in keyword_map.items():
            if keyword in combined:
                libs.update(libs_list)

        return list(libs)[:5]  # Máximo 5 librerías para no exceder tokens

    def _build_context7_instructions(self, task: dict) -> str:
        """
        Genera instrucciones para que el agente use Context7 MCP automáticamente.
        """
        libraries = self._get_relevant_libraries(task)
        if not libraries:
            return ""

        libs_str = ", ".join(libraries)
        return f"""

=== CONTEXT7: INSTRUCCIONES OBLIGATORIAS ===
Antes de implementar, DEBES usar las herramientas MCP de Context7 para obtener documentación actualizada:

LIBRERÍAS RELEVANTES: {libs_str}

PROTOCOLO OBLIGATORIO (2 pasos por librería):
1. resolve-library-id: Obtén el ID oficial de Context7
   - Ejemplo: resolve-library-id libraryName="astro" query="View Transitions API v5"

2. query-docs: Consulta la documentación específica
   - Ejemplo: query-docs libraryId="/withastro/astro" query="View Transitions API v5 breaking changes"

REGLAS:
- EJECUTA AMBOS PASOS antes de escribir código
- MÁXIMO 3 consultas por librería si no encuentras la respuesta
- Incluye en tu código: // Implementation validated via context7 (Latest version)
- NO uses conocimiento previo; usa SOLO lo que devuelva Context7

EJECUTA AHORA para cada librería: {', '.join(libraries)}
"""

    def _build_context7_context(self, task: dict) -> str:
        """
        Genera instrucciones para que el agente use Context7 MCP automáticamente.
        """
        return self._build_context7_instructions(task)

    # ------------------------------------------------------------------
    # UTILIDADES
    # ------------------------------------------------------------------

    @staticmethod
    def _sha256(path: Path) -> str:
        h = hashlib.sha256()
        with open(path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                h.update(chunk)
        return h.hexdigest()
