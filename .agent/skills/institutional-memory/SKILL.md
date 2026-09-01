---
name: institutional-memory
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Memoria institucional de AIRON‑Cast. Permite consultar decisiones
  arquitectónicas, patrones de solución y lecciones aprendidas almacenadas
  en el ecosistema (ADRs y journal), así como registrar nuevas soluciones
  no triviales. Activar cuando se necesite buscar precedentes técnicos,
  soluciones a problemas difíciles o documentar una decisión importante.
  Trigger phrases: "busca en la base de conocimiento", "¿cómo resolvimos
  esto antes?", "consulta histórica", "registra esta solución",
  "lecciones aprendidas", "memoria institucional".
  No activar para registrar tareas rutinarias o interactuar con Google
  NotebookLM (usar `notebooklm-mcp-integration` para eso).
triggers:
  primary: ["base de conocimiento", "busca en la memoria institucional", "consulta histórica"]
  secondary: ["lecciones aprendidas", "cómo resolvimos", "registra solución"]
  context: ["institutional memory", "knowledge base", "ADR"]
dependencies:
  - name: journal-writer
    version: ">=2.0.0"
    optional: false
framework_version: ">=1.0.0"
assigned_agents:
  - orchestrator
  - meta_factory
  - backend_specialist
  - frontend_worker
  - qa_auditor
last_used: 2026-06-05
scope: restricted
---

# Institutional Memory — AIRON‑Cast

This skill provides access to AIRON‑Cast's long‑term institutional memory:
architectural decisions, proven solutions to non‑trivial problems, and
reusable patterns. It uses the ecosystem's own SQLite + FTS5 memory.

---

## 0. Core Principle

**Not a daily log.** This knowledge base stores only definitive solutions to
significant technical challenges — not routine task completions. The
`journal-writer` handles operational journaling; this skill focuses on
reusable, high‑value knowledge.

---

## 1. Querying the Knowledge Base

Before designing a new solution, check if a similar problem has already been
solved. Use the internal search tools:

### 1.1 ADR Search (Architectural Decisions)

ADRs are stored in the `adrs` table with full‑text search via FTS5.

```bash
# Via memory_manager (Python)
memory_manager.search_adrs("embedding model selection")
```

### 1.2 Journal Search (Patterns and Field Knowledge)

Reusable patterns and field feedback are stored in the journal.

```bash
# Via journal_query.py
python .agents/skills/journal-writer/scripts/journal_query.py \
  --term "payment gateway timeout" \
  --type adr
```

### 1.3 Combined Search

When unsure where a solution might be, search both sources. The agent should
summarize findings and present them to the operator before forging new
components.

---

## 2. Adding Knowledge

Only record a knowledge entry when:

- A non‑trivial architectural decision was made (→ ADR).
- A reusable solution pattern was discovered (→ Pattern).
- A significant integration bottleneck was resolved with a clear,
  reproducible solution (→ ADR or Pattern).

**Do NOT record:** routine bug fixes, daily task completions, or operational
checklists.

### 2.1 Recording a Decision (ADR)

Use `journal-writer` with type `adr`. Required fields:
- `title`: clear, searchable description of the decision.
- `context`: the situation that forced the decision.
- `decision`: what was chosen.
- `alternatives_considered`: list of options evaluated.
- `reasoning`: why this option was selected.
- `consequences`: known trade‑offs.
- `status`: `accepted` (or `superseded` if replacing a previous ADR).

### 2.2 Recording a Pattern

Use `journal-writer` with type `pattern`. Required fields:
- `title`: concise pattern name.
- `description`: what the pattern is and when it applies.
- `evidence`: references to journal entries or ADRs that exhibit this pattern.
- `recommendation`: concrete action to apply (or avoid) the pattern.

---

## 3. Anti‑Patterns

- ❌ **"We'll remember this later."** — Without a written ADR, the decision
  evaporates. Always record immediately after validation.
- ❌ **Recording trivialities.** — If it didn't require at least 30 minutes of
  analysis to solve, it probably doesn't belong here.
- ❌ **Duplicating without search.** — Always query first to avoid redundant
  or conflicting knowledge.

---

## 4. Integration with the Ecosystem

- **`memory_manager`** provides FTS5 search over ADRs.
- **`journal-writer`** provides the write interface for ADRs and patterns.
- **`meta_factory`** uses this skill to detect error patterns and propose
  ecosystem improvements.
- **`orchestrator`** may consult it before assigning complex tasks to avoid
  reinventing solutions.