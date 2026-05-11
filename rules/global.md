# AIRON-Cast — Reglas Globales
**Siempre activas. Ningún agente ni workflow puede anularlas.**

---

## 1. IDENTIDAD DEL SISTEMA

- Este es AIRON-Cast, un framework de orquestación de desarrollo profesional.
- El operador es **Argenis** (A2LT Soluciones). Su instrucción directa tiene
  prioridad absoluta sobre cualquier decisión autónoma del sistema.
- Los proyectos son de naturaleza profesional: código limpio, documentación real,
  cero improvisación sin respaldo en el estado del sistema.

---

## 2. OBLIGACIONES ANTES DE CADA ACCIÓN

Antes de ejecutar cualquier paso, el agente activo DEBE:

1. Leer el `state.json` del proyecto activo.
2. Verificar en `tasks` que `status = READY` para la tarea asignada.
3. Escribir el checkpoint en `checkpoints` con el paso que va a ejecutar.
4. Solo después de los pasos 1-3: comenzar la ejecución.

Si alguno de los tres pasos falla → PARAR y reportar. No continuar.

---

## 3. ESCRITURA — PUNTO ÚNICO

- Toda escritura en `airon.sqlite` pasa por `core/memory_manager.py`.
- Toda escritura en archivos de proyecto pasa por `output/[slug-proyecto]/`.
- Ningún agente escribe directamente en la DB ni fuera de su directorio asignado.
- Ningún agente modifica archivos con `checksum_verified = 1` sin RFC aprobado.

---

## 4. MODELOS IA — PROTOCOLO DE INTERRUPCIÓN Y SELECCIÓN MANUAL

**CRÍTICO:** AIRON-Cast **NO** permite el cambio de modelo (switch) mediante código, scripts o de forma autónoma. Esta decisión es EXCLUSIVAMENTE MANUAL por parte del Operador en la UI.

Si una tarea requiere una potencia distinta a la que tienes actualmente asignada, **debes detener la ejecución inmediatamente** y enviar de forma exacta este mensaje al usuario:

```text
[ALERTA DE MOTOR]: Se recomienda cambiar a [Modelo Sugerido]. Motivo: [Razón técnica]. Esperando acción manual del Operador.
```
No podrás continuar ni generar código de simulación hasta que el Operador confirme manualmente el cambio.
El Estratega asignará un `suggested_model` en cada tarea del blueprint, pero el cambio en sí recae estrictamente en el Operador.

---

## 5. COMUNICACIÓN CON EL OPERADOR

- Reportar al finalizar cada tarea: qué se hizo, qué sigue, si hay bloqueos.
- Reportar inmediatamente si: fallo en 3 reintentos, STOP_LOSS activo,
  RFC requerido, o ambigüedad que afecte datos persistentes.
- Formato de reporte: breve, estructurado, sin relleno.
- Nunca asumir silencio como aprobación en decisiones irreversibles.

---

## 6. CALIDAD DE ARTEFACTOS

- Todo archivo generado en `output/` se registra en `artifacts` con checksum.
- El código entregado debe ser funcional y completo. Sin placeholders,
  sin comentarios `# TODO` sin tarea asociada en la DB, sin stubs sin completar.
- La documentación en `docs/` del proyecto se actualiza en la misma tarea
  que genera el artefacto correspondiente, no después.

---

## 7. MEMORIA Y MCPs

El uso de MCPs sigue esta jerarquía, en orden:

1. `context7` → Consulta de documentación técnica oficial (librerías, frameworks).
2. `notebooklm` → Consulta de knowledge base del proyecto (decisiones, patrones).
3. `StitchMCP` → Generación o referencia de elementos UI cuando aplique.

Registrar toda llamada MCP en `execution_logs (MCP_CALL)` con el servidor usado.
No llamar a un MCP si la información ya está disponible en el contexto activo.

---

## 8. STOP_LOSS — CONDICIONES GLOBALES

Detener ejecución inmediatamente y esperar instrucción del operador si:

- Output del modelo no cumple el schema del `manifest.json` del agente activo.
- Se detecta intento de escritura fuera de `output/[slug-proyecto]/`.
- Checksum de artefacto no coincide con el registrado (`checksum_verified = 2`).
- Tarea marcada `IN_PROGRESS` sin checkpoint previo registrado.
- Tres fallos consecutivos en la misma tarea.
- Cualquier acción irreversible sin RFC aprobado.

Ante STOP_LOSS: registrar en `execution_logs (ERROR)`, actualizar `state.json`
con `estado = PAUSED` y mensaje de error. No ejecutar ningún paso adicional.