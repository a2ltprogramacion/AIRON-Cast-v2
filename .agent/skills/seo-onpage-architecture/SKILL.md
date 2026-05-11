---
name: seo-onpage-architecture
description: "Macro-Skill de Arquitectura On-Page y Fragmentos A2LT. Optimiza Metadatos impulsados por CTR, diseña jerarquías H1-H6, genera Schemas y formatea textos para capturar Featured Snippets."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# SEO On-Page Architecture & Authority (A2LT Standard)

This macro-skill dictates the structural scaffolding of a webpage. It covers meta tag psychology, heading hierarchies, schema markup, featured snippet formatting, and on-page authority signaling.

---

## 1. Meta Tag Optimization (CTR Psychology)

Do not just include keywords; optimize for Click-Through Rate (CTR).

- **URLs:** `< 60 chars`, hyphens only, primary keyword as close to the root as possible. No stop words.
- **Title Tags:** `50-60 chars`. Primary keyword in the first 30 characters. Inject emotional triggers, power words, or freshness indicators (e.g., "Updated 2025").
- **Meta Descriptions:** `150-160 chars`. Include a clear CTA, action verbs, and special characters (like ✓ / ★) to stand out in the SERPs.

---

## 2. Structure Architecture (H1-H6 Hierarchy)

The HTML structure must map perfectly to the topic's logical hierarchy.

- **Rule of One:** Absolutely only one `<h1>` per page capturing the broad topic/primary keyword.
- **Siloing:** `<h2>` for major sections (Secondary keywords), `<h3>` for deep-dive subsections. Use Jump Links (Table of Contents) to facilitate scannability.
- **Schema Suggestions:** Mandate the use of structured data contextually:
  - `Article` or `BlogPosting` for posts.
  - `FAQPage` for Q&A sections.
  - `Organization` / `LocalBusiness` for brand homepages.
  - `BreadcrumbList` for category hierarchies.

---

## 3. SEO Snippet Hunting (Position Zero)

Actively format on-page text to mathematically increase the odds of capturing Google's "Featured Snippets".

- **Paragraph Snippets (40-60 words):** The direct answer MUST be in the very first sentence immediately following an `<h2/h3>` question block. No fluff.
- **List Snippets:** Use strictly formatted ordered/unordered HTML lists (5-8 items). Add a clear summary sentence right before the list begins.
- **Table Snippets:** Use standard HTML `<table>` structures (without complex CSS disruptions) to compare specs, prices, or datasets.

### Snippet Formatting Example:

```markdown
## [Exact Question Extracted from 'People Also Ask']

[40-60 word definitive, punchy answer starting with the core fact. Do not start with "Well, it depends..."]

**Supporting Details:**

- Tangible point 1
- Tangible point 2
```

---

## 4. On-Page Authority Builder (E-E-A-T Injection)

Analyze templates to ensure trust signals are hard-coded into the UI architecture.

- **Author Biographies:** Ensure bylines are present, linking to comprehensive author pages featuring credentials, social proof, and professional history.
- **Trust Elements:**
  - Clear editorial guidelines and "last updated" stamps.
  - Prominent links to Privacy Policies and Contact details.
  - Hard data citations heavily emphasizing outbound links to highly authoritative domains (`.edu`, `.gov`, or massive industry journals).

---

## 5. Platform Integration Context

- For **Astro**, this skill dictates the usage of `SEO` components (like `astro-seo`) passing precise title/description props and injecting JSON-LD schema into the `<head>`.
- For **Django**, this influences template blocks (`{% block meta_description %}`) and the structural flow of server-rendered HTML.
