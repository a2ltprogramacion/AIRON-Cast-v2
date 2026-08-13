---
description: Protocolo de auto-mantenimiento donde el Orchestrator detecta errores recurrentes, el meta_factory propone parches, el Operador los aprueba, el qa_auditor los valida en sandbox y el meta_factory los despliega de forma segura.
---

# Workflow: Auto-Mantenimiento del Ecosistema (System)

**Propósito:** Protocolo seguro para que AIRON‑Cast se auto-corrija y evolucione
sin intervención directa del Operador sobre archivos core.
**Tipo:** system
**Duración estimada:** Variable (detección → parche → validación → despliegue)
**Activa:** `meta_factory` al detectar patrones en `feedback_history` con
`recurrence_count > 2`, o por solicitud explícita del Operador.

---

## 1. Arquitectura de Auto-Mantenimiento

AIRON‑Cast aplica el principio de "shadow work": los cambios se diseñan, prueban
y validan en un espacio aislado (`workspace/.system-lab/`) antes de aplicarse al
ecosistema productivo. Ningún archivo en `.agents/` o `core/` se modifica sin
pasar por este ciclo.

**Agentes involucrados:**

| Orden | Agente | Rol en el workflow |
|-------|--------|--------------------|
| 1 | `meta_factory` | Detecta patrones, propone parches, ejecuta cambios aprobados |
| 2 | `qa_auditor` | Valida que los cambios no introduzcan errores |
| — | **Operador** | Aprueba/rechaza cada parche |

**Orchestrator** supervisa el ciclo sin ejecutar modificaciones. Su rol es
despachar tareas entre `meta_factory` y `qa_auditor` en orden Round‑Robin.

---

## 2. Flujo de Auto-Mantenimiento

```
┌─────────────────────────────────────────────────────────────┐
│ FASE 0: MONITOREO CONTINUO                                  │
│ - Orchestrator verifica feedback_history periódicamente     │
│ - Si detecta (error_type, affected_agent) con               │
│   recurrence_count > 2 → activa meta_factory               │
│ - Operador también puede activar manualmente                │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 1: DIAGNÓSTICO Y PROPUESTA (meta_factory)             │
│ - Analiza la causa raíz del error recurrente                │
│ - Invoca brainstorming para evaluar enfoques                │
│ - Diseña el parche (modificación al perfil .md o SKILL.md)  │
│ - Prepara diagnóstico estructurado:                         │
│   * Componente afectado                                     │
│   * Causa raíz                                              │
│   * Corrección propuesta                                    │
│   * Impacto esperado                                        │
│ - Presenta al Operador y espera aprobación                  │
│ - Escribe checkpoint en central_intelligence.db             │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 2: APROBACIÓN DEL OPERADOR (HITL)                     │
│ - Operador revisa diagnóstico                               │
│ - Responde: "Aprobado", "Ajustar: [detalle]", "Rechazado"   │
│ - Si es rechazado → se registra ADR con motivo              │
│ - Si requiere ajustes → meta_factory itera (máx 2 rondas)   │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 3: SHADOW WORK (meta_factory)                          │
│ - Copia el archivo a modificar en workspace/.system-lab/    │
│ - Aplica el parche en la copia aislada                      │
│ - Registra checksum del archivo original (para rollback)    │
│ - NO modifica el archivo productivo todavía                 │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 4: VALIDACIÓN EN SANDBOX (qa_auditor)                  │
│ - Recibe la copia modificada en .system-lab/                │
│ - Ejecuta yaml-validator sobre el frontmatter               │
│ - Verifica que no haya referencias rotas a skills o agents  │
│ - Valida checksum del archivo modificado                    │
│ - Emite veredicto: APPROVED / REJECTED                      │
│   * Si REJECTED → devuelve a FASE 1 con hallazgos           │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ FASE 5: DESPLIEGUE CONTROLADO (meta_factory)                │
│ - Reemplaza archivo productivo con versión validada         │
│ - Incrementa version en frontmatter                         │
│ - Actualiza manifest.json (vía manifest-updater)            │
│ - Escribe ADR documentando el cambio                        │
│ - Registra entrada en journal (vía journal-writer)          │
│ - Resetea recurrence_count en feedback_history              │
│ - Elimina archivos temporales de .system-lab/               │
└─────────────────────────────────────────────────────────────┘
```

---

## 3. Condiciones de Stop‑Loss

El Orchestrator detiene el workflow si:

- `qa_auditor` encuentra `CRITICAL` en la validación (no se despliega).
- El Operador rechaza el parche dos veces consecutivas (se registra ADR y se archiva).
- El checksum del archivo productivo cambia durante el shadow work (posible
  modificación externa → HITL inmediato).
- Cualquier agente del ciclo falla 3 veces consecutivas (R04 del Orchestrator).

---

## 4. Espacio de Shadow Work

```
workspace/.system-lab/
├── [YYYYMMDD-HHMMSS]_[component-name]/
│   ├── original/          ← copia del archivo antes del parche
│   │   └── [file].md
│   ├── patched/           ← versión modificada para validación
│   │   └── [file].md
│   └── validation.json    ← resultado de qa_auditor
└── archive/               ← parches aplicados históricos
```

Este espacio se limpia automáticamente tras cada despliegue exitoso. Solo se
conserva `archive/` como historial.

---

## 5. Roles y Responsabilidades

| Responsabilidad | Agente |
|-----------------|--------|
| Detectar patrones en feedback_history | Orchestrator |
| Diagnosticar y proponer parches | meta_factory |
| Aprobar o rechazar cambios | Operador (Argenis) |
| Validar parches en sandbox | qa_auditor |
| Desplegar cambios aprobados | meta_factory |
| Documentar en ADR y journal | meta_factory |
| Supervisar el ciclo completo | Orchestrator |

---

> *"No automatices el caos. Orquesta con memoria."*
> — AIRON‑Cast Manifesto, v1.0.0
