---
name: ui-ux-pro-max
version: 1.0.0
type: frontend
subtype: skill
tier: all
description: |
  Design intelligence with a database of styles, color palettes, typography,
  UX guidelines and stack-specific examples. Provides the 4 Premium Authority
  Archetypes, the 6-step Mini-Brief, and the 7-section landing blueprint.
  Trigger phrases: "diseño de landing", "premium landing", "arquetipo visual",
  "paleta de colores", "tipografía", "design system", "UX guidelines".
  Do NOT activate for backend logic or non-visual development tasks.
triggers:
  primary: ["diseño de landing", "premium landing", "design system"]
  secondary: ["paleta de colores", "tipografía", "UX guidelines", "arquetipo visual"]
  context: ["UI design", "visual identity", "branding"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - ux-ui_specialist
  - frontend_worker
last_used: 2026-06-05
scope: restricted
---

# UI/UX Pro Max – Design Intelligence

This skill contains a complete database with:

- 67 UI styles + **4 Premium Authority Archetypes**.
- 96 color palettes categorized by product type.
- 57 typographic pairs with Google Fonts imports.
- 25 chart types with library recommendations.
- 99 prioritized UX guidelines.
- Specific guidelines for 13 tech stacks (React, Astro, Tailwind, etc.).

The data resides in `data/` and the BM25 search engine is implemented in `scripts/`. The main script is `search.py`, which accepts natural language queries and returns relevant results.

## 💎 Premium Landing Intake (The 6-Step Mini-Brief)

When the operator requests a "Premium Landing", "VCard Authority", or a high-converting web project, you MUST implicitly map the user's provided information onto this 6-step brief before generating any design specifications. If critical data is missing (especially Verifiable Proof), you should request it or generate plausible placeholders marked for operator review.

1. **Project Name & Core Offer**: 1 sentence defining the product/service.
2. **Ideal Client**: Target demographic/psychographic.
3. **Problem/Solution Dynamics**: Exactly what pain point is resolved.
4. **Verifiable Proof (Crucial)**: Real numbers, years of experience, or highly plausible metrics. _No generic "high quality" claims._
5. **Main CTA**: Action verb (e.g., Reserve, Join, Order).
6. **Target Visual Archetype**: Selection from the 4 Premium Archetypes (A/B/C/D).

## 🏛️ The 4 Premium Authority Archetypes

Authority pages MUST adopt one of these predefined aesthetic systems to ensure an intentional, "Digital Instrument" feel, avoiding generic AI variations.

### A) "Modern Clinic"

- **Vibe**: Objective, premium consultation, clean, "no mysticism".
- **Palette**: Cream (Background) + Charcoal (Text) + Sober Accent (Clay or Soft Blue).
- **Backgrounds**: Minimalist interiors, marble, glass, soft natural light.
- **Typography**: Modern Sans (Headlines) + Elegant Serif (Short titles).

### B) "Sober Tech"

- **Vibe**: Serious B2B product, "this just works".
- **Palette**: Dark Background + Cool Accent (Blue / Turquoise).
- **Backgrounds**: Blurred macro tech, discreet deep gradients.
- **Typography**: Grotesk (Headlines) + Clean Monospace (Metrics/Data).

### C) "Luxury Editorial"

- **Vibe**: High-end magazine, fashion show, creative architecture.
- **Palette**: Ivory + True Black + Soft Gold Accent.
- **Backgrounds**: Architectural shadows, fine paper textures, film grain.
- **Typography**: Protagonist Serif (High Contrast) + Minimalist Sans (Body).

### D) "Cinematic Travel"

- **Vibe**: Premium agency, wide epic scales.
- **Palette**: Warm Neutrals + Terracotta/Earthy Accent.
- **Backgrounds**: Epic landscapes with warm lighting.
- **Typography**: Wide Sans + Serif for specific keywords.

## 🏗️ Premium Landing Structure (The 7-Section Blueprint)

For Authority and VCard projects, the landing page MUST follow this fixed sequence. It ensures narrative flow, trust building, and conversion optimization without feeling templated.

1. **Hero** – Strong headline + short subhead + 2 CTAs. Authority badge (use the Verifiable Proof from the brief).
2. **Problem → Solution (Double column)** – Left: real problem (3 bullets). Right: solution (3 bullets). Animation: smooth scroll reveal (no fireworks).
3. **How it Works (Timeline)** – 3 numbered steps (01 / 02 / 03). Each step with a distinct micro‑animation (subtle).
4. **Evidence (Dynamic social proof)** – Slow carousel of "results" (numbers or mini case studies). Alternate "before/after" or "situation/result". No generic testimonials; sound plausible.
5. **Services / Plans** – If pricing exists: 3 plans, middle one highlighted. If no pricing: 3 service blocks + CTA.
6. **Quick Questions (FAQ)** – 4 real questions (no filler). Smooth accordion animation.
7. **Closing** – Strong CTA + low‑friction microcopy ("takes 30 seconds", "no commitment"). Clean footer with links and legal.

## ✨ Premium Micro-Interactions (Tailwind / CSS-Only Rule)

For Authority and VCard standards, **DO NOT USE GSAP** to preserve extreme lightness and performance. All interactions must be resolved via CSS/Tailwind and the native `IntersectionObserver` (`.reveal` classes).

1. **Anti-Template Materiality (Noise)**: Apply a global CSS `noise` overlay to eliminate "flat" AI looks. Use an absolutely positioned SVG `<filter id="noise"><feTurbulence type="fractalNoise" baseFrequency="0.8" numOctaves="4" stitchTiles="stitch"/></filter>` with opacity around `0.03` to `0.05`.
2. **Magnetic Buttons**: Apply subtle scaling on hover (`hover:scale-[1.02] transition-transform duration-300 ease-out`).
3. **Smooth Reveals**: Elements entering the viewport should fade/translate up smoothly. Use CSS `@keyframes fadeUp` triggered purely by the `.reveal.visible` class added by JS.
4. **No Lorem Ipsum**: Never use placeholder text. Inject realistic, context‑aware copy based on the Mini-Brief.

## 📌 When to use this skill

- The user asks to design a landing page, Authority page, or VCard.
- They need to map an incoming project to one of the 4 Premium Archetypes.
- They need to calculate a color palette or typographic pairing.
- They request accessibility or UX best practices.

## 🛠️ How to use the skill

### Step 1: Analyze user requirements

Extract from the message:

- **Product type** / **Archetype target**.
- **Style keywords**: minimal, elegant, dark mode.
- **Stack**: React, Astro, Tailwind.

### Step 2: Generate complete design system (if applicable)

Whenever the project requires a visual identity, execute:

```bash
python scripts/search.py "<product> <industry> <keywords>" --design-system -p "Project Name"
```

_(Use python3 if required by OS)_

### Step 3: Complement with detailed searches

If more information is needed:

```bash
python scripts/search.py "<keyword>" --domain <domain> [-n <max_results>]
```

Available domains: `style`, `color`, `typography`, `chart`, `ux`, `landing`, `product`, `prompt`, `icons`, `react`, `web`.

### Step 4: Obtain stack-specific guides

```bash
python scripts/search.py "<keyword>" --stack <stack>
```

Available stacks: `html-tailwind`, `react`, `nextjs`, `astro`, `vue`, `nuxtjs`, `nuxt-ui`, `svelte`, `swiftui`, `react-native`, `flutter`, `shadcn`, `jetpack-compose`.

### Step 5: Synthesize and implement

You MUST combine the obtained information (BM25 matches + The 4 Archetypes) and apply it to the generated code. Follow priority guidelines (critical accessibility first). For Authority projects, ensure the landing follows the 7‑Section Blueprint and uses CSS‑only micro‑interactions.

## ⚠️ Common rules for professional UI

- **Icons**: always use SVG (Lucide, Heroicons), never emojis.
- **Cursor**: `cursor-pointer` on clickable elements.
- **Hover**: smooth transitions (`duration-300`).
- **Contrast**: text on light background minimum 4.5:1.
- **Dark mode**: test both modes, use `dark:` classes when applicable (unless constrained to strict dark VCard).

## ⛔ Mandatory Enforcement Rules

### Rule 1: Anti-Mediocrity Guard

If the search returns generic fallback results, you MUST try more specific keywords. NEVER blindly implement "Minimalism" when the user asked for "Luxury Editorial". Map requests to the 4 Premium Archetypes when dealing with landing pages.

### Rule 2: MASTER.md Consultation Directive

If `--persist` was used and a `design-system/<project>/MASTER.md` exists:

1. You MUST read `MASTER.md` BEFORE writing any component.
2. All CSS variables must comply with MASTER.

### Rule 3: Conflict Resolution

If `web-design-guidelines` flags a conflict, correct it locally. If a discrepancy exists between default heuristic and `MASTER.md`, `MASTER.md` wins.

---

## 🔗 AIRON‑Cast Integration

This skill is consumed by:
- `ux-ui_specialist` — to define design tokens, palettes, and layouts.
- `frontend_worker` — to implement components with the correct styles and archetypes.

Design artifacts generated with `--persist` are stored in `workspace/<slug>/design-system/`, accessible to the entire taskforce.