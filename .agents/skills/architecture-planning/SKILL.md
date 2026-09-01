---
name: architecture-planning
description: "Metodología de Desglose de Tareas A2LT. Impone la creación de planes atómicos (< 10 pasos), verificabilidad inmediata, y prevé el bloqueo de 'falsos positivos' mediante criterios de completitud duros."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Architecture Planning & Task Breakdown (A2LT Standard)

This core capability dictates how multi-step features must be decomposed prior to execution. Random, monolithic coding attempts fail in complex environments.

---

## 1. The 10-Step Limit

- A plan must never exceed 10 distinct tracking steps.
- If a feature requires 50 steps, construct **Sub-Phases** or independent architectural plans. Massive checklists induce hallucination and context loss.

## 2. Immediate Verifiability

Every single step must possess a rigid verification mechanism.

- ❌ **Wrong:** "Set up authentication."
- ✅ **Right:** "Configure NextAuth -> Verify: Visiting `/api/auth/session` returns 200 JSON object."
- A task is not complete simply because the code was generated. It is complete when the verification command/test succeeds.

## 3. Sequential Dependencies

Determine the Critical Path before writing code.

- Dependencies (Environment, Database Schemas) MUST run first.
- UI components and Client layers run second.
- End-to-End verification runs last.

## 4. Contextual Scope

Do not inject generic checklist items.

- If adding a frontend button, do not add "Run Security Scan" to the plan unless the button calls a financial endpoint. Keep the execution cycle hyper-focused.

---

**The Goal of Planning:**
A plan exists solely so that any other agent, or the human operator, can read it and instantly understand _Exactly What is Happening_ and _How to Prove it Works_.
