---
name: seo-onpage-architecture
version: 1.0.0
type: backend
subtype: skill
tier: all
description: |
  Arquitectura On-Page SEO para AIRON‑Cast. Optimiza meta tags, jerarquías
  H1-H6, schema markup, featured snippets y señales de autoridad E-E-A-T.
  Activar cuando el `writer` necesite estructurar páginas individuales para
  motores de búsqueda.
  Trigger phrases: "meta tags", "schema markup", "featured snippet",
  "on-page SEO", "title tag", "H1-H6", "structured data".
  No activar para estrategia de contenido general (usar `seo-content-strategy`).
triggers:
  primary: ["meta tags", "schema markup", "on-page SEO", "featured snippet"]
  secondary: ["title tag", "H1-H6", "structured data", "E-E-A-T"]
  context: ["SEO on-page", "page optimization", "SERP"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - writer
last_used: 2026-06-05
scope: restricted
---

# SEO On-Page Architecture — AIRON‑Cast

This skill dictates the structural scaffolding of a webpage. It covers meta
tag psychology, heading hierarchies, schema markup, featured snippet
formatting, and on-page authority signaling.

---

## 1. Meta Tag Optimization (CTR Psychology)

Optimize for Click-Through Rate, not just keywords.

- **URLs:** Under 60 chars, hyphens only, primary keyword close to root.
  No stop words.
- **Title Tags:** 50-60 chars. Primary keyword in the first 30 characters.
  Inject emotional triggers, power words, or freshness indicators.
- **Meta Descriptions:** 150-160 chars. Include a clear CTA, action verbs,
  and special characters to stand out in SERPs.

---

## 2. Structure Architecture (H1-H6 Hierarchy)

- **Rule of One:** Exactly one `<h1>` per page capturing the broad topic and
  primary keyword.
- **Siloing:** `<h2>` for major sections (secondary keywords), `<h3>` for
  deep-dive subsections.
- **Jump Links:** Use a Table of Contents for scannability.

---

## 3. Schema Markup

Mandate structured data contextually:

- `Article` or `BlogPosting` for posts.
- `FAQPage` for Q&A sections.
- `Organization` / `LocalBusiness` for brand homepages.
- `BreadcrumbList` for category hierarchies.

---

## 4. Featured Snippet Formatting (Position Zero)

### Paragraph Snippets (40-60 words)

The direct answer MUST be in the very first sentence immediately following an
`<h2/h3>` question block. No fluff.

### List Snippets

Use strictly formatted ordered/unordered HTML lists (5-8 items). Add a clear
summary sentence before the list begins.

### Table Snippets

Use standard HTML `<table>` structures to compare specs, prices, or datasets.

**Formatting Example:**

```markdown
## [Exact Question from 'People Also Ask']

[40-60 word definitive, punchy answer starting with the core fact.]

**Supporting Details:**
- Tangible point 1
- Tangible point 2
```

---

## 5. On-Page Authority Builder (E-E-A-T Injection)

- **Author Biographies:** Bylines present, linking to comprehensive author pages
  with credentials, social proof, and professional history.
- **Trust Elements:** Clear editorial guidelines, "last updated" stamps,
  prominent links to Privacy Policies and Contact details.
- **Citations:** Outbound links to highly authoritative domains (`.edu`, `.gov`,
  major industry journals).

---

## 6. Platform Integration

- **Astro:** Use `SEO` components (like `astro-seo`) passing precise
  title/description props and injecting JSON-LD schema into `<head>`.
- **Django:** Template blocks (`{% block meta_description %}`) for
  server-rendered HTML.