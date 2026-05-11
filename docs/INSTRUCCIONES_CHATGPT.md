# Instrucciones para ChatGPT (GPT-4o) — AIRON-Cast Integración y Tests
**Lee primero:** `HANDOFF_CONTEXT.md` completo antes de continuar.

---

## Por qué tú

ChatGPT tiene mejor capacidad que otros modelos para escribir tests de
integración complejos que cruzan múltiples módulos, y para el `orchestrator.py`
que es el archivo más complejo del core — requiere razonamiento sobre flujo
de control, manejo de estados y comunicación entre componentes.

---

## Tu asignación: 4 archivos

### 1. `core/orchestrator.py`

**Propósito:** Motor de ejecución que conecta todo el sistema. Lee workflows,
gestiona la cola de tareas, activa agentes en orden y maneja el loop
completo de ejecución.

**Contrato de diseño:**

```python
class Orchestrator:
    def __init__(self, project_slug: str, workflow_path: str)
    def load_workflow(self) -> dict          # Lee el .md del workflow
    def build_task_queue(self) -> list       # Consulta v_ready_tasks
    def run(self) -> ExecutionReport         # Loop principal
    def _execute_task(self, task: dict) -> bool
    def _handle_failure(self, task: dict, error: str) -> None
    def _should_stop(self) -> bool           # Verifica condiciones STOP_LOSS
    def resume_from_checkpoint(self) -> bool # Para recuperación tras fallo
```

**El loop principal `run()` debe:**
1. Cargar workflow del archivo `.md` correspondiente.
2. Verificar que el proyecto existe en la DB y está `ACTIVE`.
3. Obtener cola de tareas vía `mm.get_ready_tasks(project_slug)`.
4. Por cada tarea en cola:
   a. Escribir checkpoint (`mm.write_checkpoint`) ANTES de ejecutar.
   b. Actualizar task a `IN_PROGRESS`.
   c. Ejecutar la tarea (en esta versión: simular y loguear — la integración
      real con el LLM es fase siguiente).
   d. Validar output con `Validator`.
   e. Si OK: marcar `COMPLETED`, intentar desbloquear dependientes.
   f. Si FALLA: llamar a `_handle_failure` → reintento o HITL.
5. Al finalizar: generar `ExecutionReport` con resumen.

**`resume_from_checkpoint()`:**
- Lee `mm.get_last_checkpoint(project_id)`.
- Restaura el `state.json` desde el snapshot guardado.
- Retoma desde la tarea interrumpida.

**STOP_LOSS — el método `_should_stop()` retorna True si:**
- Hay una tarea `FAILED` con `retry_count >= max_retries`.
- Hay artefactos comprometidos en `v_integrity_alerts`.
- El `state.json` del proyecto tiene `estado = "PAUSED"`.

**`ExecutionReport` (dataclass o dict):**
```python
{
    "project": str,
    "tasks_completed": int,
    "tasks_failed": int,
    "tasks_pending": int,
    "stop_loss_triggered": bool,
    "hitl_required": bool,
    "duration_seconds": float,
    "timestamp": str
}
```

**Prueba obligatoria en `if __name__ == "__main__"`:**
- Crear un proyecto de prueba con 3 tareas (sin dependencias, con dependencias).
- Ejecutar el orchestrator.
- Verificar que el orden de ejecución respeta las dependencias.
- Simular fallo en tarea 2 y verificar que activa reintento.
- Verificar que el `ExecutionReport` tiene los valores correctos.

---

### 2. `tests/test_core_integration.py`

**Propósito:** Test de integración que verifica que todos los módulos del
`core/` funcionan juntos correctamente.

**Tests obligatorios:**

```python
class TestMemoryManagerIntegration:
    def test_project_lifecycle()     # create → active → completed
    def test_task_dependency_chain() # tarea B no pasa a READY hasta que A esté COMPLETED
    def test_checkpoint_before_step()# checkpoint siempre antes que IN_PROGRESS
    def test_artifact_checksum_cycle()# register → verify OK → modify → verify FAIL
    def test_hitl_escalation_flow()  # 3 fallos → HITL → resolve → READY

class TestValidatorIntegration:
    def test_valid_frontend_artifact()
    def test_missing_required_field()
    def test_invalid_severity_value()
    def test_qa_report_not_approved_is_still_valid()

class TestOrchestratorIntegration:
    def test_run_simple_workflow()
    def test_resume_from_checkpoint()
    def test_stop_loss_on_integrity_alert()
    def test_dependency_unlock_cascade()  # A→COMPLETED desbloquea B y C
```

