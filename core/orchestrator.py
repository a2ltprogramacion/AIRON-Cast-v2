"""
AIRON-Cast Orchestrator
=======================
Motor Round‑Robin con pizarra compartida y memoria híbrida.
Coordina agentes, construye contexto, gestiona STOP_LOSS y escribe MISSION_CONTROL.md.
"""

import time
import json
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

from core.memory_manager import MemoryManager
from core.api_router import APIRouter


@dataclass
class ExecutionReport:
    project: str
    tasks_completed: int
    tasks_failed: int
    tasks_pending: int
    stop_loss_triggered: bool
    hitl_required: bool
    duration_seconds: float
    timestamp: str


class Orchestrator:
    def __init__(
        self,
        project_slug: str,
        workflow_file: Optional[str] = None,
        memory_manager: Optional[MemoryManager] = None,
    ):
        self.project_slug = project_slug
        self.workflow_file = workflow_file
        self.mm = memory_manager if memory_manager else MemoryManager()
        self.router = APIRouter()
        self.project = None
        self.hitl_required = False

    # ------------------------------------------------------------------
    # INICIALIZACIÓN
    # ------------------------------------------------------------------

    def load_project(self) -> dict:
        """Carga y valida el proyecto desde la base de datos."""
        self.project = self.mm.get_project(self.project_slug)
        if not self.project:
            raise Exception(f"Proyecto '{self.project_slug}' no encontrado.")
        if self.project["status"] != "ACTIVE":
            raise Exception(
                f"Proyecto '{self.project_slug}' no está ACTIVE "
                f"(status={self.project['status']})."
            )
        return self.project

    # ------------------------------------------------------------------
    # COLA DE TAREAS (Round‑Robin)
    # ------------------------------------------------------------------

    def build_task_queue(self) -> list:
        """Obtiene las tareas READY ordenadas por prioridad y fecha de creación."""
        return self.mm.get_ready_tasks(self.project_slug)

    # ------------------------------------------------------------------
    # CONTEXTO (MEMORIA HÍBRIDA)
    # ------------------------------------------------------------------

    def build_context(self, task: dict) -> str:
        """
        Construye el paquete de contexto usando el nuevo método
        build_context_for de MemoryManager, que ya incluye:
        - Historial comprimido
        - ADRs relevantes vía FTS5
        - Feedback anterior para el agente
        - Definición de la tarea actual
        """
        return self.mm.build_context_for(task["id"])

    # ------------------------------------------------------------------
    # CONSTRUCCIÓN DE PROMPT PARA AGENTE
    # ------------------------------------------------------------------

    def _build_agent_prompt(self, task: dict, agent_profile: str, context: str) -> str:
        """
        Construye el prompt completo que el IDE model procesará
        actuando como el agente asignado.
        """
        agent = task["assigned_agent"]
        project_slug = self.project_slug

        return f"""Eres el agente **{agent}** del ecosistema AIRON‑Cast.

## Tu perfil operativo
{agent_profile}

## Contexto del proyecto
{context}

## Tarea asignada
- **ID:** {task['id']}
- **Título:** {task['title']}
- **Descripción:** {task.get('description', 'Sin descripción adicional')}
- **Prioridad:** {task.get('priority', 0)}

## Instrucciones
1. Actúa EXCLUSIVAMENTE como el agente {agent} según tu perfil.
2. Genera TODOS los artefactos necesarios para completar esta tarea.
3. Escribe los archivos en `workspace/{project_slug}/src/` (o la ruta correspondiente al proyecto).
4. Respeta tu jurisdicción: no hagas lo que está en "Prohibido".
5. Al terminar, indica explícitamente: "TAREA COMPLETADA. Artifacts: [lista de archivos generados]".

Comienza a trabajar como {agent}.
"""

    def _load_agent_profile(self, agent: str) -> Optional[str]:
        """Carga el perfil Markdown del agente buscando en las ubicaciones estándar."""
        candidate_paths = [
            Path(".agent/agents") / f"{agent}.md",
            Path(".agents/profiles") / f"{agent}.md",
        ]
        for p in candidate_paths:
            if p.exists():
                return p.read_text(encoding="utf-8")
        # En caso de ejecuciones de prueba o mock
        return f"# Mock Agent Profile: {agent}\nRol: {agent}\n"

    # ------------------------------------------------------------------
    # DISPATCH: OBTENER SIGUIENTE TAREA + PROMPT
    # ------------------------------------------------------------------

    def dispatch_next(self) -> Optional[dict]:
        """
        Obtiene la siguiente tarea READY, construye el prompt completo
        y lo retorna para que el IDE model lo procese.

        Returns:
            dict con {"task_id", "agent", "title", "prompt"} o None si
            no hay tareas READY o se activó STOP_LOSS.
        """
        if not self.project:
            self.load_project()

        if self._should_stop():
            self._write_mission_control("STOP_LOSS activado. Cola congelada.")
            return None

        queue = self.build_task_queue()
        if not queue:
            return None

        task = queue[0]
        agent = task["assigned_agent"]

        # Leer perfil del agente
        agent_profile = self._load_agent_profile(agent)
        if agent_profile is None:
            self._write_mission_control(
                f"ERROR: Perfil no encontrado para agente: {agent}"
            )
            return None
        context = self.build_context(task)
        prompt = self._build_agent_prompt(task, agent_profile, context)

        # Checkpoint antes de despachar
        state = self.mm.read_state_json(self.project_slug) or {}
        self.mm.write_checkpoint(
            self.project["id"],
            task["id"],
            "orchestrator",
            0,
            f"Despachando tarea {task['id']} → {agent}",
            json.dumps(state),
        )

        # Mover a IN_PROGRESS
        self.mm.update_task_status(task["id"], "IN_PROGRESS", "orchestrator")
        self._write_mission_control(
            f"Tarea {task['id']} → IN_PROGRESS ({agent})"
        )

        return {
            "task_id": task["id"],
            "agent": agent,
            "title": task["title"],
            "prompt": prompt,
        }

    # ------------------------------------------------------------------
    # COMPLETE: REGISTRAR RESPUESTA DEL IDE MODEL
    # ------------------------------------------------------------------

    _EXT_TO_FILE_TYPE = {
        "astro": "source", "html": "source", "htm": "source",
        "css": "source", "scss": "source", "sass": "source",
        "js": "source", "jsx": "source", "mjs": "source", "cjs": "source",
        "ts": "source", "tsx": "source",
        "vue": "source", "svelte": "source",
        "json": "config", "yaml": "config", "yml": "config", "toml": "config",
        "toml": "config", "ini": "config", "env": "config",
        "md": "doc", "mdx": "doc", "txt": "doc", "rst": "doc",
        "svg": "asset", "png": "asset", "jpg": "asset", "jpeg": "asset",
        "webp": "asset", "gif": "asset", "ico": "asset", "avif": "asset",
        "pdf": "asset", "zip": "asset", "tar": "asset", "gz": "asset",
    }

    @classmethod
    def _map_file_type(cls, file_path: str) -> str:
        ext = Path(file_path).suffix.lstrip(".").lower()
        return cls._EXT_TO_FILE_TYPE.get(ext, "other")

    def complete_task(
        self,
        task_id: int,
        response: str,
        artifacts: Optional[list] = None,
        success: bool = True,
    ) -> bool:
        """
        Registra la respuesta del IDE model y mueve la tarea a REVIEW.

        Args:
            task_id: ID de la tarea completada.
            response: Texto completo de la respuesta del IDE model.
            artifacts: Lista de rutas de archivos generados (opcional).
            success: True si el agente completó la tarea correctamente.

        Returns:
            True si se registró correctamente.
        """
        if not self.project:
            self.load_project()

        project_id = self.project["id"]

        if success:
            self.mm.update_task_status(task_id, "REVIEW", "orchestrator")
            self._write_mission_control(
                f"Tarea {task_id} → REVIEW (pendiente de QA)"
            )

            # Registrar artefactos generados
            if artifacts:
                for file_path in artifacts:
                    try:
                        file_type = self._map_file_type(file_path)
                        self.mm.register_artifact(
                            task_id, project_id, file_path, file_type
                        )
                    except Exception as e:
                        self._write_mission_control(
                            f"WARN: No se pudo registrar artefacto {file_path}: {e}"
                        )

                # Hook post-artefacto: detectar e indexar ADRs automaticamente
                for file_path in artifacts:
                    if not self.mm.is_adr_file(file_path):
                        continue
                    try:
                        adr_result = self.mm.register_adr_from_file(
                            file_path, project_id, task_id=task_id,
                            applied_agents=[self.project.get("slug", "")],
                        )
                        if adr_result["inserted"]:
                            self._write_mission_control(
                                f"ADR auto-indexado: {adr_result['decision_id']} - {adr_result['title'][:50]}"
                            )
                        elif adr_result["reason"] == "duplicate":
                            self._write_mission_control(
                                f"ADR ya indexado (skip): {adr_result['decision_id']}"
                            )
                        else:
                            self._write_mission_control(
                                f"WARN: ADR no procesado ({adr_result['reason']}): {file_path}"
                            )
                    except Exception as e:
                        self._write_mission_control(
                            f"WARN: Error indexando ADR {file_path}: {e}"
                        )

            # Desbloquear dependencias
            all_tasks = self.mm.get_ready_tasks(self.project_slug)
            for t in all_tasks:
                self.mm.unlock_task(t["id"])

        else:
            self._handle_failure(
                {"id": task_id, "title": "", "retry_count": 0},
                f"Agente reportó fallo: {response[:200]}"
            )
            self._write_mission_control(
                f"Tarea {task_id} → FALLO reportado por agente"
            )

        # Cachear la respuesta para futuros lookups
        prompt_hash = self.router.hash_prompt(response[:500])
        self.router.store_response(
            prompt_hash, "ide_model", response[:2000],
            tokens_used=0, model_used="ide_active_model",
        )

        return True

    # ------------------------------------------------------------------
    # RUN_STEP: EJECUCIÓN PASO A PASO DESDE EL IDE
    # ------------------------------------------------------------------

    def run_step(self) -> dict:
        """
        Ejecuta UN solo paso del ciclo Round-Robin.
        Diseñado para ser llamado por el IDE model en cada iteración.

        Returns:
            {"status": "dispatched", "task_id": ..., "prompt": ...}
            {"status": "empty"} si no hay tareas READY.
            {"status": "stop_loss"} si se activó STOP_LOSS.
        """
        dispatch = self.dispatch_next()

        if dispatch is None:
            if self._should_stop():
                return {"status": "stop_loss"}
            return {"status": "empty"}

        return {
            "status": "dispatched",
            "task_id": dispatch["task_id"],
            "agent": dispatch["agent"],
            "title": dispatch["title"],
            "prompt": dispatch["prompt"],
        }

    # ------------------------------------------------------------------
    # _EXECUTE_TASK (INTERNO — WRAPPER DE DISPATCH + COMPLETE)
    # ------------------------------------------------------------------

    def _execute_task(self, task: dict) -> bool:
        """
        Modo IDE-as-Agent: construye el prompt y lo emite vía stdout
        en formato JSON estructurado para que el IDE model lo consuma.
        NO bloquea, NO espera input().

        Cuando se ejecuta dentro del ciclo run(), este método emite
        el prompt y retorna True. El IDE model debe llamar
        complete_task() por separado para registrar la respuesta.
        """
        agent = task["assigned_agent"]

        # Leer perfil del agente
        agent_profile = self._load_agent_profile(agent)
        if agent_profile is None:
            self._write_mission_control(
                f"ERROR: Perfil no encontrado para agente: {agent}"
            )
            return False
        context = self.build_context(task)
        prompt = self._build_agent_prompt(task, agent_profile, context)

        # Emitir prompt como JSON para consumo del IDE model
        output = json.dumps({
            "action": "dispatch",
            "task_id": task["id"],
            "agent": agent,
            "title": task["title"],
            "prompt": prompt,
        }, ensure_ascii=False)

        print(output)
        return True

    # ------------------------------------------------------------------
    # GESTIÓN DE FALLOS
    # ------------------------------------------------------------------

    def _handle_failure(self, task: dict, error: str) -> None:
        """Delega en update_task_status(FAILED), que ya implementa la
        política de reintentos: incrementa retry_count y, si supera
        max_retries, deja la tarea en FAILED y marca HITL requerido.
        Mantiene hitl_required sincronizado con el estado de la DB."""
        task_id = task["id"]
        with self.mm._connect() as conn:
            row = conn.execute(
                "SELECT retry_count, max_retries FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        prev_retries = row["retry_count"] if row else 0

        self.mm.update_task_status(
            task_id, "FAILED", "orchestrator", error_message=error
        )

        with self.mm._connect() as conn:
            row = conn.execute(
                "SELECT status, retry_count, max_retries FROM tasks WHERE id = ?", (task_id,)
            ).fetchone()
        new_retries = row["retry_count"]
        new_status = row["status"]

        if new_status == "FAILED" and new_retries >= row["max_retries"]:
            self.hitl_required = True
            print(f"[ORCHESTRATOR] Tarea {task_id}: FAILED. HITL requerido (retry {new_retries}/{row['max_retries']}).")
        else:
            print(f"[ORCHESTRATOR] Tarea {task_id}: reintento {new_retries}/{row['max_retries']}.")

    # ------------------------------------------------------------------
    # CONDICIONES DE PARADA (STOP_LOSS)
    # ------------------------------------------------------------------

    def _should_stop(self) -> bool:
        """Evalúa las 5 condiciones de STOP_LOSS definidas en AGENTS.md."""
        # S1: 3 fallos consecutivos en alguna tarea (status=FAILED, retry_count >= max_retries)
        all_tasks = self.mm.get_all_project_tasks(self.project_slug)
        for t in all_tasks:
            max_retries = t.get("max_retries", 3)
            if t.get("status") == "FAILED" and t.get("retry_count", 0) >= max_retries:
                print(f"[STOP_LOSS] Tarea {t['id']} con {t['retry_count']} fallos consecutivos.")
                return True

        # S2: Checksum de artefacto alterado
        alerts = self.mm.get_integrity_alerts()
        if alerts:
            print(f"[STOP_LOSS] {len(alerts)} artefactos con checksum alterado.")
            return True

        # S3: Escritura fuera del workspace (pendiente de implementar)

        # S4: Tarea IN_PROGRESS sin checkpoint (pendiente de implementar)

        # S5: Acción irreversible sin RFC (pendiente de implementar)

        return False

    # ------------------------------------------------------------------
    # BITÁCORA (MISSION_CONTROL.md)
    # ------------------------------------------------------------------

    def _write_mission_control(self, message: str) -> None:
        """Añade una entrada a MISSION_CONTROL.md del proyecto."""
        mission_path = Path("workspace") / self.project_slug / "MISSION_CONTROL.md"
        mission_path.parent.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        entry = f"[{timestamp}] {message}\n"
        with open(mission_path, "a", encoding="utf-8") as f:
            f.write(entry)

    # ------------------------------------------------------------------
    # RECUPERACIÓN DESDE CHECKPOINT
    # ------------------------------------------------------------------

    def resume_from_checkpoint(self) -> bool:
        """Intenta restaurar el estado desde el último checkpoint."""
        if not self.project:
            self.load_project()
        checkpoint = self.mm.get_last_checkpoint(self.project["id"])
        if not checkpoint:
            return False
        state = json.loads(checkpoint["state_snapshot"])
        self.mm.write_state_json(self.project_slug, state)
        self._write_mission_control("Proyecto restaurado desde checkpoint.")
        return True

    # ------------------------------------------------------------------
    # CICLO PRINCIPAL
    # ------------------------------------------------------------------

    def run(self) -> ExecutionReport:
        """Ejecuta el ciclo Round‑Robin completo."""
        start = time.time()

        self.load_project()
        self._write_mission_control("Orquestador iniciado.")

        tasks_completed = 0
        tasks_failed = 0

        while True:
            queue = self.build_task_queue()
            if not queue:
                self._write_mission_control("Sin tareas READY. Ciclo finalizado.")
                break

            for task in queue:
                if self._should_stop():
                    self._write_mission_control("STOP_LOSS activado. Congelando cola.")
                    break

                task_id = task["id"]

                # Checkpoint antes de ejecutar
                state = self.mm.read_state_json(self.project_slug) or {}
                self.mm.write_checkpoint(
                    self.project["id"],
                    task_id,
                    "orchestrator",
                    0,
                    f"Despachando tarea {task_id} → {task['assigned_agent']}",
                    json.dumps(state),
                )

                self.mm.update_task_status(task_id, "IN_PROGRESS", "orchestrator")
                self._write_mission_control(
                    f"Tarea {task_id} → IN_PROGRESS ({task['assigned_agent']})"
                )

                try:
                    success = self._execute_task(task)

                    if success:
                        self.mm.update_task_status(task_id, "REVIEW", "orchestrator")
                        tasks_completed += 1
                        self._write_mission_control(
                            f"Tarea {task_id} → REVIEW (pendiente de QA)"
                        )

                        # Desbloquear dependencias
                        all_tasks = self.mm.get_ready_tasks(self.project_slug)
                        for t in all_tasks:
                            self.mm.unlock_task(t["id"])

                except Exception as e:
                    self._handle_failure(task, str(e))
                    tasks_failed += 1
                    self._write_mission_control(
                        f"Tarea {task_id} → ERROR: {str(e)}"
                    )

            if self._should_stop():
                break

        end = time.time()
        all_tasks = self.mm.get_project_status(self.project_slug)
        total = all_tasks[0]["total_tasks"] if all_tasks else 0

        report = ExecutionReport(
            project=self.project_slug,
            tasks_completed=tasks_completed,
            tasks_failed=tasks_failed,
            tasks_pending=total - tasks_completed - tasks_failed,
            stop_loss_triggered=self._should_stop(),
            hitl_required=self.hitl_required,
            duration_seconds=round(end - start, 2),
            timestamp=datetime.now(timezone.utc).isoformat(),
        )

        self._write_mission_control(f"Orquestador finalizado. Reporte: {report}")
        return report