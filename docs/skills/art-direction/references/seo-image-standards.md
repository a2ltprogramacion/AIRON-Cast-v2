# SEO & Performance Standards for Enterprise Web Images

Mandatory standards for all images in A2LT web projects. Compliance directly impacts Core Web Vitals (LCP, CLS), search rankings, and social visibility.

---

## 1. Format Hierarchy & Fallback

| Priority | Format       | Use Case                                                | Transparency |
| -------- | ------------ | ------------------------------------------------------- | ------------ |
| 1st      | **AVIF**     | Best compression/quality — progressive enhancement      | ✅           |
| 2nd      | **WebP**     | Broad browser support (97%+) — default for broad compat | ✅           |
| 3rd      | **PNG**      | Only when transparency required                         | ✅           |
| 4th      | **JPEG**     | Legacy fallback ONLY                                    | ❌           |
| ❌       | GIF/BMP/TIFF | NEVER for web                                           | —            |

### Progressive Enhancement Pattern

```html
<picture>
  <source srcset="image.avif" type="image/avif" />
  <source srcset="image.webp" type="image/webp" />
  <img
    src="image.jpg"
    alt="Descriptive text"
    width="1920"
    height="1080"
    loading="lazy"
    decoding="async"
  />
</picture>
```

### JPEG XL Monitoring Note

Chrome's Chromium team reversed its 2022 decision and will restore JPEG XL support via Rust decoder. Implementation is feature-complete but NOT yet in Chrome stable. When available, add `<source srcset="image.jxl" type="image/jxl">` after AVIF. ~20% lossless JPEG recompression.

---

## 2. Tiered File Size Budgets

All images must fall under **Target**. If size hits **Warning**, log warning but accept. If exceeds **Critical**, **REJECT** and re-prompt or recompress.

| Asset Type          | Target (KB) | Warning (KB) | Critical (KB) |
| ------------------- | ----------- | ------------ | ------------- |
| Hero (full-width)   | ≤ 150       | 151-250      | > 250         |
| Service Card        | ≤ 50        | 51-100       | > 100         |
| Avatar              | ≤ 20        | 21-40        | > 40          |
| Logo                | ≤ 15        | 16-30        | > 30          |
| Texture (bg)        | ≤ 100       | 101-200      | > 200         |
| OG Image (1200×630) | ≤ 100       | 101-150      | > 150         |
| Before/After        | ≤ 200       | 201-300      | > 300         |
| Infographic         | ≤ 200       | 201-350      | > 350         |
| Blog/Content Image  | ≤ 100       | 101-150      | > 300         |
| Product Shot        | ≤ 100       | 101-200      | > 300         |

**Compression:** WebP quality 80-85%, AVIF effort 4 quality 60-80, JPEG quality 85 progressive.

---

## 3. Responsive Images with srcset

Generate at minimum 3 breakpoints:

| Breakpoint | Viewport   | Image Width        |
| ---------- | ---------- | ------------------ |
| Mobile     | ≤ 640px    | 640px              |
| Tablet     | 641-1024px | 1024px             |
| Desktop    | ≥ 1025px   | 1920px (or native) |

```html
<img
  srcset="hero-640w.webp 640w, hero-1024w.webp 1024w, hero-1920w.webp 1920w"
  sizes="(max-width: 640px) 100vw, (max-width: 1024px) 100vw, 90vw"
  src="hero-1920w.webp"
  alt="Descriptive, keyword-rich alt text"
  width="1920"
  height="1080"
  loading="lazy"
  decoding="async"
/>
```

In Astro, use `<Image />` from `astro:assets` with `widths={[640, 1024, 1920]}` and `formats={['avif', 'webp']}`.

---

## 4. Loading Strategy (Core Web Vitals)

### Hero / LCP Image

```html
<img
  src="hero.webp"
  loading="eager"
  fetchpriority="high"
  decoding="async"
  width="1920"
  height="1080"
  alt="..."
/>
```

- `loading="eager"` — Do NOT lazy-load the LCP element.
- `fetchpriority="high"` — Prioritize in browser's network queue.
- `decoding="async"` — Don't block rendering while decoding.
- Consider `<link rel="preload" as="image" href="hero.webp">` in `<head>`.

