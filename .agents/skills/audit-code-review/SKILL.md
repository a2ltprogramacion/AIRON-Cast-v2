---
name: audit-code-review
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Auditor estricto de código para AIRON‑Cast. Evalúa funcionalidad, seguridad,
  linting, clean code y cobertura de tests antes de cualquier merge o despliegue.
  Activar cuando un agente entrega código para revisión final.
  Trigger phrases: "audita este código", "revisa el PR", "code review",
  "valida el componente antes de deploy".
  No activar para revisiones informales o código no finalizado.
triggers:
  primary: ["audita este código", "revisa el PR", "code review"]
  secondary: ["valida antes de deploy", "pre-merge check"]
  context: ["gate final", "qa", "despliegue"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - qa_auditor
last_used: 2026-06-05
scope: restricted
---

# Code Review & QA Audit — AIRON‑Cast

This skill is the final gatekeeper before code is merged or deployed.
It mandates a rigorous inspection across five dimensions:
functionality, security, linting, clean code, and test coverage.

---

## 1. Verificación Funcional

- Does the code resolve the precise objective without introducing
  out-of-scope logic?
- Are edge cases handled? (empty states, zero values, null, massive payloads)
- If conditional rendering is used (ternary `? :`), verify that there is no
  use case where both branches should render simultaneously. If yes, refactor
  to two independent `&&` expressions.

---

## 2. Seguridad y Protección de Datos

### 2.1 Inyección
- SQL queries MUST be parameterized (ORM native methods, never string
  interpolation).
- XSS: sanitize user input in the frontend.

### 2.2 Autenticación y Autorización
- Does the endpoint validate session/JWT tokens?
- Does it verify the user owns the resource they are trying to modify?

### 2.3 Secretos Hardcodeados
- Scan the payload for leaked API keys, `.env` fallbacks, or raw database
  credentials. **Halt immediately if found.**

---

## 3. Linting y Formato

### 3.1 Python
- Prioritize `Ruff` for linting and formatting.
- `# noqa` requires an explicit documented reason. Blanket disables are
  forbidden.
- Before reporting syntax issues, run auto-fix: `ruff check --fix`.

### 3.2 Frontend (Astro / TypeScript / Tailwind)
- TypeScript `any`: if compilation fails due to implicit `any`, infer the
  proper type. `// @ts-ignore` is considered a task failure.
- Tailwind: use `prettier-plugin-tailwindcss` for deterministic class
  ordering. AI-generated raw CSS must be translated to Tailwind utilities.
- Before reporting issues, run: `npm run lint:fix`.

### 3.3 Reglas Específicas de Astro
- **NO JSDoc for typing in `.astro` files:** Astro compiles `<script>` blocks
  as pure TypeScript modules. JSDoc comments are NOT processed as type
  directives. Always use inline TypeScript annotations.
  - ✅ `let count: number = 0`
  - ❌ `/** @type {number} */ let count = 0`

### 3.4 Protocolo de Sincronización CMS-Zod (Decap CMS + Astro)

> This section exists because schema mismatches between `config.yml` and
> `content.config.ts` cause silent CMS freezes and fatal TypeErrors.

1. **Read Before Write:** Before modifying any file in `src/content/`, read
   `content.config.ts` to understand the current Zod schema. Never create or
   overwrite a content file without validating against the schema first.

2. **Optional Field Mirroring:** Every field marked `required: false` in
   Decap CMS `config.yml` MUST have its Zod field marked `.optional()`.

3. **List Widget singular vs plural:** Use `field:` (singular) for simple
   string lists to produce a flat array. `fields:` (plural) forces map
   objects and causes a fatal `TypeError`.
   - ✅ `field: { label: "Item", name: "item", widget: "string" }`
   - ❌ `fields: [...]`

4. **Select Widget Default Trap:** A `select` widget with a `default` value
   will NOT mark the document as dirty if the selection matches the default,
   blocking the "Publish" button. **Omit `default` from select widgets.**

5. **Enum Hardening:** Finite-value fields (theme, layout) must use
   `z.enum([...])` in Zod, not `z.string()`.

---

## 4. Clean Code Checklist

Verify the following before approving:

- [ ] Functions and components are under 30 lines.
- [ ] Each function/component does exactly one thing.
- [ ] Variable, function, and prop names are intention-revealing.
- [ ] No comments explain what the code does (only why, if unusual).
- [ ] Semantic HTML tags used (`<article>`, `<section>`, `<nav>`) instead of
      `<div>` soup.
- [ ] No deep chaining: `a.get_b().get_c().do_something()`.
- [ ] Exceptions used instead of returning error codes (`-1`, `null`).
- [ ] No `None`/`null` passed as arguments without explicit handling.
- [ ] Variables declared as close to their usage as possible.

---

## 5. Cobertura de Tests (Regla del 80%)

- All new business logic MUST have a unit or integration test.
- If a PR fixes a bug perfectly but includes zero tests to prevent future
  regressions, the PR is **Rejected**.

---

## 6. Formato de Feedback

Output feedback linearly with one of these tags:

| Tag | Meaning |
|-----|---------|
| `[CRITICAL]` | Security vulnerability, crash risk, or hardcoded secret. Must be fixed before merge. |
| `[ARCH]` | Structural or clean code violation. Should be fixed; requires justification to ignore. |
| `[LINT]` | Linting or formatting issue. Run auto-fix first, then report remaining. |
| `[TESTS]` | Missing test coverage for new logic. |
| `[CMS-ZOD]` | Schema mismatch between Decap CMS config and Zod. |