---
name: tailwind-architecture
version: 1.0.0
type: frontend
subtype: skill
tier: all
description: |
  Tailwind CSS v4 architecture for AIRON‑Cast. CSS-First methodology
  with @theme directives, Container Queries, strict design token
  enforcement, and post-mortem rules from real production failures.
  Trigger phrases: "configurar Tailwind", "tema Tailwind", "design tokens",
  "Container Queries", "arquitectura CSS", "Tailwind v4".
  Do NOT activate for general CSS questions unrelated to Tailwind v4.
triggers:
  primary: ["configurar Tailwind", "tema Tailwind", "arquitectura CSS"]
  secondary: ["design tokens", "Container Queries", "Tailwind v4"]
  context: ["Astro styling", "frontend design system"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - ux-ui_specialist
  - frontend_worker
last_used: 2026-06-05
scope: restricted
---

# Tailwind CSS v4 Architecture (AIRON‑Cast Standard)

This skill dictates how Tailwind CSS must be utilized in Astro projects,
explicitly targeting the **Tailwind v4 Oxide Engine** methodologies.

---

## 1. The CSS-First Mentality

`tailwind.config.js` is deprecated in spirit. Configuration belongs in the
main CSS file using the `@theme` directive.

- **Tokens:** Define all tokens as CSS Variables (`--color-primary`, `--spacing-md`).
- **OKLCH Usage:** Use `oklch()` color spaces for primary themes due to its perceptual uniformity.

---

## 2. The Two-Level Variable Rule (`@theme` vs `@layer base`)

> **POST-MORTEM ORIGIN:** Multiple components in the A2LT VCard template used
> phantom Tailwind classes (`bg-bg-elevated`, `bg-border-subtle`) that silently
> generated NO CSS output, causing invisible backgrounds and pagination dots.

There is a **critical distinction** in Tailwind v4 between where you define
a CSS variable:

| Definition Location | Generates Utility Class? | How to Use |
|---------------------|--------------------------|------------|
| `@theme { --color-X: yyy }` | ✅ YES — `bg-X`, `text-X`, `border-X` work | Use Tailwind classes normally |
| `@layer base { :root { --color-X: yyy } }` | ❌ NO — Any `bg-X` class is a phantom | MUST use `style="background-color: var(--color-X);"` |

### Operational Rules

1. **Before using any `bg-*`, `text-*`, or `border-*` class** that references
   a custom variable, verify the variable is defined inside `@theme {}`. If it
   lives in `@layer base`, you MUST use inline `style="property: var(--color-name);"` instead.
2. **Phantom Class Detection:** If a visual element (dot, card, overlay) appears
   to have no background color despite having a Tailwind class, the FIRST diagnostic
   step is to check where the referenced variable is defined.
3. **The AIRON‑Cast Convention for Theming Surfaces:** For critical surfaces that
   toggle Light/Dark (section backgrounds, modal panels, card overlays), use
   explicit CSS variable injection:
   ```html
   <section style="background-color: var(--color-bg-surface);">
     <div style="background-color: var(--color-bg-elevated);"></div>
   </section>
   ```
   This is MORE reliable than Tailwind classes when the token lives in `@layer base`.

---

## 3. Design Tokens Integration

This skill expects design tokens from `ux-ui_specialist` stored in
`workspace/<slug>/src/styles/design-tokens.json`. The tokens are injected
via `global.css` using `@theme`:

```css
@theme {
  --color-primary-50: #eff6ff;
  --color-primary-500: #3b82f6;
  --color-primary-700: #1d4ed8;
  --color-bg-surface: #ffffff;
  --color-bg-alt: #f8fafc;
  --color-bg-elevated: #ffffff;
  --color-text-main: #0f172a;
  --color-text-muted: #475569;
  --color-border: #e2e8f0;
  --color-border-subtle: #f1f5f9;
  --font-heading: 'Inter', sans-serif;
  --font-body: 'Inter', sans-serif;
}
```

Dark mode tokens go in `@layer base`:

```css
@layer base {
  .dark {
    --color-bg-surface: #0f172a;
    --color-bg-alt: #1e293b;
    --color-bg-elevated: #1e293b;
    --color-text-main: #f1f5f9;
    --color-text-muted: #94a3b8;
    --color-border: #334155;
    --color-border-subtle: #1e293b;
  }
}
```

---

## 4. Responsive Design vs Container Queries

Instead of strictly relying on viewport breakpoints (`md:`, `lg:`), isolate
components using native **Container Queries**.

| Breakpoint | Width | Target Device |
|------------|-------|---------------|
| `sm` | 640px | Large phones |
| `md` | 768px | Tablets |
| `lg` | 1024px | Small laptops |
| `xl` | 1280px | Desktops |
| `2xl` | 1536px | Large screens |

- **Context-Independent Components:** Wrap the parent card in `@container`.
  Let internal elements flow via `@sm:`, `@md:` logic.
- **Mobile-First:** All styles start at 375px base. Scale up, never down.

---

## 5. Dark Mode

- Use strict class-based toggling (`dark:bg-zinc-900`, `dark:text-white`).
- **Borders:** In dark mode, borders should be incredibly subtle
  (`dark:border-zinc-800`).
- Always test both modes before delivery.

---

## 6. Standard Layouts

### 6.1 Hero Section
```html
<section class="min-h-[100svh] flex items-center px-6">
  <div class="max-w-7xl mx-auto w-full"><!-- Hero content --></div>
</section>
```

### 6.2 Feature Cards (3-column grid)
```html
<div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8 max-w-7xl mx-auto px-6">
  <div class="bg-surface rounded-2xl p-8 border border-border hover:shadow-lg transition-shadow"><!-- Card --></div>
</div>
```

### 6.3 Alternating Sections (Zebra Stripe)
```html
<section class="py-24 px-6" style="background-color: var(--color-bg-surface);">
<section class="py-24 px-6" style="background-color: var(--color-bg-alt);">
```

### 6.4 Footer
```html
<footer class="border-t border-border py-16 px-6" style="background-color: var(--color-bg-alt);">
  <div class="max-w-7xl mx-auto"><!-- Footer grid --></div>
</footer>
```

---

## 7. Micro-Interactions (CSS-Only)

### 7.1 Reveal on Scroll
```css
.reveal {
  opacity: 0;
  transform: translateY(20px);
  transition: opacity 0.6s ease-out, transform 0.6s ease-out;
}
.reveal.visible {
  opacity: 1;
  transform: translateY(0);
}
```

### 7.2 Magnetic Buttons
```css
.btn-magnetic {
  transition: transform 300ms ease-out;
}
.btn-magnetic:hover {
  transform: scale(1.02);
}
```

### 7.3 Focus States
```css
*:focus-visible {
  outline: 2px solid var(--color-primary-500);
  outline-offset: 2px;
  border-radius: 4px;
}
```

---

## 8. Specificity Overrides for Themed Components

When a base CSS color and a Tailwind utility need to coexist on the same
element (e.g., pagination dots with a default color and an active brand color):

```css
/* Compound selector = higher specificity than a single Tailwind class */
button.dot-class {
  background-color: var(--color-border-subtle); /* Base state */
}
button.dot-class.bg-brand-teal {
  background-color: var(--color-brand-teal); /* Active state wins */
}
```

---

## 9. The `<dialog>` Top Layer Inheritance

The native `<dialog>` element creates a browser "top layer". Despite this,
CSS custom properties defined on `:root` ARE inherited into the top layer.
**NEVER hardcode HEX colors in modals.** Always use `var(--color-bg-surface)`,
`var(--color-text-main)`, etc. The common error is assuming variables don't
inherit and preemptively hardcoding `#0f172a` for dark backgrounds.

---

## 10. PROHIBITIONS (Absolute Rules — No Exceptions)

> These rules are the direct result of post-mortem failures from real projects.

- **NO arbitrary color hex values in HTML:** `bg-[#ff3b30]` is PROHIBITED if
  the project has a `@theme` block defined in `global.css`. Every brand color
  MUST be a named CSS variable exposed as a Tailwind token.
- **Activation Protocol:** Before writing a single Tailwind class on a component,
  READ `src/styles/global.css`. Find all `@theme` tokens. Use ONLY those tokens.
  If no tokens exist yet, STOP and create them first.
- **NO `classList.add('hidden')` on animated elements:** The `hidden` utility
  can lose specificity battles against animated classes in Tailwind v4's CSS
  pipeline. Use `element.style.display = 'none'` directly from JavaScript instead.
- **`@apply` Directive:** Heavily discouraged. If you find yourself writing
  `@apply` for 5+ classes, extract them into a physical Astro component instead
  of polluting the CSS.
- **Arbitrary Values:** `text-[13px]` is forbidden if a design token scale
  exists. Stick to the generated type scale (`text-xs`, `text-sm`).

---

## 11. Tailwind v4 Gotchas

- **Specificity conflict with `hidden` + animations:** When an element has an
  active CSS animation (e.g. `animate-pulse`) and an inline display class
  (`inline-block`), adding `hidden` via `classList` may fail to hide the element
  because the animation class wins the specificity battle. Solution: always use
  `element.style.display` for JS-driven show/hide of animated elements.
- **`@theme` replaces `tailwind.config.js`:** All design tokens (colors, spacing,
  fonts) belong in the CSS file under `@theme {}`, not in a JS config file. The
  JS config is only for plugin registration.

---

## 🔗 AIRON‑Cast Integration

This skill is consumed by:
- `ux-ui_specialist` — to define the theme configuration and token mapping.
- `frontend_worker` — to implement layouts, components, and micro-interactions.

Generated files go to `workspace/<slug>/src/styles/global.css` and
`workspace/<slug>/tailwind.config.mjs`.