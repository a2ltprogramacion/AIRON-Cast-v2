---
name: art-direction
description: |
  Dirección Artística Digital para generación de imágenes de marketing y páginas web Enterprise-Grade.
  Actívala cuando se necesiten imágenes (hero backgrounds, ilustraciones de servicios, avatares, logos abstractos, texturas, gráficos sociales, antes/después).
  Proporciona frameworks de prompt engineering visual, patrones por industria, estándares SEO de imágenes y plantillas reutilizables.
  No activar para tareas de código, lógica backend, o configuración de servidores.
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Art Direction Skill (A2LT Digital Studio)

**CRITICAL DIRECTIVE:** This skill transforms Antigravity from a generic image generator into a **Digital Art Director**. Every image produced under this skill MUST pass the **"Would I Pay For This?"** test — quality high enough that a client prefers it over stock photography. Mediocre AI images scream "cheap automation" to visitors.

**Tool Mandate:** Visual assets are generated EXCLUSIVELY via the `generate_image` tool. PROHIBITED: Python/Pillow scripts, `sharp`/`imagemagick` CLI, downloading icon libraries from NPM.

## Input Contract

| Parameter                 | Type              | Required | Source / Notes                                                                                                                                                                       |
| ------------------------- | ----------------- | -------- | ------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------ |
| `brand_palette`           | Object (CSS vars) | Yes      | Project's `global.css` or `tailwind.config.mjs`; must include primary, secondary, accent, neutral, background                                                                        |
| `asset_type`              | String            | Yes      | One of: `hero-abstract`, `hero-environmental`, `service-isometric`, `service-flat`, `avatar`, `logo`, `texture`, `og-image`, `before-after`, `product`, `testimonial`, `infographic` |
| `target_industry`         | String            | No       | Overrides default industry patterns (see `references/industry-patterns.md`)                                                                                                          |
| `brand_personality`       | String[]          | No       | Tone descriptors: e.g., `["trustworthy", "innovative", "minimal"]` — influences style and color                                                                                      |
| `negative_space_required` | Boolean           | No       | Default `false`; set `true` for hero backgrounds needing text overlay                                                                                                                |
| `aspect_ratio`            | String            | No       | If omitted, uses default per asset type from `assets/prompt-templates.md`                                                                                                            |
| `mood`                    | String            | No       | e.g., `"calm"`, `"energetic"`, `"luxury"` — overrides default mood                                                                                                                   |
| `seo_priority`            | String            | No       | `"LCP"` or `"non-LCP"` — influences loading strategy defaults                                                                                                                        |

---

## 1. Anti-Mediocrity Manifesto

### Absolute Prohibitions

| Prohibition                        | Why It Fails                                               | What To Do Instead                                       |
| ---------------------------------- | ---------------------------------------------------------- | -------------------------------------------------------- |
| Visible text/words in images       | AI text is ALWAYS garbled/misspelled                       | Use "no text, no letters, no words" in EVERY prompt      |
| Stock-photo clichés                | Handshakes, stethoscopes, call-center headsets, lightbulbs | Use abstract metaphors, editorial angles                 |
| Oversaturated neon without purpose | Screams "AI art" immediately                               | Lock to project's actual brand palette                   |
| Centered symmetrical composition   | Boring, predictable, template-like                         | Rule of thirds, asymmetric tension, negative space       |
| Flat gradient backgrounds          | Zero depth, zero interest                                  | Subtle textures, lighting effects, environmental context |
| Competing subjects                 | Confusing, unfocused, cheap                                | One clear focal point per image                          |
| Photorealistic human faces         | High risk of uncanny valley artifacts                      | Stylized illustrations or abstract representations       |
| Clichéd metaphors                  | Lightbulb=idea, puzzle=solution, rocket=growth             | Original visual metaphors tied to the brand              |

### Quality Gate Thresholds

Every generated image must pass ALL of these:

1. **Composition:** Intentional framing (rule of thirds, leading lines)? Not accidental?
2. **Brand Lock:** Color palette strictly adheres to brand constraints?
3. **Visual Hierarchy:** Clear hierarchy of elements?
4. **Enterprise Credibility:** Would this look credible on a Fortune 500 landing page?
5. **Emotional Response:** Does it evoke the intended mood?
6. **Lighting Consistency:** Lighting is consistent and purposeful?
7. **Artifact-Free:** No weird hands, distorted faces, unnatural seams?
8. **AI Detection:** Could this be mistaken for a generic AI image? (if yes → FAIL)

