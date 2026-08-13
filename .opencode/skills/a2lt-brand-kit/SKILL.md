---
name: a2lt-brand-kit
version: 1.0.0
type: frontend
subtype: skill
tier: all
description: |
  ADN visual A2LT Soluciones: Navbars, SVGs, efectos Neón/Platinum,
  CSS brand-header, brand-effects, hero-layouts y plantillas HTML
  para footers y heroes. Activar cuando se necesite aplicar la
  identidad visual corporativa en cualquier proyecto.
  Trigger phrases: "brand kit", "estilos A2LT", "identidad visual",
  "navbar A2LT", "footer corporativo", "efectos Neón".
  No activar para diseñar desde cero sin marca definida.
triggers:
  primary: ["brand kit", "estilos A2LT", "identidad visual"]
  secondary: ["navbar A2LT", "footer corporativo", "efectos Neón"]
  context: ["branding", "corporate identity"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - ux-ui_specialist
  - frontend_worker
last_used: 2026-06-05
scope: restricted
---

# A2LT Brand Kit Skill

**CRITICAL DIRECTIVE:** This skill represents the definitive "Visual DNA" of Argenis León / A2LT Soluciones. Any agent invoking this skill MUST enforce these standards to prevent generic, template-like UI deliverables.

## 1. The Core Arsenal (Assets)

This skill provides mandatory files located in the `assets/` folder:

- **`css/brand-effects.css`**: The Vault of Visual Authority.
  - Contains `a2lt-shine-*` classes for "Liquid Gold/Platinum" metallic text shines.
  - Contains `a2lt-icon-led` and `--spark-color` variables for the exact 1-Cycle "Electric Spark" hover effects on social media icons.
- **`css/brand-header.css`**: The Authority Header.
  - Glassmorphism header with neon orange border.
  - Logo signature with accent color span.
  - Footer signature with gradient separator and copy toast.
- **`css/hero-layouts.css`**: The Topology Engine.
  - Defines the 3 Laws of Hero (Text-Centered, Split-Hero, Offset-Overlap).
- **`templates/footer-blueprint.html`**: The 5-Column Matrix.
  - Contains exact SVG paths for Facebook, Instagram, LinkedIn, X, YouTube, and TikTok integrated with `a2lt-icon-led` sparks.
  - Contains advanced JavaScript copy-to-clipboard logic for the `mailto:` CTA.
- **`templates/hero-centered-blueprint.html`**: Centered hero with full-viewport background image and overlay.
- **`templates/hero-offset-blueprint.html`**: Offset Overlap hero (60/40 split) with SVG wave separator.
- **`templates/hero-split-blueprint.html`**: Split hero (50/50 text/image division).
- **`scripts/smart-navbar.js`**: The Scroll-Aware Header.
  - Logic for transparent tops, blur-on-scroll, and auto-hiding when the footer is reached.
- **`scripts/generate_humans_txt.py`**: Authorship generator.
  - Drops a `humans.txt` file in the project root, signing the digital product.
- **`templates/humans.txt.j2`**: Template for the humans.txt file.

## 2. Input Contract

**What this skill expects from its caller:**

- **Trigger context:** The UI element (Hero, Footer, Social Icons) being built or audited.
- **Dependencies:** Tailwind CSS must be installed. Bootstrap Icons must be used for SVGs.

## 3. Implementation Directives

### A. The Electric Spark (Social Icons)

DO NOT use generic hover opacities. Use the exact `<a class="a2lt-icon-led [network]-hover">...</a>` structures from `footer-blueprint.html`. Ensure `--spark-color` matches the network's identity.

### B. Hero Topology (Offset Overlap Priority)

Prioritize the **Offset Overlap (60/40 Split Horizontal)** for modern landing pages:
- Top 60% (`h-[60vh]`): Opacified background image with readable Hero Typography.
- Bottom 40% (`h-[40vh]`): Solid surface with sharp SVG Wave separator holding CTAs.
- Right Column: Vertically centered image bridging both zones.

### C. UX Feedback Loop

Generic static buttons are forbidden. Implement immediate visual validation (e.g., Email Copy Button swaps SVG to Checkmark, changes border/bg to `#25D366` for 2000ms before resetting).

## 4. Theming Critical Surfaces (CSS Inline Strategy)

### Rules

1. **CSS Inline for Toggle-Dependent Surfaces:** For backgrounds of sections, cards, modals, and overlays that MUST adapt to Light/Dark themes, use `style="background-color: var(--color-bg-surface);"` directly on the HTML element.

2. **Dynamic Overlay Variables:** The project's `global.css` MUST define a `--color-bg-alt` variable with differentiated Light/Dark values for the "Zebra-Stripe" effect between sections.

3. **Dialog/Modal Theming:** NEVER hardcode HEX colors inside modals. All surfaces and text MUST use `var(--color-bg-surface)`, `var(--color-text-main)`, `var(--color-text-muted)`.

4. **Bounding Box Pattern for Multi-Ratio Logos:** When rendering CMS logos, replace static height classes with a Dynamic Bounding Box:
   ```html
   <img class="w-auto object-contain max-h-[180px] max-w-[320px] md:max-w-[420px]" />
   ```

## 5. Mandatory Authorship

The `scripts/generate_humans_txt.py` MUST be run to drop a `humans.txt` file in the `public/` or `dist/` root of the final project, officially signing the digital product.

---

## 🔗 AIRON‑Cast Integration

This skill is consumed by:
- `ux-ui_specialist` — to define visual identity and apply brand effects.
- `frontend_worker` — to implement headers, footers, heroes and interactive elements.

All assets are stored in `.agents/skills/a2lt-brand-kit/assets/`. Generated components go to `workspace/<slug>/src/`.