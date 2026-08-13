---
name: architecture-refactoring
description: "Patrones de Refactorización Atómica (Astro/TS/Python). Establece las reglas para aplicar Early Returns, tipado estricto, eliminación de código muerto y DRY sin romper la capa de negocio."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Universal Refactoring Patterns (A2LT Standard)

This skill dictates how to untangle "Spaghetti Code" across all supported languages (TypeScript, Python, Bash) without introducing functional regressions.

---

## 1. The Early Return (Bouncer Pattern)

Deeply nested `if/else` statements are cognitive poison. Focus on returning early.

- ❌ **Wrong:**
  ```python
  if user:
      if user.is_active:
          return run_process()
  ```
- ✅ **Right:**
  ```python
  if not user or not user.is_active:
      return False
  return run_process()
  ```

## 2. Magic Strings to Constants

If a literal string like `"COMPLETED"` or `"admin"` is used more than once, extract it immediately to an Enum or a global constant. Refuse to refactor without applying this mapping.

## 3. Strict Typing Constraints

When refactoring JavaScript to TypeScript, or raw Python to Typed Python:

- **No `any` Types:** Implicit or explicit `any` types are strictly forbidden. If the data structure is unknown, use `unknown` and cast/validate it properly.
- **Destructuring:** In TS/React/Astro, always destructure props `const { title } = Astro.props;` rather than passing the massive `props` object around.

## 4. The Boy Scout Rule

When modifying a file to fix a bug, the agent MUST scan the immediate surroundings for orphaned variable declarations, unused imports, or duplicate logic blocks, and clean them in the same commit.
