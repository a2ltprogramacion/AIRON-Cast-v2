---
name: seo-technical-audit
version: 1.0.0
type: backend
subtype: skill
tier: all
description: |
  Auditoría técnica SEO exhaustiva para AIRON‑Cast. Identifica bloqueos de
  indexación, evalúa Core Web Vitals, detecta canibalización de keywords y
  calcula el Índice de Salud SEO (0-100). Activar cuando `writer` o el
  Operador necesiten diagnosticar la salud SEO de un sitio.
  Trigger phrases: "auditoría técnica SEO", "SEO health check", "Core Web
  Vitals", "cannibalization", "indexación", "SEO audit".
  No activar para optimización on-page (usar `seo-onpage-architecture`).
triggers:
  primary: ["auditoría técnica SEO", "SEO audit", "health check"]
  secondary: ["indexación", "Core Web Vitals", "cannibalization", "SEO score"]
  context: ["SEO diagnóstico", "site audit", "technical SEO"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - writer
last_used: 2026-06-05
scope: restricted
---

# SEO Technical Audit — AIRON‑Cast

Diagnose and score SEO health. Identify issues, do not implement fixes unless
explicitly requested.

---

## 1. Scope & Business Context

Before starting, identify:
- Site type (SaaS, eCommerce, Blog) and target market.
- Goal (Traffic, Leads, Brand).
- Audit scope (full site or specific pages).

---

## 2. Technical SEO Fundamentals

### Crawlability & Indexation
- **Robots.txt & Sitemaps:** Check for accidental blocks, valid XML format,
  orphaned pages.
- **Indexation Health:** Incorrect `noindex`, canonical conflicts, soft 404s.

### Core Web Vitals (CWV)
- **LCP (Largest Contentful Paint):** < 2.5s
- **INP (Interaction to Next Paint):** < 200ms
- **CLS (Cumulative Layout Shift):** < 0.1

### Security & Architecture
- HTTPS everywhere, valid SSL.
- Mobile-first readiness (responsive viewport, tap targets).

---

## 3. Keyword Cannibalization Detection

- **Title/Meta Overlap:** Same primary keyword across multiple URLs.
- **Content/Intent Overlap:** Thinly spread similar intent.
- **Resolution:** Merge via 301, add canonicals, or differentiate themes.

---

## 4. Content Quality & E-E-A-T Auditor

- **Experience:** First-hand product use or data.
- **Expertise:** Deep topic coverage, author credentials.
- **Authoritativeness:** Industry citations, backlinks.
- **Trustworthiness:** Privacy policies, secure protocols, clear contact info.
- **Depth:** Does the content fully answer user intent?
- **Readability:** Short paragraphs, bullets, scannability.

---

## 5. SEO Health Index (0-100)

### Category Weights

| Category                           | Weight |
|------------------------------------|--------|
| Crawlability & Indexation          | 30     |
| Technical Foundations (CWV, Mobile)| 25     |
| On-Page & Cannibalization          | 20     |
| Content Quality & E-E-A-T          | 15     |
| Authority & Trust Signals          | 10     |
| **Total**                          | **100** |

### Deduction Rules

Start each category at 100. Subtract per issue:
- Critical (blocks indexing/ranking): -15 to -30
- High: -10
- Medium: -5
- Low (cosmetic): -1 to -3

### Health Bands
- **90–100:** Excellent
- **75–89:** Good
- **60–74:** Fair
- **40–59:** Poor
- **<40:** Critical (SEO fundamentally broken)

---

## 6. Audit Output Structure

1. **Executive Summary** (including business context).
2. **SEO Health Index Scorecard** (weighted breakdown).
3. **Findings Classification:** For each: `Issue`, `Category`, `Evidence`,
   `Severity`, `Score Impact`, `Recommendation`.
4. **Prioritized Action Plan:** Grouped into Critical Blockers, High-Impact,
   Quick Wins.