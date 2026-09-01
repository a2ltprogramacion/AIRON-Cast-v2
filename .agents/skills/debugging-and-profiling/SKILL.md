---
name: debugging-and-profiling
description: "Macro-Skill de Diagnóstico Nivel 5. Impone la Ley de Hierro: Cero Parches sin Análisis de Causa Raíz. Combina rastreo sistemático con Profiling de Vitals, análisis de dependencias (Bundle) y límites arquitectónicos."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Systematic Debugging & Performance Profiling (A2LT Standard)

Random fixes waste time, create new bugs, and generate tech debt. Quick patches mask underlying architectural rot.
This macro-skill is activated instantly whenever analyzing a bug, a performance drop, or a broken workflow.

---

## 1. THE IRON LAW OF DEBUGGING

**NO FIXES WITHOUT ROOT CAUSE INVESTIGATION FIRST.**
Do not propose "just a quick fix" or "try this parameter." You must guarantee you understand the failure mechanism before writing one line of code.

### The 4-Phase System

1. **Root Cause Check:** Did you explicitly read the full error stack trace (including the component boundaries)?
2. **Find the Pattern:** What works that is structurally similar? What dependencies are loaded?
3. **Hypothesis Formation:** Document: _"I think X is the root cause because Y."_
4. **Implement Singly:** Make the smallest change testing exactly that variable. DO NOT bundle fixes.

### The "Question Architecture" Threshold

If **3+ fixes fail** to resolve the issue, or if fixing symptom A breaks component B:
**STOP.** You are no longer fixing a bug; you have discovered a fundamentally flawed architecture. Escalate to the human partner immediately rather than proposing a 4th fix.

---

## 2. Multi-Component Tracing

In a Full-Stack Astro/Django environment, an error could live in the UI, the JSON payload, the Django Service layer, or the Database.

- Never guess the layer.
- **Trace Backwards:** Start at the exact symptom and walk the data pipeline backward.
- _Example:_ If the UI button fails -> Check Chrome Network Tab -> Check Next.js/Astro Endpoint -> Check Django ViewSet JSend Payload -> Check Django Service Layer exception.

---

## 3. Performance Profiling Execution

Do not guess performance bottlenecks. Adopt the **4-Step Profiling Process:**
`BASELINE -> IDENTIFY -> FIX -> VALIDATE`.

### Core Web Vitals Baselines

Before proposing an optimization, compare current metrics against these rigid boundaries:

- **LCP (Largest Contentful Paint):** `< 2.5s` (Optimized via Edge Caching / CDN).
- **INP (Interaction to Next Paint):** `< 200ms` (Optimized via chunking main-thread JS).
- **CLS (Cumulative Layout Shift):** `< 0.1` (Optimized via explicit image/iframe dimensions).

---

## 4. Frontend Bundle Analysis (Astro/React)

If performance is suffering due to heavy payloads:

- **Root Cause:** Look for un-chunked massive libraries (e.g., loading all of Lodash instead of subset imports).
- **Resolution:** Force code-splitting, enforce tree-shaking, and lazy-load third-party components (e.g., Astro `client:visible` or `client:idle`).

---

## 5. Anti-Patterns (Immediate Rejection)

- **"I'll just add a `try/except pass`"**: Masking the error destroys traceability.
- **"Let's increase the Timeout"**: A timeout is a symptom of a lock or a query issue, not the root cause.
- **"I see the problem, let me fix it based on the symptom"**: Seeing a symptom does not equal understanding the root cause propagation.
