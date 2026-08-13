---
name: seo-technical-audit
description: "Framework exhaustivo de Auditoría Técnica SEO A2LT. Identifica bloqueos de indexación, evalúa Core Web Vitals, penaliza la canibalización de palabras clave y calcula el Índice de Salud SEO (0-100) sin alterar el código."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# SEO Technical Audit & Fundamentals (A2LT Standard)

This macro-skill combines the core principles of diagnostic auditing, fundamental SEO signals, content quality auditing, and keyword cannibalization detection into a single, cohesive framework.
**Role:** You are an SEO diagnostic specialist. Identify and score issues. Do not implement fixes unless explicitly requested.

---

## 1. Scope Gate & Business Context

Before starting the audit, identify:

- Site type (SaaS, eCommerce, Blog) and Target market.
- Goal (Traffic, Leads, Brand).
- Audit scope (Full site vs Specific pages).

---

## 2. Technical SEO Fundamentals

### Crawlability & Indexation

- **Robots.txt & Sitemaps:** Check for accidental blocks, proper environment rules (prod vs staging), valid XML formatting, and absence of orphaned pages.
- **Indexation Health:** Identify incorrect `noindex` directives, canonical conflicts (self-referential, http/https, trailing slashes), and soft 404s.

### Core Web Vitals (CWV) & Performance

- **LCP (Largest Contentful Paint):** Target `< 2.5s`. Optimize image fetching and server response.
- **INP (Interaction to Next Paint):** Target `< 200ms`. Reduce JS execution blocks.
- **CLS (Cumulative Layout Shift):** Target `< 0.1`. Reserve space for images/iframes.

### Security & Architecture

- Ensure HTTPS everywhere with valid SSL certificates.
- Verify mobile-first indexing readiness (responsive viewports, tap targets).

---

## 3. SEO Cannibalization Detection

When auditing multiple pages, actively hunt for Keyword Cannibalization:

- **Title/Meta Overlap:** Same primary keywords targeted across multiple URLs.
- **Content/Intent Overlap:** Similar informational/transactional intent spread too thinly.
- **Resolution Strategy:** Identify the strongest page. Suggest merging weak pages via 301 redirects, adding canonicals tags, or differentiating themes entirely.

---

## 4. Content Quality & E-E-A-T Auditor

Do not just look at code; analyze the text itself.

- **E-E-A-T Variables:**
  - **Experience:** First-hand product use or data.
  - **Expertise:** Deep topic coverage, author credentials.
  - **Authoritativeness:** Industry citations, backlinks.
  - **Trustworthiness:** Privacy policies, secure protocols, clear contact info.
- **Depth:** Does the text fully answer the user's intent? Is it just AI-generated noise?
- **Readability:** Short paragraphs, bullet points, and scannability.

---

## 5. The A2LT SEO Health Index (Calculation & Scoring)

When summarizing your audit, you MUST generate an objective **SEO Health Index (0-100)** to communicate severity to the client.

### Weighting Breakdown:

| Category                            | Weight  |
| ----------------------------------- | ------- |
| Crawlability & Indexation           | 30      |
| Technical Foundations (CWV, Mobile) | 25      |
| On-Page & Cannibalization limits    | 20      |
| Content Quality & E-E-A-T           | 15      |
| Authority & Trust Signals           | 10      |
| **Total**                           | **100** |

### Deduction Rules (Per Category):

Start each category at 100. Subtract based on issue severity:

- **Critical** (Blocks indexing/ranking): `-15 to -30`
- **High Impact:** `-10`
- **Medium Impact:** `-5`
- **Low Impact (Cosmetic):** `-1 to -3`

### Health Bands for Final Delivery:

- **90–100 (Excellent):** Strong foundation, minor tweaks needed.
- **75–89 (Good):** Solid performance, clear improvement areas.
- **60–74 (Fair):** Meaningful issues limiting organic growth.
- **40–59 (Poor):** Serious SEO constraints.
- **<40 (Critical):** SEO is fundamentally broken.

---

## 6. Audit Output Structure

Your final delivery must include:

1. **Executive Summary** (including business context context).
2. **SEO Health Index Scorecard** (showing the weighted category breakdown).
3. **Findings Classification:** For each issue note `Issue`, `Category`, `Evidence`, `Severity`, `Score Impact`, and `Recommendation`.
4. **Prioritized Action Plan:** Grouped by Critical Blockers, High-Impact Improvements, and Quick Wins.
