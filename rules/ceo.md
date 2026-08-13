# CEO Rules — AIRON‑Cast Límites Operativos

> **Naturaleza:** Reglas estrictas de cumplimiento automático.  
> **Jerarquía:** Por encima de cualquier perfil de agente o workflow.  
> **Audiencia:** Orquestador, agentes del taskforce y scripts del ecosistema.

---

## 1. Límites Absolutos

### 1.1 Presupuesto: $0
- **API de pago prohibida.** Solo se permite el uso de modelos gratuitos (Nvidia DeepSeek V4 preview, fallbacks definidos en `api_router.py`).
- **Caché obligatoria:** antes de invocar cualquier modelo, verificar `response_cache` mediante `api_router.check_cache()`.
- **Notificación de modelo sugerido:** si una tarea requiere un modelo más potente, se notificará al Operador sin detener el proceso (ver §4). El cambio de modelo siempre es manual.

### 1.2 RAM máxima: 16 GB
- **Máximo 1 agente activo** (Round‑Robin) + **1 script Python simultáneo**.
- No se permite la ejecución de modelos locales (Ollama, LM Studio) dentro del ecosistema.
- El orquestador monitorizará el uso de memoria; si se excede el 80% (12.8 GB), pausará la cola y notificará al Operador.

### 1.3 Sin vectores externos
- Solo se utiliza SQLite con FTS5 para búsqueda semántica.
- No se deben instalar bases de datos vectoriales (ChromaDB, Pinecone, etc.).

---

## 2. Escritura y Persistencia

### 2.1 Punto único de acceso a datos
Toda lectura y escritura en `central_intelligence.db` se canaliza exclusivamente a través de `core/memory_manager.py`. Ningún agente, script o herramienta puede abrir una conexión directa a la base de datos.

**Excepción documentada:** `tools/dashboard_server.py` abre conexiones de solo lectura
directamente contra SQLite para servir el panel de monitoreo (`dashboard/index.html`).
Esta herramienta no es un agente del ecosistema, no realiza escrituras, y solo se ejecuta
bajo demanda del Operador en un entorno local. Es la única excepción permitida a esta regla.

### 2.2 Archivos de proyecto
La escritura de artefactos generados está confinada a `workspace/<slug>/src/`. Cualquier intento de escritura fuera de este directorio activará STOP_LOSS.

### 2.3 Protección de artefactos verificados
Un artefacto con `checksum_verified = 1` (íntegro) **no puede ser modificado** sin un RFC aprobado por el Operador. Si se requiere un cambio, se debe crear un nuevo artefacto y marcar el anterior como obsoleto.

### 2.4 Formato de estado
- `state.json`: minúsculas, claves en inglés (`status`, `current_task`, `error_message`).
- `MISSION_CONTROL.md`: entradas con timestamp UTC, formato `[YYYY-MM-DD HH:MM:SS UTC] [AGENTE] mensaje`.
- `BACKLOG.md`: estados de tarea en inglés (`TODO → DOING → DONE → BLOCKED`).

---

## 3. Ciclo de Tareas y Reintentos

### 3.1 Flujo de estados
```
LOCKED → READY → IN_PROGRESS → REVIEW → COMPLETED
                                  ↓
                               FAILED (si ≥3 reintentos)
```

### 3.2 Reintentos
- Máximo **3 reintentos** por tarea.
- En cada reintento, el orquestador debe inyectar el error anterior en el contexto del agente.
- Al tercer fallo consecutivo, la tarea pasa a `FAILED`, se notifica al Operador (HITL) y se congelan las tareas dependientes.

### 3.3 Desbloqueo de dependencias
Una tarea se mueve de `LOCKED` a `READY` automáticamente cuando todas sus dependencias están en `COMPLETED`. El orquestador invocará `memory_manager.unlock_task()` para ello.

---

## 4. Modelos IA y Notificaciones

### 4.1 Cambio de modelo manual
**AIRON‑Cast no permite el cambio automático de modelo.** Esta decisión es exclusiva del Operador. Si una tarea sugiere un modelo distinto (`suggested_model`), `api_router.py` imprimirá una notificación visible:

```
[ALERTA DE MOTOR]: Se recomienda cambiar a [Modelo Sugerido].
Motivo: [Razón técnica].
Acción manual requerida por el Operador.
```

El proceso no se detiene. El agente continuará con el modelo actual. Si el Operador decide cambiar, lo hará manualmente en la interfaz de su IDE.

### 4.2 Registro de uso de modelos
Cada llamada a un modelo se registra en `execution_logs` con:
- `model_used`
- `prompt_hash` (para cacheo)
- `tokens_used`
- `duration_ms`

---

## 5. Integridad y Calidad

### 5.1 Checksum obligatorio
Todo artefacto generado en `workspace/<slug>/src/` debe registrarse en la tabla `artifacts` con checksum SHA256 (`memory_manager.register_artifact()`). El `qa_auditor` verificará la integridad antes de cualquier aprobación.

### 5.2 Código sin placeholders
No se permite código con `# TODO`, `FIXME`, stubs sin implementar o funciones vacías. Si una tarea no puede completarse, debe marcarse como `FAILED` con una descripción clara del motivo.

### 5.3 Documentación sincrónica
La documentación (`REQUIREMENTS.md`, `component-specs.md`) se actualiza en la misma tarea que genera el código correspondiente, no en una fase posterior.

---

## 6. STOP_LOSS — Condiciones de Parada Inmediata

El orquestador detendrá toda ejecución y notificará al Operador si ocurre cualquiera de las siguientes condiciones:

| # | Condición | Detección |
|---|---|---|
| S1 | 3 fallos consecutivos en la misma tarea | `tasks.retry_count >= tasks.max_retries` |
| S2 | Checksum de artefacto alterado | `artifacts.checksum_verified = 2` |
| S3 | Escritura detectada fuera de `workspace/<slug>/` | Monitor del orquestador |
| S4 | Tarea en `IN_PROGRESS` sin checkpoint previo | Validación antes de cada paso |
| S5 | Acción irreversible sin RFC aprobado | Verificación de ADR con `decision_id` |

### Procedimiento ante STOP_LOSS:
1. Congelar la cola de tareas del proyecto.
2. Registrar el evento en `execution_logs` con `outcome = 'failure'`.
3. Actualizar `state.json`: `{"status": "PAUSED", "error_message": "<diagnóstico>"}`.
4. Notificar al Operador con el diagnóstico completo.
5. No ejecutar ningún paso adicional hasta confirmación manual.

---

## 7. Prohibiciones Absolutas

- ❌ Usar APIs de pago.
- ❌ Ejecutar modelos locales (Ollama, LM Studio, etc.).
- ❌ Escribir directamente en `central_intelligence.db` sin pasar por `memory_manager`.
- ❌ Modificar artefactos con `checksum_verified = 1` sin RFC.
- ❌ Cambiar el estado de un proyecto (`ACTIVE`/`PAUSED`) automáticamente.
- ❌ Eliminar registros de `execution_logs`, `adrs` o `feedback_history`.
- ❌ Ejecutar más de un agente simultáneamente.
- ❌ Omitir la verificación de checksum en la revisión de QA.