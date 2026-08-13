---
name: astro-project-standards
description: "Estándares de calidad A2LT para proyectos Astro. Garantiza que cada proyecto incluya robots.txt, humans.txt (créditos A2LT), netlify.toml con security headers, sitemap, y estructura SEO completa antes del primer commit."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# Astro Project Standards (A2LT Baseline)

This skill defines the non-negotiable baseline files that EVERY Astro project must have before it can be considered deployable. This checklist was born from a post-mortem where security headers, sitemap, and robots.txt were omitted in an initial scaffold and had to be retroactively added.

---

## 1. Required Files Checklist

Before declaring any Astro project ready for first deploy, verify ALL of the following exist:

| File                | Location                             | Status Check                             |
| ------------------- | ------------------------------------ | ---------------------------------------- |
| `robots.txt`        | `public/robots.txt`                  | Must exist and block `/admin/`           |
| `humans.txt`        | `public/humans.txt`                  | Must credit A2LT Soluciones as developer |
| `netlify.toml`      | Project root                         | Must include security headers            |
| `sitemap-index.xml` | Built via `@astrojs/sitemap`         | Must be installed and configured         |
| SEO Meta Tags       | `src/components/atoms/SeoHead.astro` | 12 required tags (see below)             |
| `astro.config.mjs`  | Project root                         | Must have `site:` URL configured         |

---

## 2. `public/robots.txt` Template

```txt
User-agent: *
Allow: /

Disallow: /admin/

Sitemap: https://TU-DOMINIO.COM/sitemap-index.xml
```

---

## 3. `public/humans.txt` Template (A2LT Standard Credit)

```txt
/* TEAM */
Developer & Architect: A2LT Soluciones
Website: https://a2lt.netlify.app
Contact: contacto@a2lt.com
Location: Venezuela / Remote

/* TECHNOLOGY */
Framework: Astro 5 (SSG/SSR)
Styling: Tailwind CSS v4 (Oxide Engine, CSS-First @theme)
CMS: Decap CMS (Git-based)
Hosting: Netlify (CI/CD + Identity)
Language: TypeScript

/* SITE */
Last update: YYYY/MM/DD
Standards: HTML5, CSS3, WAI-ARIA
```

---

## 4. `netlify.toml` Security Headers Template

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "DENY"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "camera=(), microphone=(), geolocation=()"
    Strict-Transport-Security = "max-age=31536000; includeSubDomains; preload"
    Content-Security-Policy = "default-src 'self'; script-src 'self' 'unsafe-inline'; style-src 'self' 'unsafe-inline' https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com; img-src 'self' data: blob:; connect-src 'self';"
```

---

## 5. Required SEO Meta Tags in `SeoHead.astro`

Every page must emit ALL of the following:

1. `<title>` — Dynamic per-page title
2. `<meta name="description">` — 150-160 char description
3. `<meta name="robots" content="index, follow">`
4. `<meta name="author" content="A2LT Soluciones">` — Always A2LT as author
5. `<link rel="canonical">` — Absolute URL of the current page
6. `<meta property="og:title">`
7. `<meta property="og:description">`
8. `<meta property="og:image">` — Social share image
9. `<meta property="og:url">`
10. `<meta property="og:locale" content="es_VE">` (or appropriate locale)
11. `<meta property="og:site_name">` — Brand name
12. `<meta name="twitter:card" content="summary_large_image">`

---

## 6. `astro.config.mjs` Required Fields

```js
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://TU-DOMINIO.COM", // REQUIRED for sitemap + canonical
  integrations: [sitemap()],
});
```

---

## 7. Astro 5 Natively Directives (CRITICAL)

To prevent runtime or build errors on Windows/Linux environments, force these standards:

1. **Content Collections (Windows Safe):** ALWAYS use the new Astro 5 Content Layer API with `loader: glob()`. NEVER use `type: 'content'` as it causes silent `InvalidContentEntryDataError` validation failures in Windows environments due to path separators.
2. **JSX Parser Fragility in `.astro` Files:** Avoid using generics like `CollectionEntry<'services'>` directly inside `.astro` template expressions (like `.sort()` callbacks or inline maps). The Astro parser confuses `< >` with JSX Fragments. Either cast to `any` (e.g., `(a: any, b: any)`) or define the typed function purely in the Frontmatter script boundary `---` before passing it to the HTML template.
3. **Decap CMS Dev Mode:** Ensure `local_backend: true` is set in `public/admin/config.yml` during development.
4. **Type Checking:** `@astrojs/check` is mandatory in the pipeline to prevent build CI failures.

## 8. Component Architecture Rules (CRITICAL)

> **POST-MORTEM ORIGIN:** These rules exist because the VCard testimonials section required 5 iterations to stabilize due to forcing a single component to serve radically different Mobile and Desktop UIs.

### 8.1 Mobile/Desktop Separation Mandate

When Mobile and Desktop require **fundamentally different interaction patterns** (e.g., single-card swipe vs infinite marquee, column stack vs panoramic grid), you MUST create separate components and use explicit visibility classes:

```astro
<!-- Mobile: completely independent component -->
<MobileCarousel class="md:hidden" testimonials={testimonials} />

<!-- Desktop: the CMS-selected variant -->
<DesktopVariant class="hidden md:block" testimonials={testimonials} />
```

This separation is **robust and regression-proof**: no future change to desktop components can break the mobile experience. Do NOT attempt to make a single component adapt to fundamentally different behaviors via CSS alone.

### 8.2 `aspect-ratio` Restriction

**PROHIBITION:** Never use `aspect-ratio` combined with `overflow: hidden` on cards that contain **variable-length text content** (quotes, descriptions, bios). The fixed aspect ratio WILL clip content when text exceeds the expected length.

- ✅ Use `aspect-ratio` ONLY on containers for images, videos, or fixed media.
- ✅ For text cards, use `min-height` per breakpoint to allow organic vertical growth:
  ```css
  .testimonial-card {
    min-height: 320px;
  }
  @media (min-width: 768px) {
    .testimonial-card {
      min-height: 280px;
    }
  }
  ```

### 8.3 CSS Extraction for Complex Animations

**MANDATE:** Keyframes, infinite scroll animations, complex hover states, and multi-step transitions MUST be extracted to dedicated CSS files at `src/styles/{component-name}.css`. They MUST NOT be embedded in `<style>` blocks inside `.astro` components.

- Reason: Large `<style>` blocks inside `.astro` files create readability bottlenecks for both humans and AI agents in future sessions.
- Pattern: `src/styles/clients-carousel.css`, `src/styles/styled-carousel.css`.
- Import the CSS file in the component's Frontmatter: `import '../styles/clients-carousel.css';`
