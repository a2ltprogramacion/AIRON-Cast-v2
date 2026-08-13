# Reusable Prompt Templates by Asset Type

Each template follows the 8-block structure from `references/prompt-anatomy.md`. Replace `[bracketed]` values with project-specific details. Multiple **mood variants** provided for key asset types.

---

## Quick Reference Table

| Asset Type         | Template | Ratio        | Max Size (KB) | Loading               |
| ------------------ | -------- | ------------ | ------------- | --------------------- |
| Hero Abstract      | §1       | 16:9         | 150           | eager + fetchpriority |
| Hero Environmental | §2       | 16:9 or 21:9 | 150           | eager + fetchpriority |
| Service Isometric  | §3       | 4:3 or 1:1   | 50            | lazy + decoding=async |
| Service Flat       | §4       | 1:1          | 50            | lazy + decoding=async |
| Avatar             | §5       | 1:1          | 20            | lazy + decoding=async |
| Logo               | §6       | 1:1          | 15            | eager (if LCP)        |
| Texture            | §7       | 1:1          | 100           | lazy + decoding=async |
| OG Image           | §8       | 1.91:1       | 100           | N/A (meta)            |
| Before/After       | §9       | 16:9 or 2:1  | 200           | lazy + decoding=async |
| Product            | §10      | 4:3          | 100           | lazy + decoding=async |
| Testimonial        | §11      | 1:1          | 50            | lazy + decoding=async |
| Infographic        | §12      | 2:1          | 200           | lazy + decoding=async |

---

## §1. Hero Abstract (Technology, Finance, Abstract)

**Default — Innovative & Trustworthy:**

```
Abstract representation of [concept: e.g., cloud computing], geometric shapes floating in space, interconnected lines and nodes,
3D render, smooth surfaces, studio soft lighting with volumetric glow,
composition: rule of thirds, wide angle, shallow depth of field, empty [left/right] third for text overlay,
color palette: [brand-primary] with [brand-accent] accents, [brand-neutral] background,
high detail, 8k, aspect ratio 16:9,
no text, no watermark, no stock clichés, no literal objects, no oversaturated
```

**Mood: Energetic & Dynamic:**

```
Abstract data flow, swirling particles, speed lines, vibrant motion,
cinematic photography style, dynamic lighting with neon streaks,
composition: diagonal lines, dutch angle, motion blur, empty [side] for text,
color palette: [brand-primary] with neon [brand-accent] accents,
high contrast, sharp, 8k, 16:9,
no static, no flat, no dull, no text, no watermark
```

**Mood: Calm & Serene:**

```
Abstract landscape of gentle curves, soft gradients, serene atmosphere,
digital painting, soft pastel textures, diffused lighting,
composition: centered, minimalist, generous negative space for text,
color palette: monochromatic [brand-primary] with cream accents,
smooth gradients, low contrast, 4k, 16:9,
no harsh lines, no clutter, no noise, no text, no watermark
```

---

## §2. Hero Environmental (Real Estate, Travel, Lifestyle)

**Default — Aspirational:**

```
[Scene: e.g., modern architectural facade with pool], golden hour lighting, lush greenery,
architectural photography, tilt-shift lens, warm natural light,
composition: wide shot, leading lines towards entrance, symmetry, empty [side] for text,
color palette: earth tones, warm neutrals, sky blue,
photorealistic, high detail, 16:9,
no people, no clutter, no oversaturated HDR, no cloudy sky, no text, no watermark
```

---

## §3. Service Isometric (SaaS, IT, Business)

**Default — Efficient & Modern:**

```
Isometric 3D illustration of [service concept as physical metaphor],
clay render style, soft studio lighting, clean ambient occlusion shadows,
composition: bird's-eye view, geometric layout, depth, centered,
color palette: [brand-primary] and [brand-accent] on [brand-bg] background,
sharp lines, 4k, aspect ratio 4:3,
no text, no photorealistic faces, no cluttered elements, no watermark
```

---

## §4. Service Flat (Creative, Education, Health)

**Default — Friendly & Clear:**

```
Flat vector illustration of [service concept], abstract figures interacting,
simple shapes, bright solid colors, no gradients, clean lines,
composition: centered, circular elements for community,
color palette: [brand-primary] and [brand-secondary] with white space,
crisp SVG-like lines, 1:1 square format,
no shadows, no depth, no 3D effects, no text, no watermark
```

---

## §5. Avatar (Team, Testimonials)

**Default — Professional & Inclusive:**

