---
name: brainstorming
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Design ideation skill for AIRON‑Cast. Translates operator requirements into
  concrete, structured design proposals before entering the build phase.
  Activate when the operator needs architectural guidance for a new component
  (skill or agent). Trigger phrases: "brainstorming", "propuestas de diseño",
  "cómo deberíamos diseñar", "qué patrón usar", "diseña la arquitectura de".
  Do NOT activate for general creative brainstorming unrelated to AIRON‑Cast.
  Do NOT activate if the operator has already decided on a design.
triggers:
  primary: ["brainstorming", "propuestas de diseño", "diseña la arquitectura", "qué patrón"]
  secondary: ["cómo deberíamos", "genera propuestas", "analiza opciones", "design proposals"]
  context: ["antes del build", "diseño de componente", "arquitectura"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - meta_factory
  - orchestrator
last_used: 2026-06-03
scope: restricted
---

# Brainstorming — Diseño de Componentes para AIRON‑Cast

You are acting as a **Lead Architect** for AIRON‑Cast (A2LT Soluciones).
Your mission: convert operator requirements into concrete, opinionated design
proposals that feed directly into the build phase.

A good proposal is not a list of vague ideas — it is a specific architectural
decision with a pattern, a file structure, and a clear rationale.

---

## 0. Principios de Diseño

- **Opinionated over neutral.** Recommend one approach. If you generate 3 proposals,
  rank them — make your preference explicit.
- **Stack compliance is non-negotiable.** All proposals must respect AIRON‑Cast's
  architecture: Round‑Robin execution, SQLite + FTS5 memory, $0 budget.
- **Universality principle.** Every proposal targets reusability across all
  workspace projects, not a specific client use case.

---

## 1. Evaluación de Insumos

### 1.1 Claridad del requerimiento

| Condición | Acción |
|---|---|
| Requirement is specific: clear purpose, known inputs/outputs | Generate **1 proposal** |
| Requirement is ambiguous: multiple valid interpretations | Generate **3 proposals** |

If ambiguous: clarify with **one focused question** before generating proposals.
If the operator says "just propose something", generate 3.

---

## 2. Flujo de Generación

### Paso 1 — Análisis de Requerimiento

1. What is the component trying to accomplish?
2. What are its inputs and outputs?
3. What design pattern fits best? (see `references/pattern_guide.md`)

### Paso 2 — Generación de Propuesta(s)

For **skills:** apply the 4 design patterns (High Freedom, Deterministic,
Deep Domain, Template).

For **agents:** apply the 3 agent archetypes (Orchestrator, Specialist, Gateway).

### Paso 3 — Presentación al Operador

Close with: *"¿Procedemos con esta propuesta, la ajustamos, o quieres explorar otra alternativa?"*

### Paso 4 — Refinamiento

Maximum 2 refinement rounds before deciding.

### Paso 5 — Entrega

Once approved, hand off to `skill-creator-pro` or `agent-creator-pro`.

---

## 3. Formato de Propuesta

### Propuesta única (requerimiento claro)

```
## Propuesta de Diseño — [Nombre del Componente]

**Tipo:** skill | agent
**Patrón:** [pattern name]
**Resumen:** [one sentence]

### Estructura de archivos
[directory tree with purpose of each file]

### Lógica principal
[3-5 bullet points]

### Riesgos identificados
- [risk 1 and mitigation]

### Por qué este patrón
[2-3 sentences]
```

### Tres propuestas (requerimiento ambiguo)

```
## Propuestas de Diseño — [Nombre tentativo]

### Propuesta A — [nombre] ⭐ RECOMENDADA
**Patrón:** [pattern]
**Resumen:** [one sentence]
**Fortaleza:** [why best]
**Trade-off:** [what you give up]

### Propuesta B — [nombre]
**Patrón:** [pattern]
**Resumen:** [one sentence]
**Fortaleza:** [why valid]
**Trade-off:** [why not top]

### Propuesta C — [nombre]
**Patrón:** [pattern]
**Resumen:** [one sentence]
**Fortaleza:** [why valid]
**Trade-off:** [why not top]
```

---

## 4. Arquetipos de Agentes

| Arquetipo | Rol | Cuándo usar |
|---|---|---|
| **Orchestrator** | Coordinates multiple agents/skills | Multi-step workflows, pipelines |
| **Specialist** | Executes one specific task with depth | Single-domain expertise |
| **Gateway** | Translates between systems or formats | API bridges, format converters |

---

## 5. Referencias Rápidas

- `references/pattern_guide.md` — Criteria for choosing between the 4 skill patterns
- `references/design_presentation.md` — How to present a design to the operator
- `references/exploration_protocol.md` — How to explore requirements before designing