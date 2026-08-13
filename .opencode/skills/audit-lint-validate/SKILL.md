---
name: audit-lint-validate
description: "Mecanismo A2LT para garantizar la correcta ejecución de Linters y validadores (Ruff, ESLint, Prettier, TypeScript). Bloquea la inyección de código con 'code smells' o variables huérfanas."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Pre-Flight Lint & Validate (A2LT Standard)

This skill is the enforcer for code hygiene before it runs. If a project has linters configured, the agent MUST run them and respect their output immediately.

---

## 1. Python (Ruff over Flake8)

- Always prioritize `Ruff` for linting and formatting in Python. It executes in milliseconds.
- Warning: Ignoring a linter rule with `# noqa` requires an explicitly documented reason. Blanket disables (`# noqa`) without rules are forbidden.

## 2. Frontend Ecosystem (Astro / TS / Tailwind)

- **TypeScript `any` rule:** If compiling fails due to implicit `any`, the agent MUST infer the proper Type or Interface. Adding `// @ts-ignore` to silence the compiler is strictly considered a failure of the agent task.
- **Tailwind Ordering:** Use `prettier-plugin-tailwindcss` to enforce deterministic class sorting. AI-generated generic raw CSS must be translated to Tailwind utility classes.

## 3. The Auto-Fix Mandate

Before reporting massive syntax issues to the user, run the auto-fix commands if they exist (`npm run lint:fix` or `ruff check --fix`). Only escalate architectural errors that Linters cannot auto-resolve.

## 4. Astro-Specific Rules

> These rules exist because Astro's compilation model differs from plain TypeScript files.

- **NO JSDoc for typing in `.astro` files:** Astro compiles `<script>` blocks as pure TypeScript modules. JSDoc comments (`/** @type {string} */`) are NOT processed as type directives in this context. They are silently ignored. ALWAYS use inline TypeScript annotations:
  - ✅ `let count: number = 0`
  - ✅ `const handler = (e: MouseEvent): void => {}`
  - ❌ `/** @type {number} */ let count = 0`

## 5. Conditional Rendering Audit Rule

- After writing any component that uses a ternary (`? :`) for conditional rendering, ask: **_"Does a use case exist where the user would want BOTH branches rendered simultaneously?"_**
  - If YES → refactor to two independent `&&` expressions.
  - If NO → the ternary is valid.
- This rule exists because `logo ? <Image> : <h3>title</h3>` was silently broken in production — the user could not display both logo AND title at the same time.

## 6. CMS-Zod Syncing Protocol (Astro + Decap CMS)

> **POST-MORTEM ORIGIN:** This section exists because a silent Decap CMS "Publish" button freeze and a fatal `TypeError: e.get is not a function` crash were caused by schema mismatches between `config.yml` and `content.config.ts`.

### Mandatory Rules

1. **Read Before Write:** BEFORE modifying any file in `src/content/`, you MUST read `content.config.ts` to understand the current Zod schema. NEVER create or overwrite a JSON/MD content file without validating its structure against the schema first.

2. **Optional Field Mirroring:** Every field marked `required: false` in Decap CMS `config.yml` MUST have its corresponding Zod schema field marked with `.optional()`. Failing to mirror this causes the CMS "Publish" button to silently freeze when the user clears an optional field.

   ```yaml
   # config.yml
   - {
       label: "Logo Image",
       name: "logo_image",
       widget: "image",
       required: false,
     }
   ```

   ```typescript
   // content.config.ts
   logo_image: z.string().optional(),
   ```

3. **List Widget Singular vs Plural (CRITICAL):** When creating a list of simple strings in Decap CMS, use `field:` (SINGULAR) to produce a flat array. Using `fields:` (PLURAL) forces Decap to serialize as map/dictionary objects, causing a fatal `TypeError` in the ListControl serializer.

   ```yaml
   # ✅ CORRECT — produces ["Item 1", "Item 2"]
   - {
       label: "Trust Indicators",
       name: "trust_indicators",
       widget: "list",
       field: { label: "Indicator", name: "indicator", widget: "string" },
     }

   # ❌ FATAL — produces [{indicator: "Item 1"}] and crashes the serializer
   - {
       label: "Trust Indicators",
       name: "trust_indicators",
       widget: "list",
       fields: [{ label: "Indicator", name: "indicator", widget: "string" }],
     }
   ```

4. **Select Widget Default Trap:** A `select` widget with a `default` value in Decap CMS will NOT mark the document as "dirty" if the user's selection matches the default. This prevents the "Publish" button from activating. **Omit `default` from select widgets** that control themes, layouts, or carousel types.

5. **Enum Hardening:** If a field accepts a finite set of values (e.g., theme: light/dark, layout: box/full-bg), define it as `z.enum([...])` in Zod, not `z.string()`. This catches typos at build time instead of producing silent runtime mismatches.
