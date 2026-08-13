# memory
## Propósito y Funcionalidad
Este documento regula las instrucciones vinculantes para interactuar correctamente con la capa de persistencia estricta del framework. La lectura del núcleo descansa enteramente en llamadas unívocas al puente `memory_manager.py` más las variables operativas subidas a su respectivo `state.json`.

## Reglas de Persistencia

### 1. Cuándo leer `state.json`
El agente asume el estatus del entorno SIEMPRE despuntando el arranque y el proceso iniciático de una tarea. Previo a iniciar siquiera una labor, debe extraer y leer minuciosamente toda la panorámica registrada previamente del proyecto en `output/[proyecto]/state.json`.

### 2. Checkpoints Obligatorios (Pre-Condición)
La regla suprema manda registrar su estatus inminente y la intencionalidad material o técnica escribiendo obligatoriamente en la memoria del core como un **checkpoint ANTES de ejecutar código o emitir su siguiente paso funcional**. Está terminantemente proscrito escribir esto terminada la labor; debe preceder siempre.

### 3. Registro y Adición de Artefactos
Su tarea se cierra emitiendo siempre esta huella obligatoria para el marco y la revisión posterior:
Debe codificarse de esta manera exacta su paso a producción final interactuando con las firmas dadas por la BD:
`mm.register_artifact(task_id, project_id, file_path, file_type, metadata)` (Donde metadata porta el JSON final).

### 4. Actualizar Estado de una Tarea
Si un status del ecosistema cambia la estipulación lógica o cumple el cometido encomendado, debe obligatoriamente notificar al orquestador informándole de un cierre o eventual de la actividad mediante una llamada estricta sobre la clase del manager:
`mm.update_task_status(task_id, new_status, agent_name, model_used)`

### Fallos Críticos (`MemoryManagerError`)
Si el framework retorna el volcado del sistema por una advertencia de bloqueo rotundo ante lectura o grabado fallido como un `MemoryManagerError`: el agente se ve incapacitado y cesa en estricto acato activando escalamiento (HITL). Se detiene el motor completo y se solicita aval perentorio del operador sobre los `execution_logs`.
