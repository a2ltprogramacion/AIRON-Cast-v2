---
name: journal-writer
version: 2.0.0
type: utility
subtype: skill
tier: all
description: |
  Core skill que escribe y gestiona la memoria institucional de AIRON‑Cast.
  Se activa al completar una tarea, resolver un problema, tomar una decisión
  arquitectónica, detectar un patrón o registrar feedback de campo.
  Escribe entradas estructuradas en el workspace del proyecto activo.
  Trigger phrases: "registra en el journal", "guarda esta decisión",
  "escribe la entrada", "log this", "journal entry".
  No usar para notas temporales (viven en MISSION_CONTROL.md o state.json).
triggers:
  primary: ["journal", "registra", "guarda decisión", "log this"]
  secondary: ["entrada de journal", "patrón detectado"]
  context: ["cierre de tarea", "problema resuelto", "field feedback"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - orchestrator
  - meta_factory
last_used: 2026-06-03
scope: restricted
---

# Journal Writer — Memoria Institucional de AIRON‑Cast

This skill is the write interface to AIRON‑Cast's institutional memory.
It produces structured Markdown journal entries that are human-readable,
searchable via SQLite FTS5, and evolvable over time.

Read this document completely before writing any entry.

---

## 0. Principios del Journal

- **Entradas permanentes.** Never delete or overwrite entries — append corrections
  as new entries referencing the original by filename.
- **Un problema = una entrada.** Do not bundle multiple unrelated issues.
- **Confirmación para juicio.** Entries requiring architectural judgment (adr, pattern, field)
  are presented to the operator before persisting. Factual entries (task, problem) are
  written automatically.
- **Buscar antes de escribir.** Before writing an `adr` or `pattern` entry, query the
  memory database (via `memory_manager`) to check if a similar decision or pattern
  already exists. If it does, reference it — don't duplicate.

---

## 1. Estructura del Sistema de Journal

```
workspace/<project-slug>/journal/
├── .task-counter.json       ← contador de tareas + umbral de reporte
├── entries/                 ← todas las entradas (task, problem, adr, pattern, field)
└── reports/                 ← reportes auto-generados
```

**Filename convention:**
```
[YYYYMMDD-HHMMSS]_[type]_[slug].md
```

Examples:
- `20260603-143022_task_orchestrator-v1.md`
- `20260603-150845_problem_sqlite-lock-contention.md`
- `20260603-162300_adr_fts5-search-strategy.md`

---

## 2. Tipos de Entrada y Sus Plantillas

### 2.1 Tipo: `task`
**Cuándo:** Al completar exitosamente una tarea por un agente.
**Confirmación:** None — se escribe directamente.

Load template: `assets/templates/task.md`

Required fields:
- `agent_name` — agent that completed the task
- `task_description` — what was accomplished
- `skills_used` — list of skills invoked
- `duration_minutes` — approximate task time
- `output_artifacts` — list of generated files
- `notes` — any relevant operational observations

### 2.2 Tipo: `problem`
**Cuándo:** Cuando un agente encuentra un error, un `[ALTO]` se dispara, o el operador reporta un problema.
**Confirmación:** None — se escribe directamente.

Load template: `assets/templates/problem.md`

Required fields:
- `title` — concise problem statement (max 80 chars)
- `context` — what was being attempted
- `root_cause` — diagnosed cause
- `solution` — exact steps that resolved it
- `mitigation` — what was changed to prevent recurrence
- `affected_components` — list of skills/agents affected
- `severity` — low | medium | high | critical
- `recurrence_risk` — low | medium | high

### 2.3 Tipo: `adr` (Architectural Decision Record)
**Cuándo:** Cuando se toma una decisión arquitectónica significativa.
**Confirmación:** Required — se presenta al operador antes de persistir.

Load template: `assets/templates/adr.md`

Required fields:
- `title` — decision statement (max 100 chars)
- `context` — what situation forced this decision
- `decision` — what was chosen
- `alternatives_considered` — list of options evaluated
- `reasoning` — why this option was selected
- `consequences` — known trade-offs or future implications
- `status` — accepted | superseded | deprecated
- `supersedes` — filename of previous ADR if this replaces one

### 2.4 Tipo: `pattern`
**Cuándo:** When the same problem or solution appears 2+ times across different
components or projects.
**Confirmación:** Required — present to operator before persisting.

Load template: `assets/templates/pattern.md`

Required fields:
- `title` — pattern name (concise, action-oriented)
- `description` — what this pattern is and when it applies
- `evidence` — list of journal entry filenames that exhibit this pattern
- `recommendation` — concrete action to apply or avoid this pattern
- `applies_to` — skill types or contexts where this pattern is relevant
- `first_seen` — date of earliest evidence entry

### 2.5 Tipo: `field`
**Cuándo:** When a skill or agent is used in a real project and produces
observable results.
**Confirmación:** Required — present to operator before persisting.

Load template: `assets/templates/field.md`

Required fields:
- `skill_or_agent` — component name from manifest
- `project_context` — type of project (describe by industry/use case, no client names)
- `usage_description` — what the component was used for
- `outcome` — what actually happened
- `friction_points` — any confusion, errors, or complaints
- `suggested_improvement` — concrete change based on this experience
- `operator_rating` — 1-5

---

## 3. Flujo de Escritura

### Para entradas automáticas (task, problem):

```
1. Collect required fields from current task context
2. Load corresponding template from assets/templates/
3. Populate all fields — no empty fields allowed
4. Run: python scripts/journal_write.py --type task|problem --payload '<json>'
5. Confirm entry_path in output
6. Increment task counter (task type only)
7. Check if report threshold reached → generate report if yes
```

### Para entradas con confirmación (adr, pattern, field):

```
1. Query memory database for duplicates or related entries
2. Collect required fields from context
3. Load template and populate all fields
4. PAUSE — present formatted entry to operator with:
   "He preparado esta entrada de journal. ¿La guardamos tal cual, la ajustas, o la descartamos?"
5. On operator approval: run journal_write.py
6. On adjustment: incorporate changes, re-present once, then save
7. On discard: log reason in state.json
```

---

## 4. Contador de Tareas y Reportes Automáticos

The `.task-counter.json` file tracks task completions and triggers pattern reports:

```json
{
  "total_tasks": 0,
  "report_threshold": 10,
  "last_report_at": 0,
  "last_report_file": null
}
```

**Trigger logic:**
- On every successful `task` entry: increment `total_tasks`
- If `total_tasks - last_report_at >= report_threshold`: generate pattern report
- Update `last_report_at` after report generation

---

## 5. Scripts de Soporte

### `journal_write.py`
Writes a new journal entry from a JSON payload and template.

```bash
python scripts/journal_write.py \
  --type task|problem|adr|pattern|field \
  --payload '<json>'
```

### `journal_report.py`
Generates a pattern report from all entries since the last report.

```bash
python scripts/journal_report.py \
  [--project-slug landing-01] \
  [--since-entry <filename>]
```

### `journal_query.py`
Text-based search across journal entries.

```bash
python scripts/journal_query.py \
  --term "fts5" \
  --type problem \
  [--project-slug landing-01]
```

---

## 6. Integración con Memoria

Journal entries are indexed by SQLite FTS5 for semantic search.
The `memory_manager` module indexes `workspace/<project>/journal/entries/`
on every write via the `trajectory_compressor`.

Query prefix for journal entries: `[JOURNAL]` — included in each entry's header.
`pattern` and `adr` types have the highest retrieval value;
`task` entries are primarily for audit.

---

## 7. Referencias Rápidas

- `references/report_structure.md` — Pattern report format and section guide
- `references/entry_examples.md` — Filled examples of each entry type