### Below-Fold Images

```html
<img
  src="photo.webp"
  loading="lazy"
  decoding="async"
  width="800"
  height="600"
  alt="..."
/>
```

### CLS Prevention (MANDATORY)

EVERY `<img>` MUST have `width` and `height` attributes. CSS safety net:

```css
img {
  aspect-ratio: attr(width) / attr(height);
  max-width: 100%;
  height: auto;
}
```

In Astro, `<Image />` handles this automatically when you provide the image import.

---

## 5. Alt Text Standards

1. **Descriptive and Specific:** Describe what image SHOWS, not what it IS.
   - ❌ "hero image", "background", "photo 1", "image.jpg"
   - ✅ "Red de fibra óptica convergente representando conectividad empresarial"
2. **Keywords Naturally:** Incorporate relevant terms without stuffing.
3. **Page Language:** Alt text in same language as page content.
4. **Max Length:** ≤ 125 characters (screen reader truncation point).
5. **Decorative Images:** Use `alt=""` (empty string). NEVER omit `alt` attribute entirely.
6. **Functional Images:** Logos linking to home → `alt="[Brand] - Home"`.
7. **Complex Images:** Infographics → provide extended description via `aria-describedby`.

---

## 6. File Naming Convention

`[asset-type]-[brief-description].[ext]`

Examples: `hero-cloud-connectivity.avif`, `avatar-ceo-silhouette.webp`, `service-data-analytics.webp`

Rules: hyphens, no spaces, all lowercase, 2-5 keyword description.

---

## 7. Open Graph & Social Media

| Platform                          | Dimensions     | Aspect Ratio |
| --------------------------------- | -------------- | ------------ |
| OG (Facebook, LinkedIn, WhatsApp) | 1200 × 630 px  | ~1.91:1      |
| Twitter Card (Large)              | 1200 × 600 px  | 2:1          |
| Instagram                         | 1080 × 1080 px | 1:1          |
| LinkedIn                          | 1200 × 627 px  | ~1.91:1      |

```html
<meta property="og:image" content="https://domain.com/images/og-share.webp" />
<meta property="og:image:width" content="1200" />
<meta property="og:image:height" content="630" />
<meta property="og:image:alt" content="Descriptive alt for social preview" />
<meta name="twitter:card" content="summary_large_image" />
```

**OG Best Practices:** No small text (unreadable on mobile feeds), brand logo visible, critical content in center 80%, MUST be absolute URL.

---

## 8. Schema.org ImageObject

```json
{
  "@context": "https://schema.org",
  "@type": "ImageObject",
  "contentUrl": "https://domain.com/images/hero-bg.webp",
  "width": 1920,
  "height": 1080,
  "encodingFormat": "image/webp",
  "caption": "Keyword-rich description",
  "creditText": "A2LT Digital Studio",
  "creator": { "@type": "Organization", "name": "A2LT Soluciones" },
  "copyrightNotice": "© 2026 A2LT Soluciones",
  "representativeOfPage": true
}
```

---

## 9. Compression Checklist (8 Checks)

| #   | Check                                                  | Method                                 |
| --- | ------------------------------------------------------ | -------------------------------------- |
| 1   | Format is AVIF/WebP?                                   | Astro `<Image />` or manual conversion |
| 2   | Size within budget?                                    | File properties vs tiered thresholds   |
| 3   | `width` + `height` in HTML?                            | Grep for `<img` without dimensions     |
| 4   | Hero uses `loading="eager"` + `fetchpriority="high"`?  | Source verification                    |
| 5   | Below-fold uses `loading="lazy"` + `decoding="async"`? | Source verification                    |
| 6   | Alt text descriptive (≤125 chars)?                     | Manual review                          |
| 7   | OG 1200×630 with absolute URL?                         | Social media debugger                  |
| 8   | No visible artifacts (banding, blocking)?              | Visual inspection                      |

## 10. Performance Budget Enforcement

The agent MUST **reject** any image exceeding **Critical** threshold. If between Target and Warning, log warning but accept. If below Target, the image passes cleanly.
