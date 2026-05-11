# AIRON-Cast — Documento de Traspaso de Sesión
**Lee este archivo completo antes de ejecutar cualquier instrucción específica.**

---

## ¿Qué es AIRON-Cast?

**AIRON-Cast: Blacksmithing Development Framework**
A.I.R.O.N. = Artificial Intelligence Reinforced Orchestration Network

Framework de orquestación de desarrollo profesional construido sobre Antigravity
(fork de VSCode con integración nativa de agentes IA, corre local en la máquina
del operador). El operador es **Argenis** — desarrollador y consultor (A2LT Soluciones).

Actividades que cubre: diseño web, apps web/escritorio, administración GoHighLevel
(workflows, bots IA, snapshots), desarrollo backend, y soluciones personalizadas.

---

## Stack técnico confirmado

- **Entorno:** Antigravity (VSCode fork, local)
- **Modelos disponibles:** Gemini 3.1 Pro, Gemini 3 Flash, Claude Sonnet 4.6
  Thinking, Claude Opus 4.6 Thinking, GPT-OSS 120B
- **MCPs activos:** StitchMCP (UI generation, 8 tools), context7 (docs técnicas,
  2 tools), notebooklm (knowledge base, 32 tools)
- **DB:** SQLite (airon.sqlite) — corre local, sin servidor
- **Lenguaje core:** Python 3.x
- **Sin modelos locales** (hardware insuficiente para LM Studio u otros)
- **Sin API keys propias** — usa los modelos vía Antigravity nativo

---

## Estructura del proyecto

```
AIRON-Cast/
├── AGENTS.md                    ✅ COMPLETO
├── manifest.json                ✅ COMPLETO y validado (JSON)
├── requirements.txt             ⬜ VACÍO — pendiente
├── .gitignore                   ⬜ VACÍO — pendiente
├── rules/
│   └── global.md                ✅ COMPLETO
├── workflows/
│   ├── web-design.md            ⬜ VACÍO — pendiente
│   ├── web-app.md               ⬜ VACÍO — pendiente
│   ├── ghl-admin.md             ⬜ VACÍO — pendiente
│   ├── ghl-bot.md               ⬜ VACÍO — pendiente
│   ├── ghl-snapshot.md          ⬜ VACÍO — pendiente
│   ├── erp-pos.md               ⬜ VACÍO — pendiente
│   ├── custom.md                ⬜ VACÍO — pendiente
│   └── system.md                ⬜ VACÍO — pendiente
├── agents/
│   ├── strategist.md            ⬜ VACÍO — pendiente
│   ├── orchestrator.md          ⬜ VACÍO — pendiente
│   └── taskforce/
│       ├── frontend.md          ⬜ VACÍO — pendiente
│       ├── backend.md           ⬜ VACÍO — pendiente
│       ├── ux.md                ⬜ VACÍO — pendiente
│       ├── qa.md                ⬜ VACÍO — pendiente
│       └── docs.md              ⬜ VACÍO — pendiente
├── skills/
│   ├── memory/SKILL.md          ⬜ VACÍO — pendiente
│   ├── context7/SKILL.md        ⬜ VACÍO — pendiente
│   ├── notebooklm/SKILL.md      ⬜ VACÍO — pendiente
│   └── ghl/SKILL.md             ⬜ VACÍO — pendiente
├── core/
│   ├── airon_cast_schema.sql    ✅ COMPLETO y testeado
│   ├── memory_manager.py        ✅ COMPLETO — 9/9 pruebas OK
│   ├── validator.py             ⬜ VACÍO — pendiente
│   ├── hitl_gateway.py          ⬜ VACÍO — pendiente
│   ├── orchestrator.py          ⬜ VACÍO — pendiente
│   └── checksum_verifier.py     ⬜ VACÍO — pendiente
├── output/                      (carpeta vacía, aquí van los proyectos)
├── specs/                       (carpeta vacía)
└── docs/                        (carpeta vacía)
```

---

## Decisiones de arquitectura ya tomadas — NO reabrir

