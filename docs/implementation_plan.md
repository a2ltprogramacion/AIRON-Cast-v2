# Plan de Integración: Fusión de Agentes y Generación de Scripts

## Contexto

Se fusionarán los 12 agentes de `docs/agents/` con los 7 existentes en `.agent/agents/`, usando el template definido por `agent-creator-pro`. Se generarán los scripts de utilidad faltantes. Skills de `docs/skills/` **no se procesan** (esqueletos, pendiente de specs reales). RAG ignorado por ahora.

## Matriz de Mapeo Agent → Destino

| docs/agents/          | .agent/agents/ actual     | Acción              |
|-----------------------|---------------------------|---------------------|
| `agent_architect`     | `strategist.md`           | MERGE (enriquecer)  |
| `agent_backend`       | `taskforce/backend.md`    | MERGE               |
| `agent_frontend`      | `taskforce/frontend.md`   | MERGE               |
| `agent_uxui`          | `taskforce/ux.md`         | MERGE               |
| `agent_docs`          | `taskforce/docs.md`       | MERGE               |
| `agent_reviewer`      | `taskforce/qa.md`         | MERGE (reviewer+qa) |
| `agent_tester`        | —                         | NEW → `taskforce/tester.md` |
| `agent_pm`            | —                         | NEW → `pm.md`       |
| `agent_forge`         | —                         | NEW → `forge.md`    |
| `agent_ghl`           | —                         | NEW → `taskforce/ghl.md` |
| `agent_infra`         | —                         | NEW → `taskforce/infra.md` |
| `agent_writer`        | —                         | NEW → `taskforce/writer.md` |
| — (existente)         | `orchestrator.md`         | KEEP (ya completo)  |

---

## Cambios Propuestos

### Fase 1: Agentes — Fusión y Creación

#### Format Estándar (Agent Profile Template)

Todos los agentes seguirán este esquema unificado compatible con Antigravity y `agent-creator-pro`:

```markdown
# Agent Profile: <Nombre>

## 1. Core Identity
- **Role Name:** <nombre>
- **Primary Objective:** <misión en una oración>
- **Phase:** <Discovery | Design | Development | Testing | Review | Content | Delivery | Evolution>

## 2. Authorized Scope & Constraints
- **Allowed:** <operaciones permitidas>
- **Prohibited:** <operaciones prohibidas>

## 3. Rules
- R01 — ...
- R02 — ...

## 4. Assigned Skills
- <skill_name> → <descripción corta>

## 5. Orchestration & Handoff Protocol
- **Upstream:** <quién asigna trabajo>
- **Downstream:** <quién recibe output>
- **Trigger Condition:** <evento de activación>
- **Handoff Phrase (Success):** <frase exacta>
- **Handoff Phrase (Failure):** <frase exacta>

## 6. Output Contract
{ JSON schema }
```

#### Archivos a modificar (MERGE)

| Archivo | Fuente de enriquecimiento | Cambios clave |
|---------|--------------------------|---------------|
| [strategist.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/strategist.md) | `agent_architect` | Añadir Rules (R01-R05), Output Contract, Handoff Protocol |
| [backend.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/backend.md) | `agent_backend` | Añadir Rules, Skills list, Output Contract |
| [frontend.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/frontend.md) | `agent_frontend` | Añadir Rules, Output Contract |
| [ux.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/ux.md) | `agent_uxui` | Añadir Rules, Output Contract |
| [docs.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/docs.md) | `agent_docs` | Añadir Rules, Output Contract |
| [qa.md](file:///y:/Proyectos%20IA/AIRON-Cast/.agent/agents/taskforce/qa.md) | `agent_reviewer` | Fusionar reviewer + qa, añadir verdicts |

#### Archivos nuevos (NEW)

| Archivo | Rol |
|---------|-----|
| `.agent/agents/pm.md` | Product Manager — user stories, tickets, backlogs |
| `.agent/agents/forge.md` | Forge Engineer — meta-programación del ecosistema |
| `.agent/agents/taskforce/tester.md` | QA Test Engineer — ejecutor de tests y lint |
| `.agent/agents/taskforce/ghl.md` | GoHighLevel Specialist — API v2 ops |
| `.agent/agents/taskforce/infra.md` | Infrastructure — materialización, migraciones, env |
| `.agent/agents/taskforce/writer.md` | Copywriter & SEO — copy, emails, meta tags |

---

### Fase 2: Scripts de Utilidad

Generar en `.agent/scripts/`:

| Script | Función |
|--------|---------|
| `generate_agent_profile.py` | Genera `.md` desde CLI flags usando la plantilla |
| `validate_agent_profile.py` | Valida estructura regex contra el template |
| `list_agents.py` | Lista todos los agentes con su handoff geometry |

---

### Fase 3: Verificación

1. Validar todos los agentes con `validate_agent_profile.py`
2. Ejecutar tests existentes (`test_memory_manager.py`, `test_core_integration.py`)
3. Confirmar que `manifest.json` no tiene conflicts con los nuevos agentes

---

## Notas

> [!WARNING]
> Las skills referenciadas en los agentes (ej. `skill_gen_django_app`) son **placeholders**. No se crearán hasta que el Operador provea las specs reales.

> [!NOTE]
> Las referencias RAG (`project_context`, `task_memory`) se marcarán como `TODO — pendiente infraestructura vectorial`.
