---
name: architecture-documentation
description: "Estándares A2LT para plantillas de documentación. Reglas estrictas sobre la creación de READMEs, Changelogs, e In-Code Docs para explicar 'Por Qué' existe un bloque en lugar del 'Qué'."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Architecture: Enterprise Documentation (A2LT Standard)

This skill activates when generating `README.md`, writing `CHANGELOG.md`, or documenting complex modules. Good documentation accelerates agent onboarding and prevents knowledge loss.

---

## 1. The Repository Root Documentation

Every project MUST have a `README.md` containing:

- **Purpose Statement:** What does it do?
- **A2LT Constraints Stack:** (e.g., Python 3.12, Astro 4, Tailwind v4).
- **Environment Setup:** Copy-paste ready commands (e.g., `python -m venv .venv && source .venv/bin/activate`). Do not assume implicit knowledge.

## 2. In-Code Documentation (Docstrings)

- Do not state the obvious.
  - ❌ `def get_user(id): # Gets a user by ID`
  - ✅ `def get_user(id): # Returns the active user model. Bypasses the cache due to critical financial sync.`
- **Types > Docs:** A Python function defined as `def get_user(id: int) -> User:` is superior to a four-line text comment explaining the parameter types.

## 3. The Changelog Protocol

- Format MUST adhere strictly to "Keep a Changelog".
- Types: `[Added]`, `[Changed]`, `[Deprecated]`, `[Removed]`, `[Fixed]`, `[Security]`.
- Vague commit-style dumps like `[Fixed] Minor bug` are rejected. Require: `[Fixed] Payment gateway timeout on edge networks during Stripe webhook reception.`