**Reglas para los tests:**
- Usar una DB temporal en memoria: `sqlite3.connect(":memory:")`
- Aplicar el schema completo antes de cada test.
- Limpiar estado entre tests (`setUp`/`tearDown` o fixtures).
- No mockear `memory_manager.py` — usar la implementación real con DB temporal.
- Sí mockear llamadas externas a MCPs si las hay.
- Cada test debe ser independiente y reproducible.

---

### 3. `.gitignore`

**Contenido para un proyecto Python + SQLite + VSCode/Antigravity:**

Incluir secciones para:
- Python (`__pycache__`, `*.pyc`, `venv/`, `.env`, `*.egg-info`)
- SQLite (`*.sqlite`, `*.db`, `*.sqlite3`) — **EXCEPTO** `core/airon_cast_schema.sql`
  que sí debe versionarse.
- VSCode/Antigravity (`.vscode/settings.json` con tokens o claves locales)
- Output del sistema (`output/*/src/` puede ser pesado — configurar según tamaño)
- Archivos sensibles (`mcp_config.json` porque tiene API keys)
- Logs (`*.log`, `core/brain/`)
- Sistema operativo (`Thumbs.db`, `.DS_Store`)

---

### 4. `tests/test_memory_manager.py`

**Propósito:** Tests unitarios exhaustivos solo para `memory_manager.py`.

**Tests obligatorios:**

```python
class TestProjects:
    def test_create_project_success()
    def test_create_duplicate_slug_raises()
    def test_update_project_status_valid()
    def test_update_project_status_invalid_raises()
    def test_get_project_returns_dict()
    def test_get_nonexistent_project_returns_none()

class TestTasks:
    def test_create_task_starts_locked()
    def test_unlock_without_dependencies()
    def test_unlock_blocked_by_pending_dependency()
    def test_unlock_passes_when_dependency_completed()
    def test_update_status_retry_logic()    # 3 fallos → FAILED
    def test_update_status_second_fail_retries()

class TestArtifacts:
    def test_register_artifact_nonexistent_file_raises()
    def test_register_artifact_computes_checksum()
    def test_verify_intact_artifact_returns_true()
    def test_verify_modified_artifact_returns_false()
    def test_verify_updates_checksum_verified_field()

class TestCheckpoints:
    def test_write_checkpoint_returns_id()
    def test_get_last_checkpoint_returns_most_recent()
    def test_get_last_checkpoint_no_data_returns_none()
    def test_cleanup_keeps_only_10()       # trigger de limpieza automática

class TestStateJson:
    def test_write_and_read_roundtrip()
    def test_read_nonexistent_returns_none()
    def test_creates_directory_if_missing()

class TestViews:
    def test_v_project_status_progress_pct()
    def test_v_ready_tasks_filters_correctly()
    def test_v_integrity_alerts_detects_compromised()
```

---

## Reglas de entrega para ChatGPT

- Código Python completo, ejecutable, sin truncar.
- Tests usando `unittest` estándar (no pytest — para máxima compatibilidad).
  Si usas pytest, incluir la instalación en `requirements.txt`.
- El `orchestrator.py` importa desde `core/` asumiendo que se ejecuta desde
  la raíz del proyecto: `from core.memory_manager import MemoryManager`.
- No reinventar lo que ya existe en `memory_manager.py`. Reusar su API.
- El archivo `tests/test_core_integration.py` y `tests/test_memory_manager.py`
  deben poder ejecutarse con: `python -m pytest tests/` desde la raíz.

## Formato de entrega

```
### core/orchestrator.py
[código completo]

### tests/test_memory_manager.py
[código completo]

### tests/test_core_integration.py
[código completo]

### .gitignore
[contenido completo]
```