```
Stylized abstract avatar of a [role: e.g., CEO], minimalist geometric features,
vector style, flat colors, soft circular [brand-bg] background,
composition: head and shoulders, slight profile angle,
color palette: [brand-accent] background, neutral warm skin tones,
square 1:1, high contrast, crisp lines,
no photorealistic faces, no gender stereotypes, no text, no watermark, no extra fingers
```

**Mood: Friendly & Approachable:**

```
Friendly abstract avatar, rounded shapes, warm colors, gentle expression (abstract),
digital painting with soft textures, gentle side lighting,
composition: head and shoulders, soft focus [brand-light] background,
color palette: warm [brand-accent], pastel background,
square 1:1,
no harsh lines, no cold colors, no text, no watermark
```

---

## §6. Logo (Abstract Brand Mark)

**Default — Minimalist & Memorable:**

```
Abstract geometric logo mark representing [brand essence: e.g., connection],
vector graphic, clean lines, flat colors, interlocking forms,
composition: centered, balanced, elegant negative space,
color palette: [brand-primary] only, solid white background,
high contrast, scalable, square format,
no gradients, no shadows, no text, no letters, no words, no typography, no initials, no watermark
```

---

## §7. Texture / Pattern

**Default — Subtle & Professional:**

```
Seamless [pattern type: e.g., light geometric grid, topographic lines] pattern,
subtle grain, very low contrast against [brand-bg],
digital texture, soft uniform lighting, no focal point,
color palette: [brand-neutral] monochromatic,
square 1:1, seamless tileable edges, low visual weight,
no objects, no subjects, no depth, no highlights, no text, no watermark
```

**Mood: Organic & Natural:**

```
Organic texture of soft waves like sand dunes, natural grain,
macro photography of natural material surface,
abstract close-up, no repetition visible,
color palette: earth tones, warm beige,
square 1:1,
no geometric shapes, no harsh lines, no text, no watermark
```

---

## §8. OG / Social Share Image

**Default — Brand-Centric:**

```
Abstract background representing [topic], subtle brand elements,
gradient from [brand-primary] to [brand-secondary], soft geometric shapes,
composition: generous negative space in center for text overlay (text added later in CSS/HTML),
color palette: [brand-colors], high contrast for readability,
1200x630 ultra-wide format, 8k, minimal detail to keep file compact,
no text, no letters, no complex subjects, no cluttered, no watermark
```

---

## §9. Before/After (Transformations)

**Default — Comparative:**

```
Split screen composition showing [before concept] on left and [after concept] on right,
clean divide line, both sides consistent style,
3D render, neutral even lighting, even exposure,
color palette: [brand-neutrals] with [brand-accent] on "after" side,
side-by-side 2:1 aspect ratio, high detail,
no text, no labels, no cluttered background, no watermark
```

---

## §10. Product (Mockup / Showcase)

**Default — Sleek & Focused:**

```
Product shot of [item] on clean minimal surface,
studio photography style, softbox lighting, shallow depth of field,
composition: three-quarter view, rule of thirds, subject centered,
color palette: [brand-colors] with neutral background,
4K, sharp focus on product, 4:3 format,
no cluttered props, no harsh shadows, no text, no watermark
```

---

## §11. Testimonial (Quote Background)

**Default — Trustworthy & Warm:**

```
Abstract background with subtle curves suggesting conversation,
soft gradients, gentle diffused lighting,
composition: ample negative space for text overlay (quote + attribution),
color palette: [brand-light-neutrals] with subtle [brand-accent],
1:1 square, low detail, soft focus,
no distracting elements, no text, no watermark
```

---

## §12. Infographic (Data Visualization)

**Default — Clear & Engaging:**

```
Abstract infographic-style visualization of [data concept], charts and icons,
flat vector style, clean lines, color-coded sections,
composition: grid layout, hierarchical flow, organized,
color palette: [brand-colors] for categories, [brand-neutral] background,
high resolution, 2:1 landscape aspect ratio,
no 3D effects, no clutter, no unreadable text, no watermark
```

---

## Usage Instructions

1. Select template by `asset_type` from Input Contract.
2. Replace `[bracketed]` placeholders with brand-specific values.
3. If `mood` is provided in Input Contract, use the matching mood variant.
4. Verify `aspect_ratio` matches target from Quick Reference.
5. After generation, run through Quality Gate (SKILL.md §6).
6. Verify file size against SEO budgets (`references/seo-image-standards.md` §2).
