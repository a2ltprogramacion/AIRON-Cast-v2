---
name: astro-landing-kit
version: 1.0.0
type: frontend
subtype: skill
tier: all
description: |
  Astro project standards and landing page component kit for AIRON‑Cast.
  Provides ready-to-use Astro components (Hero, Features, CTA, FAQ, Footer),
  mandatory baseline files (robots.txt, humans.txt, netlify.toml, SEO),
  and post-mortem architectural rules for robust Astro 5 projects.
  Trigger phrases: "landing kit", "componente Astro", "plantilla landing",
  "robots.txt", "netlify.toml", "SEO head", "hero component".
  Do NOT activate for backend logic or non-Astro frameworks.
triggers:
  primary: ["landing kit", "componente Astro", "plantilla landing"]
  secondary: ["robots.txt", "netlify.toml", "SEO head", "hero component"]
  context: ["Astro project", "landing page", "frontend baseline"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - requirements_architect
  - frontend_worker
last_used: 2026-06-05
scope: restricted
---

# Astro Landing Kit — AIRON‑Cast

This skill defines the non-negotiable baseline for EVERY Astro project
and provides a library of landing page components. Born from post-mortems
where security headers, sitemaps, and component architecture failures
required costly retroactive fixes.

---

## PART 1: Project Baseline (Mandatory)

Before declaring any Astro project ready for first deploy, verify ALL of
the following exist:

| File | Location | Status Check |
|------|----------|--------------|
| `robots.txt` | `public/robots.txt` | Must exist and block `/admin/` |
| `humans.txt` | `public/humans.txt` | Must credit A2LT Soluciones as developer |
| `netlify.toml` | Project root | Must include security headers |
| `sitemap-index.xml` | Built via `@astrojs/sitemap` | Must be installed and configured |
| SEO Meta Tags | `src/components/atoms/SeoHead.astro` | 12 required tags (see below) |
| `astro.config.mjs` | Project root | Must have `site:` URL configured |

### 1.1 `public/robots.txt` Template

```txt
User-agent: *
Allow: /

Disallow: /admin/

Sitemap: https://TU-DOMINIO.COM/sitemap-index.xml
```

### 1.2 `public/humans.txt` Template (A2LT Standard Credit)

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

### 1.3 `netlify.toml` Security Headers Template

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

La auditoría de `astro-landing-kit` resultó **VÁLIDA**. Dos advertencias menores que no bloquean, pero que debemos atender:

1. **Placeholders funcionales** (`https://TU-DOMINIO.COM`, `YYYY/MM/DD`): Son inevitables en plantillas, pero agregaré una nota explícita en la sección de implementación para que el agente los reemplace antes de producción.
2. **Falta plantilla de `SeoHead.astro`**: La lista de 12 meta-tags está, pero no el código. La incluiré ahora como componente completo.

---

## Corrección rápida en `astro-landing-kit`

Agrego la plantilla `SeoHead.astro` faltante y una nota sobre placeholders. Solo tienes que reemplazar la sección 1.4 con esto:

### 1.4 Required SEO Meta Tags — `SeoHead.astro`

Every page must include this component in its `<head>`. It emits all 12
required tags using props for dynamic content.

```astro
---
export interface Props {
  title: string
  description: string
  canonicalURL: string
  ogImage: string
  locale?: string
  siteName: string
}

const {
  title,
  description,
  canonicalURL,
  ogImage,
  locale = 'es_VE',
  siteName,
} = Astro.props
---

<title>{title}</title>
<meta name="description" content={description} />
<meta name="robots" content="index, follow" />
<meta name="author" content="A2LT Soluciones" />
<link rel="canonical" href={canonicalURL} />

<meta property="og:title" content={title} />
<meta property="og:description" content={description} />
<meta property="og:image" content={ogImage} />
<meta property="og:url" content={canonicalURL} />
<meta property="og:locale" content={locale} />
<meta property="og:site_name" content={siteName} />
<meta name="twitter:card" content="summary_large_image" />
```

> ⚠️ **Placeholder Replacement Mandate:** Before deploying to production,
> the agent MUST replace `https://TU-DOMINIO.COM` in `robots.txt` and
> `astro.config.mjs`, and `YYYY/MM/DD` in `humans.txt`, with the actual
> project domain and current date. These placeholders are intentional
> templates, not errors.


### 1.5 `astro.config.mjs` Required Fields

```js
import { defineConfig } from "astro/config";
import sitemap from "@astrojs/sitemap";

export default defineConfig({
  site: "https://TU-DOMINIO.COM",
  integrations: [sitemap()],
});
```

---

## PART 2: Astro 5 Critical Directives

To prevent runtime or build errors on Windows/Linux environments:

1. **Content Collections (Windows Safe):** ALWAYS use the new Astro 5 Content
   Layer API with `loader: glob()`. NEVER use `type: 'content'` — it causes
   silent `InvalidContentEntryDataError` validation failures on Windows due
   to path separators.
2. **JSX Parser Fragility in `.astro` Files:** Avoid using generics like
   `CollectionEntry<'services'>` directly inside `.astro` template expressions
   (like `.sort()` callbacks). The Astro parser confuses `< >` with JSX
   Fragments. Either cast to `any` or define the typed function purely in
   the Frontmatter script boundary `---` before passing it to the HTML template.
3. **Decap CMS Dev Mode:** Ensure `local_backend: true` is set in
   `public/admin/config.yml` during development.
4. **Type Checking:** `@astrojs/check` is mandatory in the pipeline to
   prevent build CI failures.

---

## PART 3: Component Architecture Rules (CRITICAL)

> **POST-MORTEM ORIGIN:** These rules exist because the VCard testimonials
> section required 5 iterations to stabilize due to forcing a single component
> to serve radically different Mobile and Desktop UIs.

### 3.1 Mobile/Desktop Separation Mandate

When Mobile and Desktop require **fundamentally different interaction patterns**
(e.g., single-card swipe vs infinite marquee, column stack vs panoramic grid),
you MUST create separate components and use explicit visibility classes:

```astro
<!-- Mobile: completely independent component -->
<MobileCarousel class="md:hidden" testimonials={testimonials} />

<!-- Desktop: the selected variant -->
<DesktopVariant class="hidden md:block" testimonials={testimonials} />
```

This separation is **robust and regression-proof**: no future change to
desktop components can break the mobile experience. Do NOT attempt to make
a single component adapt to fundamentally different behaviors via CSS alone.

### 3.2 `aspect-ratio` Restriction

**PROHIBITION:** Never use `aspect-ratio` combined with `overflow: hidden`
on cards that contain **variable-length text content** (quotes, descriptions,
bios). The fixed aspect ratio WILL clip content when text exceeds the
expected length.

- ✅ Use `aspect-ratio` ONLY on containers for images, videos, or fixed media.
- ✅ For text cards, use `min-height` per breakpoint to allow organic
  vertical growth:
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

### 3.3 CSS Extraction for Complex Animations

**MANDATE:** Keyframes, infinite scroll animations, complex hover states,
and multi-step transitions MUST be extracted to dedicated CSS files at
`src/styles/{component-name}.css`. They MUST NOT be embedded in `<style>`
blocks inside `.astro` components.

- Reason: Large `<style>` blocks create readability bottlenecks for both
  humans and AI agents in future sessions.
- Pattern: `src/styles/clients-carousel.css`, `src/styles/styled-carousel.css`.
- Import the CSS file in the component's Frontmatter:
  `import '../styles/clients-carousel.css';`

---

## PART 4: Landing Page Components

### 4.1 Available Components

| Component | File | Props |
|-----------|------|-------|
| Hero | `Hero.astro` | `title`, `subtitle`, `ctaText`, `ctaLink`, `secondaryCtaText?`, `secondaryCtaLink?`, `badge?`, `backgroundImage?` |
| Features Grid | `Features.astro` | `features: Array<{icon: string, title: string, description: string}>` |
| CTA Section | `CTA.astro` | `title`, `description`, `buttonText`, `buttonLink` |
| FAQ Accordion | `FAQ.astro` | `questions: Array<{question: string, answer: string}>` |
| Footer | `Footer.astro` | `companyName`, `links: Array<{label: string, href: string}>`, `socialLinks?` |

### 4.2 Hero (`Hero.astro`)

```astro
---
export interface Props {
  title: string
  subtitle: string
  ctaText: string
  ctaLink: string
  secondaryCtaText?: string
  secondaryCtaLink?: string
  badge?: string
  backgroundImage?: string
}

const {
  title, subtitle, ctaText, ctaLink,
  secondaryCtaText, secondaryCtaLink, badge, backgroundImage,
} = Astro.props
---

<section
  class="min-h-[100svh] flex items-center justify-center px-6 relative overflow-hidden"
  style="background-color: var(--color-bg-surface);"
>
  {backgroundImage && (
    <div class="absolute inset-0 z-0">
      <img src={backgroundImage} class="w-full h-full object-cover" alt="" loading="eager" />
      <div class="absolute inset-0 bg-slate-950/70"></div>
    </div>
  )}
  <div class="relative z-10 max-w-4xl mx-auto text-center">
    {badge && (
      <span class="inline-block px-4 py-1 mb-6 text-sm font-semibold text-primary-500 bg-primary-500/10 rounded-full border border-primary-500/20">
        {badge}
      </span>
    )}
    <h1 class="text-4xl md:text-6xl font-heading font-bold text-text-main mb-6 leading-tight">
      {title}
    </h1>
    <p class="text-lg md:text-xl text-text-muted mb-10 max-w-2xl mx-auto">{subtitle}</p>
    <div class="flex flex-col sm:flex-row gap-4 justify-center">
      <a href={ctaLink} class="px-8 py-4 bg-primary-500 text-white font-semibold rounded-xl hover:bg-primary-600 hover:-translate-y-1 transition-all shadow-lg">
        {ctaText}
      </a>
      {secondaryCtaText && secondaryCtaLink && (
        <a href={secondaryCtaLink} class="px-8 py-4 border border-border text-text-main font-semibold rounded-xl hover:bg-surface-alt hover:-translate-y-1 transition-all" style="background-color: var(--color-bg-surface);">
          {secondaryCtaText}
        </a>
      )}
    </div>
  </div>
</section>
```

### 4.3 Features Grid (`Features.astro`)

```astro
---
export interface Feature {
  icon: string
  title: string
  description: string
}
export interface Props {
  features: Feature[]
  sectionTitle?: string
  sectionSubtitle?: string
}
const { features, sectionTitle, sectionSubtitle } = Astro.props
---

<section class="py-24 px-6" style="background-color: var(--color-bg-alt);">
  <div class="max-w-7xl mx-auto">
    {(sectionTitle || sectionSubtitle) && (
      <div class="text-center mb-16">
        {sectionTitle && <h2 class="text-3xl md:text-4xl font-heading font-bold text-text-main mb-4">{sectionTitle}</h2>}
        {sectionSubtitle && <p class="text-lg text-text-muted max-w-2xl mx-auto">{sectionSubtitle}</p>}
      </div>
    )}
    <div class="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
      {features.map((feature) => (
        <div class="p-8 rounded-2xl border border-border hover:shadow-lg transition-shadow" style="background-color: var(--color-bg-surface);">
          <div class="w-12 h-12 bg-primary-500/10 rounded-xl flex items-center justify-center mb-6">
            <span class="text-2xl" set:html={feature.icon} />
          </div>
          <h3 class="text-xl font-heading font-semibold text-text-main mb-3">{feature.title}</h3>
          <p class="text-text-muted leading-relaxed">{feature.description}</p>
        </div>
      ))}
    </div>
  </div>
</section>
```

### 4.4 CTA Section (`CTA.astro`)

```astro
---
export interface Props {
  title: string
  description: string
  buttonText: string
  buttonLink: string
}
const { title, description, buttonText, buttonLink } = Astro.props
---

<section class="py-24 px-6" style="background-color: var(--color-bg-surface);">
  <div class="max-w-3xl mx-auto text-center">
    <h2 class="text-3xl md:text-4xl font-heading font-bold text-text-main mb-6">{title}</h2>
    <p class="text-lg text-text-muted mb-10">{description}</p>
    <a href={buttonLink} class="inline-block px-10 py-5 bg-primary-500 text-white font-bold rounded-xl hover:bg-primary-600 hover:-translate-y-1 transition-all shadow-lg text-lg">
      {buttonText}
    </a>
  </div>
</section>
```

### 4.5 FAQ Accordion (`FAQ.astro`)

```astro
---
export interface QA { question: string; answer: string }
export interface Props { questions: QA[] }
const { questions } = Astro.props
---

<section class="py-24 px-6" style="background-color: var(--color-bg-alt);">
  <div class="max-w-3xl mx-auto">
    <h2 class="text-3xl md:text-4xl font-heading font-bold text-text-main text-center mb-16">
      Frequently Asked Questions
    </h2>
    <div class="space-y-4">
      {questions.map((qa) => (
        <details class="group border border-border rounded-2xl overflow-hidden" style="background-color: var(--color-bg-surface);">
          <summary class="flex items-center justify-between p-6 cursor-pointer font-semibold text-text-main">
            {qa.question}
            <span class="text-2xl transition-transform group-open:rotate-45">+</span>
          </summary>
          <div class="px-6 pb-6 text-text-muted leading-relaxed">{qa.answer}</div>
        </details>
      ))}
    </div>
  </div>
</section>
```

### 4.6 Footer (`Footer.astro`)

```astro
---
export interface NavLink { label: string; href: string }
export interface SocialLink { platform: string; url: string }
export interface Props {
  companyName: string
  links: NavLink[]
  socialLinks?: SocialLink[]
}
const { companyName, links, socialLinks = [] } = Astro.props
---

<footer class="border-t border-border py-16 px-6" style="background-color: var(--color-bg-alt);">
  <div class="max-w-7xl mx-auto">
    <div class="flex flex-col md:flex-row justify-between items-center gap-8">
      <p class="text-text-muted text-sm">&copy; {new Date().getFullYear()} {companyName}. All rights reserved.</p>
      <nav class="flex flex-wrap gap-6">
        {links.map((link) => (
          <a href={link.href} class="text-text-muted hover:text-primary-500 transition-colors text-sm">{link.label}</a>
        ))}
      </nav>
      {socialLinks.length > 0 && (
        <div class="flex gap-4">
          {socialLinks.map((social) => (
            <a href={social.url} target="_blank" rel="noopener noreferrer" class="w-10 h-10 rounded-full border border-border flex items-center justify-center text-text-muted hover:text-primary-500 hover:border-primary-500 transition-colors" style="background-color: var(--color-bg-surface);" aria-label={social.platform}>
              {social.platform}
            </a>
          ))}
        </div>
      )}
    </div>
  </div>
</section>
```

---

## 5. Implementation Rules

- **Design Tokens First:** All components use CSS custom properties.
- **Mobile-First:** Every component starts at 375px.
- **Props Typing:** Always use TypeScript interfaces. No `any` types.
- **Accessibility:** All images must have `alt` text. Icons must be SVG with `aria-label` when interactive.

---

## 🔗 AIRON‑Cast Integration

This skill is consumed by:
- `requirements_architect` — to estimate page structure and ensure baseline compliance.
- `frontend_worker` — to instantiate, customize, and assemble components.

Generated files go to:
- `workspace/<slug>/src/components/` (components)
- `workspace/<slug>/public/` (robots.txt, humans.txt)
- `workspace/<slug>/` (netlify.toml, astro.config.mjs)