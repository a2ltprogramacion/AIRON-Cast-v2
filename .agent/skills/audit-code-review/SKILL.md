---
name: audit-code-review
description: "Auditor Estricto de Pull Requests y Modificaciones. Evalúa el código bajo las dimensiones de Funcionalidad, Calidad, Seguridad (Inyecciones/Secretos), y Cobertura de Pruebas (TDD)."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Code Review & QA Audit (A2LT Standard)

This skill activates as the final gatekeeper before code is merged or considered "complete". It mandates a rigorous inspection across multiple architectural layers.

---

## 1. Functional Verification

- Does the code resolve the precise objective without introducing out-of-scope logic?
- Are edge cases (empty states, zero values, massive payloads) handled gracefully?

## 2. Security & Data Protection Check

- **Injection:** Are SQL queries parameterized? (e.g., using ORM native methods and NEVER string interpolation). Are XSS strings sanitized in the frontend?
- **Authentication/Authorization:** Is the endpoint actively validating session/JWT tokens? Does it verify the user owns the resource they are trying to modify?
- **Hardcoded Secrets:** Scrape the payload for leaked API keys, `.env` fallbacks, or raw database credentials. Halt immediately if found.

## 3. Performance & Structural Integrity

- **N+1 Queries:** Does a loop execute a database hit per iteration? (Mandate `select_related`/`JOIN`).
- **DRY / Modularity:** Have duplicate blocks of logic been hoisted into a shared utility or base class?

## 4. Test Coverage Validation (The 80% Rule)

- All new business logic MUST be accompanied by a Unit/Integration test.
- If the PR fixes a bug perfectly but includes zero tests to prevent future regressions, the PR is **Rejected**.

---

**Actionable Feedback Mode:**
When utilizing this skill, output feedback linearly:

- `[CRITICAL]` For security / crash risks.
- `[ARCH]` For structural improvements (Clean Code violations).
- `[TESTS]` For missing coverage.