Estas decisiones están cerradas. No proponer alternativas ni reabrir debate:

1. **SQLite** (no PostgreSQL, no MongoDB) — corre sin servidor, ideal para local.
2. **state.json por proyecto** en `output/[slug]/state.json` — recuperación ante
   cortes de luz. El checkpoint se escribe ANTES de ejecutar cada paso.
3. **memory_manager.py como único punto de escritura** a la DB — ningún agente
   escribe directo.
4. **Tres círculos de autoridad:** strategist (análisis) → orchestrator (táctica)
   → taskforce (ejecución).
5. **manifest.json define jurisdicción** de cada agente — qué puede leer, escribir
   y qué MCPs puede invocar.
6. **Máx 3 reintentos** por tarea antes de FAILED + escalación HITL.
7. **Checksum SHA256** por cada artefacto generado — detecta modificaciones fuera
   del flujo.
8. **Selección de modelo por fase:** (Sugerido por Estratega) (análisis), (Sugerido por Estratega) (ejecución),
   (Sugerido por Estratega) (revisión), (Sugerido por Estratega) (arquitectura crítica).

---

## Schema SQL — tablas existentes

```
projects       → Registro de proyectos (slug, status, workflow, root_path)
tasks          → Máquina de estados LOCKED→READY→IN_PROGRESS→REVIEW→COMPLETED
artifacts      → Archivos generados con checksum SHA256
checkpoints    → Estado antes de cada paso (recuperación ante fallos)
execution_logs → Auditoría completa de todas las acciones
model_usage    → Qué modelo ejecutó cada decisión
```

Vistas disponibles:
```
v_project_status    → Panel de control con % de progreso
v_ready_tasks       → Cola de tareas listas
v_last_checkpoint   → Último punto de recuperación
v_integrity_alerts  → Artefactos con checksum alterado
```

---

## memory_manager.py — API disponible

```python
from core.memory_manager import MemoryManager
mm = MemoryManager()

# Proyectos
mm.create_project(slug, name, project_type, active_workflow, client, priority)
mm.update_project_status(slug, status)
mm.get_project(slug)

# Tareas
mm.create_task(project_id, title, assigned_agent, description, priority, dependencies)
mm.unlock_task(task_id)          # LOCKED → READY si dependencias cumplidas
mm.update_task_status(task_id, new_status, agent_name, model_used)

# Artefactos
mm.register_artifact(task_id, project_id, file_path, file_type, metadata)
mm.verify_artifact(artifact_id)  # Verifica checksum en disco

# Checkpoints
mm.write_checkpoint(project_id, task_id, agent_name, step_number, description, state_snapshot)
mm.get_last_checkpoint(project_id)

# State.json
mm.write_state_json(project_slug, state_dict)
mm.read_state_json(project_slug)

# Consultas
mm.get_project_status(slug=None)
mm.get_ready_tasks(project_slug=None)
mm.get_integrity_alerts()
```

---

## Principios de diseño — obligatorios para todo lo que se construya

1. **Sin truncar.** Código y documentos completos y funcionales desde la primera
   entrega. Sin `# TODO`, sin `pass`, sin placeholders.
2. **Sin inventar.** Si algo no está en este documento, preguntar antes de asumir.
3. **Sin reabrir decisiones cerradas.** Las decisiones del bloque anterior son
   definitivas.
4. **Verificar con prueba.** Todo archivo Python debe incluir un bloque
   `if __name__ == "__main__"` con prueba de uso básico que se pueda ejecutar.
5. **Consistencia de nombres.** Usar exactamente los mismos nombres de tablas,
   campos y métodos definidos en este documento.

---

## Contexto del operador

- Nombre: Argenis (A2LT Soluciones)
- Perfil: IT engineer, 10+ años en telecomunicaciones, Python/Django relativamente
  reciente, usa IA intensivamente para desarrollo.
- Estilo de trabajo: directo, funcional, sin relleno ni validación vacía.
- Tono esperado: técnico, preciso, sin elogios ni frases de cortesía innecesarias.