---

## 2. The 5-Pillar Prompt Engineering Framework

Every `generate_image` call MUST compose the prompt using these 5 pillars IN ORDER:

```
[SUBJECT] + [STYLE DIRECTIVE] + [COMPOSITION/CAMERA] + [COLOR PALETTE LOCK] + [TECHNICAL/NEGATIVES]
```

**Pillar 1 — Subject/Concept:** What is the image about? Be concrete and specific. Include key objects, characters, or metaphors. Avoid ambiguity about quantity, orientation, and relationships.

**Pillar 2 — Style Directive:** Art style + influence + texture. Full vocabulary: `references/prompt-anatomy.md` Block 2.

> ⚠️ Named artist influences ("in the style of Mondrian") may not be understood by all generators. Use descriptive equivalents: "geometric abstraction with primary colors and black grid lines".

**Pillar 3 — Composition/Camera:** Framing, angle, lens, arrangement, depth. Critical for ensuring image works IN CONTEXT (hero needs negative space, service card needs centered subject).

**Pillar 4 — Color Palette Lock:** INJECT brand colors using descriptive names. Pattern: "using a color palette of [color1-name], [color2-name], and [color3-name] tones..."

**Pillar 5 — Technical Specs & Negative Prompts:** Aspect ratio, resolution hints, guidance scale, and MANDATORY negative prompts (universal + context-specific). See `references/prompt-anatomy.md` Block 7-8.

---

## 3. Asset Types & Templates

See `assets/prompt-templates.md` for complete templates per asset type (12 types), including **mood variants** (calm, energetic, luxury, minimalist) for key assets.

## 4. SEO & Performance Standards

See `references/seo-image-standards.md` for format hierarchy (AVIF > WebP > JPEG), tiered file size budgets, responsive srcset, loading strategies, alt text rules, and Schema.org markup.

## 5. Industry Visual Strategies

See `references/industry-patterns.md` for 9+ industry-specific visual recommendations with **psychological reasoning** behind each decision plus explicit anti-patterns.

---

## 6. Quality Gate (Self-Audit — 9 Checks)

Before accepting any generated image:

| #   | Check                                                                               | Action if FAIL                            |
| --- | ----------------------------------------------------------------------------------- | ----------------------------------------- |
| 1   | **Brand Compliance:** Colors match palette (±10% perceptual shade allowed)?         | Reinforce brand colors in prompt by name  |
| 2   | **Composition Integrity:** No cropped elements, focal point clear?                  | Adjust framing keywords                   |
| 3   | **Text Overlay Space:** If `negative_space_required`, ≥40% low-detail area?         | Add "empty [side] third for text overlay" |
| 4   | **No Artifacts:** No weird hands, distorted faces, lighting seams?                  | Reinforce negative prompts                |
| 5   | **Emotional Alignment:** Does image evoke intended mood?                            | Change lighting or style directive        |
| 6   | **Uniqueness:** Not a generic/symmetric composition?                                | Add asymmetric tension, editorial angle   |
| 7   | **SEO Readiness:** Alt text written, filename follows `[type]-[description].[ext]`? | Generate before delivery                  |
| 8   | **File Size:** Below Warning threshold for asset type?                              | Compress with WebP quality 80-85%         |
| 9   | **Accessibility:** Sufficient contrast if used with text overlay?                   | Adjust background darkness                |

If any check fails, apply **Iterative Refinement** (see `references/prompt-anatomy.md` §Iterative Refinement) — adjust guidance scale, strengthen negatives, change style, simplify palette.

---

_Forge Note: Reforged via complete pipeline: forge-ignition → brainstorming → find-skills (3 external skills absorbed: seo-images, prompt-engineering, image-generation) → Blueprint sign-off → DeepSeek Bridge (Bi-Modelo anti-brevity) → forge-shutdown._
_Post-mortem ref: `journal/2026-03-03_CRITICAL_protocol_failure_art_direction.md`._
