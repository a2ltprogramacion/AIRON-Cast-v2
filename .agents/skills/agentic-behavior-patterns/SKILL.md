---
name: agentic-behavior-patterns
description: "Metamodelo A2LT para el Orquestador y Agentes Paralelos. Impone la forma de razonar (Brainstorming estructurado vs Agentes en paralelo con responsabilidades divisorias)."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Agentic Behavior Patterns (A2LT Standard)

This skill outlines how the Orquestador and specialized sub-agents must interact, divide tasks, and coordinate brainstorming to solve complex architectural challenges.

---

## 1. Orquestador / Sub-Agent Delegation

- **Asymmetrical Isolation:** Sub-agents must be spun up with highly scoped instructions (`"Agent Alpha: Resolve the database deadlock. Return just the SQL index."`). Do not ask a sub-agent to "Build a web app".
- **Context Preservation:** Before invoking a sub-agent, prepare an atomic summary of the error or goal so the sub-agent doesn't waste tokens reading 100 previous logs.

## 2. Structured Brainstorming

When an agent is asked to ideate or solve a vague objective:

- **Divergent Phase (Quantity):** List 3 to 4 diametrically opposed architectural approaches (e.g., "Full SSR", "Static Generation", "Client-Side Fetching").
- **Constraint Filtering:** Immediately cross-reference those 4 ideas against the user's hard constraints (e.g., "Must be fast on slow networks"). Eliminate the bad ideas explicitly explaining _why_ they fail.
- **Convergent Phase:** Propose **One Final A2LT Solution**. State it confidently. Do not give the user 4 options and ask them to choose if you know one is vastly superior.

## 3. Multi-Agent Deadlock Prevention

If two proposed solutions conflict, fall back to the "Iron Triangle": Performance, Maintainability, Time. Always optimize for Maintainability and Performance over speeding up the code delivery.
