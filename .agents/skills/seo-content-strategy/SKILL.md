---
name: seo-content-strategy
version: 1.0.0
type: backend
subtype: skill
tier: all
description: |
  Estrategia de contenidos SEO para AIRON‑Cast. Planifica clusters,
  redacta contenido semántico, analiza densidades de keywords y recomienda
  actualizaciones de contenido antiguo. Activar cuando el `writer` necesite
  planificar, redactar o refrescar contenido web.
  Trigger phrases: "content strategy", "topic cluster", "keyword density",
  "content refresh", "planificar contenido", "estrategia SEO".
  No activar para meta tags o schema (usar `seo-onpage-architecture`).
triggers:
  primary: ["content strategy", "topic cluster", "keyword density"]
  secondary: ["planificar contenido", "content refresh", "LSI keywords"]
  context: ["SEO content", "copywriting", "content marketing"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - writer
last_used: 2026-06-05
scope: restricted
---

# SEO Content Strategy — AIRON‑Cast

This skill drives the entire content lifecycle: from strategic planning and
topical clustering to writing, keyword optimization, and continuous refreshing.

---

## 1. Content Planning & Topic Clustering

Before writing, establish topical authority through structured planning.

- **Topic Cluster Mapping:** Define one "Pillar Page" supported by specific
  "Cluster Pages" (subtopics, FAQs, versus content).
- **Search Intent Alignment:** Map every planned URL to one of four intents:
  Informational, Navigational, Commercial, Transactional.
- **Content Calendar:** Deliver a 30-60 day prioritization blueprint grouping
  formats, target word counts, and internal linking targets.

### Content Outline Structure

```markdown
Title: [Main Topic]
Intent: [Commercial/Informational]
Word Count: [Target]

I. Introduction (Hook & Value Prop)
II. Main Section 1 (H2 + Primary KW)
A. Subtopic (H3)
III. Main Section 2...
```

---

## 2. SEO Content Writing Framework

- **Introduction (50-100 words):** Hook the reader instantly. Place the primary
  keyword naturally in the first paragraph.
- **Body Content:** Short paragraphs (2-3 sentences), bullet points for
  scannability, semantic headings (H2/H3). E-E-A-T signals must be interwoven
  (first-hand experience, data citations).
- **Quality Standard:** Write for humans; structure for search engines.

---

## 3. Keyword Strategy & Semantic Optimization (LSI)

- **Density Guidelines:** Primary keyword target is 0.5% - 1.5%. Keyword
  stuffing restricts rankings.
- **Entity Analysis:** Extract primary entities (nouns/concepts associated with
  the topic) and inject LSI keywords.

**Delivery Format:**

```markdown
Primary: [keyword] (0.8% density, 12 uses)
LSI Keywords: [20-30 semantic variations]
Entities: [Related concepts to build authority]
```

---

## 4. Content Refreshing (Preventing Decay)

- **High Priority:** Pages losing rankings, stats older than 2 years.
- **Medium Priority:** Stagnant rankings for 6+ months, broken outbound links.
- **Refresh Actions:** Update numerical data and statistics, inject new expert
  quotes, add recently relevant FAQs, update schema `dateModified`.

---

## 5. Execution Rule

Never just generate text. Provide the strategic overview (Intent, Keyword
Density, Target Audience) alongside the actual content. Emphasize value-driven
depth over generic fluff.