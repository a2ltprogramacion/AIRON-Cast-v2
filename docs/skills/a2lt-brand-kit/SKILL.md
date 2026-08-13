---
name: a2lt-brand-kit
description: |
  Inyecta el ADN Visual y Arquitectónico de A2LT Soluciones (CSS, Navbars, SVGs).
  Actívala cuando el usuario necesite diseñar o auditar componentes UI, headers, footers, aplicar efectos Neón/Platinum, o requiera layouts Hero (Offset-Overlap).
  No activar para tareas exclusivas de lógica backend, base de datos o configuraciones de servidor.
---

# A2LT Brand Kit Skill

**CRITICAL DIRECTIVE:** This skill represents the definitive "Visual DNA" of Argenis León / A2LT Soluciones. Any Agent (specifically `a2lt-brand-curator`) invoking this skill MUST enforce these standards to prevent generic, template-like UI deliverables.

## 1. The Core Arsenal (Assets)

This skill provides mandatory files located in the `assets/` folder alongside this SKILL.md file (typically `.agent/skills/a2lt-brand-kit/assets/` in client payloads):

- **`css/brand-effects.css`**: The Vault of Visual Authority.
  - Contains `a2lt-shine-*` classes for "Liquid Gold/Platinum" metallic text shines.
  - Contains `a2lt-icon-led` and `--spark-color` variables for the exact 1-Cycle "Electric Spark" hover effects on social media icons.
- **`css/hero-layouts.css`**: The Topology Engine.
  - Defines the 3 Laws of Hero (Text-Centered, Split-Hero, Offset-Overlap).
- **`templates/footer-blueprint.html`**: The 5-Column Matrix.
  - Contains exact SVG paths (from Bootstrap Icons) for Facebook, Instagram, LinkedIn, X, YouTube, and TikTok integrated with `a2lt-icon-led` sparks.
  - Contains advanced JavaScript copy-to-clipboard logic for the `mailto:` CTA, swapping icons to a green `bi-clipboard-check` and flashing WhatsApp Green (`#25D366`) on success.
- **`js/smart-navbar.js`**: The Scroll-Aware Header.
  - Logic for transparent tops, blur-on-scroll, and auto-hiding when the footer is reached.

## 2. Input Contract

**What this skill expects from its caller (User or Agent):**

- **Trigger context:** The UI element (Hero, Footer, Social Icons) that is being built or audited.
- **Target OS Environment:** N/A (CSS/HTML are platform agnostic).
- **Dependencies:** Tailwind CSS must be installed in the project. Bootstrap Icons must be used for SVGs.

## 3. Implementation Directives

When building or auditing a project interface, apply these components:

### A. The Electric Spark (Social Icons)

DO NOT use generic hover opacities. Use the exact `<a class="a2lt-icon-led [network]-hover">...</a>` structures from `footer-blueprint.html`. Ensure `--spark-color` matches the network's identity (e.g., `#ffd700` for Instagram, `#00ffff` for LinkedIn).

### B. Hero Topology (Offset Overlap Priority)

Prioritize the **Offset Overlap (60/40 Split Horizontal)** for modern landing pages.

- Top 60% (`h-[60vh]`): Opacified background image (`z-0`) with readable Hero Typography (`z-10`).
- Bottom 40% (`h-[40vh]`): Solid surface with a sharp, non-blurred SVG Wave separator on the left side holding CTA buttons.
- Right Column: A highly-curated image, vertically perfectly centered (`top-1/2 -translate-y-1/2`), bridging both the 60% and 40% zones.

### C. UX Feedback Loop

Generic static buttons are forbidden. Implement immediate visual validation:

- Example: The Email Copy Button in `footer-blueprint.html` swaps its SVG to a Checkmark and changes border/bg color to `#25D366` for exactly 2000ms before resetting. Replicate this UX logic for all critical data-copy actions.

## 4. Theming Critical Surfaces (CSS Inline Strategy)

> **POST-MORTEM ORIGIN:** Multiple components lost their backgrounds in Light/Dark toggle because they used Tailwind classes referencing variables in `@layer base` (which don't generate utilities). This section mandates the correct approach.

### Rules

1. **CSS Inline for Toggle-Dependent Surfaces:** For backgrounds of sections, cards, modals, and overlays that MUST adapt to Light/Dark themes, it is LEGITIMATE and RECOMMENDED to use `style="background-color: var(--color-bg-surface);"` directly on the HTML element, instead of a Tailwind class that may not exist.

2. **Dynamic Overlay Variables:** The project's `global.css` MUST define a `--color-bg-alt` variable with differentiated values:
   - **Light mode:** alternates between `white` (#ffffff) and `slate-50` (#f8fafc)
   - **Dark mode:** alternates between `slate-900` (#0f172a) and `slate-950` (#020617)
     This enables the "Zebra-Stripe" effect between sections without damaging specific component aesthetics.

3. **Dialog/Modal Theming:** The native `<dialog>` element inherits CSS custom properties from `:root`. NEVER hardcode HEX colors inside modals. All modal surfaces and text MUST use `var(--color-bg-surface)`, `var(--color-text-main)`, `var(--color-text-muted)`.

4. **Bounding Box Pattern for Multi-Ratio Logos:** When rendering logos from CMS (which may be square, horizontal, or vertical), replace static height classes (`h-10`, `max-h-16`) with a Dynamic Bounding Box:
   ```html
   <img
     class="w-auto object-contain max-h-[180px] max-w-[320px] md:max-w-[420px]"
   />
   ```
   This ensures visual impact regardless of logo geometry.

## 5. Mandatory Authorship

The `scripts/generate_humans.py` MUST be run to drop a `humans.txt` file in the `public/` or `dist/` root of the final project, officially signing the digital product with:
`Powered by ⚡ A2LT Soluciones (https://a2lt.netlify.app/)`

---

_Forge Note: This skill enforces the "Creativity & Excellence Compliance" mandate. Simplicity without user-explicit authorization is a failure._
