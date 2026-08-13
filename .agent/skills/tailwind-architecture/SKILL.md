---
name: tailwind-architecture
description: "Ingeniería de Tailwind CSS v4. Uso del patrón CSS-First (`@theme`), variables nativas, Container Queries (`@container`) y layouts asimétricos para desarrollo UI sin dependencias de JS."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Tailwind CSS v4 Architecture (A2LT Standard)

This discrete skill dictates how Tailwind CSS must be utilized in modern Astro/React applications, explicitly focusing on the **Tailwind v4 Oxide Engine** methodologies.

---

## 1. The CSS-First Mentality

`tailwind.config.js` is deprecated in spirit. Configuration belongs in the main CSS file using the `@theme` directive.

- **Tokens:** Define all tokens as CSS Variables (`--color-primary`, `--spacing-md`).
- **OKLCH Usage:** Use `oklch()` color spaces for primary themes due to its perceptual uniformity.

## 2. Responsive Design vs Container Queries

Instead of strictly relying on viewport breakpoints (`md:`, `lg:`), isolate components using native **Container Queries**.

- **Context-Independent Components:** Wrap the parent card heavily in `@container`. Let internal elements flow via `@sm:`, `@md:` logic. This allows a widget to be perfectly responsive whether it's placed in a sidebar or a main row.

## 3. Dark Mode

- Utilize strict class-based toggling (`dark:bg-zinc-900`, `dark:text-white`) or system-preference media queries depending on the business requirements.
- **Borders:** In dark mode, borders should be incredibly subtle (`dark:border-zinc-800`).

## 4. Anti-Patterns

- **`@apply` Directive:** Heavily discouraged. If you find yourself writing `@apply` for 5+ classes, extract them into a physical React/Astro component instead of polluting the CSS.
- **Arbitrary Values:** `text-[13px]` is forbidden if a design token scale exists. Stick to the generated type scale (`text-xs`, `text-sm`).

## 5. PROHIBITIONS (Absolute Rules — No Exceptions)

> These rules are the direct result of post-mortem failures from real projects.

- **NO arbitrary color hex values in HTML:** `bg-[#ff3b30]` is PROHIBITED if the project has a `@theme` block defined in `global.css`. Every brand color MUST be a named CSS variable (`--color-brand-red`) exposed as a Tailwind token.
- **Activation Protocol:** Before writing a single Tailwind class on a component, READ `src/styles/global.css`. Find all `@theme` tokens. Use ONLY those tokens. If no tokens exist yet, STOP and create them first.
- **NO `classList.add('hidden')` on animated elements:** The `hidden` utility can lose specificity battles against animated classes in Tailwind v4's CSS pipeline. Use `element.style.display = 'none'` directly from JavaScript instead.

## 6. Tailwind v4 Gotchas

- **Specificity conflict with `hidden` + animations:** When an element has an active CSS animation (e.g. `animate-pulse`) and an inline display class (`inline-block`), adding `hidden` via `classList` may fail to hide the element because the animation class wins the specificity battle. Solution: always use `element.style.display` for JS-driven show/hide of animated elements.
- **`@theme` replaces `tailwind.config.js`:** All design tokens (colors, spacing, fonts) belong in the CSS file under `@theme {}`, not in a JS config file. The JS config is only for plugin registration.

## 7. The Two-Level Variable Rule (`@theme` vs `@layer base`)

> **POST-MORTEM ORIGIN:** This section exists because multiple components in the A2LT VCard template used phantom Tailwind classes (`bg-bg-elevated`, `bg-border-subtle`) that silently generated NO CSS output, causing invisible backgrounds and pagination dots.

There is a **critical distinction** in Tailwind v4 between where you define a CSS variable:

| Definition Location                        | Generates Utility Class?                   | How to Use                                           |
| ------------------------------------------ | ------------------------------------------ | ---------------------------------------------------- |
| `@theme { --color-X: yyy }`                | ✅ YES — `bg-X`, `text-X`, `border-X` work | Use Tailwind classes normally                        |
| `@layer base { :root { --color-X: yyy } }` | ❌ NO — Any `bg-X` class is a phantom      | MUST use `style="background-color: var(--color-X);"` |

### Operational Rules

1. **Before using any `bg-*`, `text-*`, or `border-*` class** that references a custom variable, verify the variable is defined inside `@theme {}`. If it lives in `@layer base`, you MUST use inline `style="property: var(--color-name);"` instead.
2. **Phantom Class Detection:** If a visual element (dot, card, overlay) appears to have no background color despite having a Tailwind class, the FIRST diagnostic step is to check where the referenced variable is defined.
3. **The A2LT Convention for Theming Surfaces:** For critical surfaces that toggle Light/Dark (section backgrounds, modal panels, card overlays), use explicit CSS variable injection:
   ```html
   <section style="background-color: var(--color-bg-surface);">
     <div style="background-color: var(--color-bg-elevated);"></div>
   </section>
   ```
   This is MORE reliable than Tailwind classes when the token lives in `@layer base`.

### Specificity Overrides for Themed Components

When a base CSS color and a Tailwind utility need to coexist on the same element (e.g., pagination dots with a default color and an active brand color):

```css
/* Compound selector = higher specificity than a single Tailwind class */
button.dot-class {
  background-color: var(--color-border-subtle); /* Base state */
}
button.dot-class.bg-brand-teal {
  background-color: var(--color-brand-teal); /* Active state wins */
}
```

### The `<dialog>` Top Layer Inheritance

The native `<dialog>` element creates a browser "top layer". Despite this, CSS custom properties defined on `:root` ARE inherited into the top layer. **NEVER hardcode HEX colors in modals.** Always use `var(--color-bg-surface)`, `var(--color-text-main)`, etc. The common error is assuming variables don't inherit and preemptively hardcoding `#0f172a` for dark backgrounds.
