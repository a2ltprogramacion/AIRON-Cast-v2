# Instrucciones para DeepSeek — AIRON-Cast Core Python
**Lee primero:** `HANDOFF_CONTEXT.md` completo antes de continuar.

---

## Por qué tú

DeepSeek maneja mejor que otros modelos gratuitos el código Python con lógica
de estado compleja, manejo de errores robusto y consistencia entre módulos.
Tu asignación es exclusivamente los archivos Python del `core/`.

---

## Tu asignación: 4 archivos Python

En este orden exacto — cada uno depende del anterior:

### 1. `core/validator.py`

**Propósito:** Validar que el output de cualquier agente cumpla con el
`output_schema` definido en `manifest.json` antes de que se escriba en disco
o en la DB.

**Contrato de diseño:**
- Lee `manifest.json` de la raíz del proyecto.
- Recibe: `agent_name (str)`, `output_dict (dict)`.
- Valida que las claves obligatorias del `output_schema` del agente existan
  y tengan el tipo correcto.
- Devuelve: `ValidationResult` con `passed: bool`, `errors: list[str]`.
- Si `passed = False` → NO lanza excepción, solo devuelve el resultado.
  Es responsabilidad del llamador decidir si hacer STOP_LOSS.
- Registra el resultado en `execution_logs` vía `MemoryManager`.

**Agentes a validar (sacar schemas de manifest.json):**
  strategist → blueprint, orchestrator → task_transition,
  frontend/backend/docs → artifact, ux → ux_report, qa → qa_report

**Prueba obligatoria en `if __name__ == "__main__"`:**
  - Validar un output correcto de `frontend` → debe pasar.
  - Validar un output con campo faltante → debe fallar con mensaje claro.
  - Validar un output de `qa` con `approved_for_delivery: False` → debe pasar
    (es válido, solo es una decisión de negocio, no un error de schema).

---

### 2. `core/hitl_gateway.py`

**Propósito:** Gestionar todas las escalaciones Human-in-the-Loop. Es el punto
de parada cuando el sistema no puede auto-resolver.

**Contrato de diseño:**
- Recibe un evento de escalación con: `project_id`, `task_id`, `agent_name`,
  `reason` (debe ser una de las condiciones definidas en `manifest.json → hitl`),
  `context` (dict con información del estado actual).
- Acciones que ejecuta siempre al escalarse:
  1. Actualiza `tasks.status = 'REVIEW'` en la DB vía MemoryManager.
  2. Escribe en `execution_logs` con `action_type = 'HITL_ESCALATION'`.
  3. Actualiza `state.json` del proyecto con `estado = 'PAUSED'` y
     `hitl_reason = reason`.
  4. Genera un archivo `output/[slug]/HITL_[timestamp].md` con el reporte
     completo del problema (qué pasó, qué necesita decidir Argenis,
     opciones disponibles).
- Método `resolve(task_id, decision: str, approved_by: str)` para cuando
  Argenis retoma: registra la decisión, devuelve la tarea a `READY`.

**Condiciones de escalación válidas** (exactamente estas, del manifest.json):
  - "Tres fallos consecutivos en la misma tarea"
  - "STOP_LOSS activado"
  - "RFC pendiente de aprobación"
  - "Cambio arquitectural detectado"
  - "Integridad de artefacto comprometida (checksum_verified = 2)"
  - "Ambigüedad en spec.md que afecte decisiones irreversibles"

**Prueba obligatoria en `if __name__ == "__main__"`:**
  - Simular escalación por "Tres fallos consecutivos".
  - Verificar que se genera el archivo HITL_*.md.
  - Simular resolución con `resolve()`.
  - Verificar que la tarea vuelve a READY.

---

### 3. `core/checksum_verifier.py`

**Propósito:** Módulo especializado en verificación de integridad de artefactos.
Extiende la capacidad de checksum que ya existe en `memory_manager.py`.

**Contrato de diseño:**
- `verify_project_artifacts(project_slug: str) -> VerificationReport`:
  Verifica TODOS los artefactos de un proyecto y devuelve reporte con:
  `total`, `verified_ok`, `compromised: list[dict]`, `missing: list[dict]`.
- `verify_single(artifact_id: int) -> bool`:
  Delega a `mm.verify_artifact()` — no duplicar lógica SHA256.
- `generate_integrity_report(project_slug: str) -> str`:
  Genera `output/[slug]/docs/integrity-report.md` con el resultado.
- Si encuentra artefactos comprometidos → llama a `HITLGateway.escalate()`
  con reason = "Integridad de artefacto comprometida (checksum_verified = 2)".

**Prueba obligatoria en `if __name__ == "__main__"`:**
  - Crear archivo temporal, registrarlo como artefacto, verificar OK.
  - Modificar el archivo, verificar de nuevo → debe detectar compromiso.
  - Generar reporte y verificar que el archivo .md se creó.

---

### 4. `core/requirements.txt`

**Contenido exacto requerido** (solo dependencias confirmadas, sin inventar):
```
sqlite3          ← builtin, no incluir
pathlib          ← builtin, no incluir
pydantic>=2.0    ← para validación de schemas en validator.py
python-dotenv    ← para variables de entorno
```

Listar solo lo que los 4 archivos Python realmente importan.
Revisar los imports de `memory_manager.py` (usa: sqlite3, json, hashlib, os,
datetime, pathlib — todos builtins, no van al requirements.txt).

---

## Reglas de entrega

- Cada archivo: completo, funcional, sin truncar.
- Sin `# TODO` sin tarea asociada.
- Sin imports que no se usen.
- Los 4 archivos deben poder coexistir sin conflictos de importación circular.
- Importar `MemoryManager` así: `from core.memory_manager import MemoryManager`
- El proyecto se ejecuta desde la raíz de `AIRON-Cast/`, no desde `core/`.

---

## Formato de entrega

Entrega cada archivo en un bloque de código separado con su ruta:

```
### core/validator.py
[código completo]

### core/hitl_gateway.py
[código completo]

### core/checksum_verifier.py
[código completo]

### requirements.txt
[contenido completo]
```
