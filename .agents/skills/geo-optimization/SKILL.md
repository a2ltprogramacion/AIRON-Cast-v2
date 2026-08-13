---
name: geo-optimization
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Generative Engine Optimization (GEO) para motores de búsqueda RAG
  (Perplexity, Claude, ChatGPT, Gemini). Diseña contenido estático para
  garantizar citaciones como fuente de autoridad mediante Entidades,
  Datos Originales y Citas Expertas. Activar cuando `writer` necesite
  optimizar contenido para indexación en motores de IA generativa.
  Trigger phrases: "GEO", "Generative Engine Optimization", "optimizar
  para IA", "AI search", "RAG indexing", "citación IA".
  No activar para SEO tradicional (usar `seo-content-strategy` o
  `seo-onpage-architecture`).
triggers:
  primary: ["GEO", "Generative Engine Optimization", "optimizar para IA"]
  secondary: ["AI search", "RAG indexing", "citación IA"]
  context: ["AI content", "generative search", "LLM indexing"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - writer
last_used: 2026-06-05
scope: restricted
---

# GEO (Generative Engine Optimization) — AIRON‑Cast

This skill is distinct from traditional SEO. It defines how content must be
architected so that AI agents acting as search engines parse, retrieve, and
CITE the content as a primary source.

---

## 1. RAG Retrieval Priorities

AI engines retrieve based on Semantic Density and Extraction Viability:

1. **Semantic Relevance (~40%):** Does the text directly answer the user's
   vector query without fluff?
2. **Authority & Entity Signals (~15%):** Is the author explicitly named with
   credentials? Does the domain exist in the Knowledge Graph?
3. **Extraction Formatting:** If an AI cannot easily parse the data, it will
   not cite it.

---

## 2. AI-Citation Engineering Checklist

When generating or restructuring content for GEO, enforce these components:

- **Original Data / Statistics:** AI engines actively favor content with hard,
  unique numbers.
- **Expert Quotes:** Embed explicit quote blocks attributing value to a named
  expert (Authority Transfer).
- **Direct Definitions:** Use clear "X is Y" sentence structures immediately
  beneath H2/H3 tags.
- **Table Comparisons:** Use Markdown/HTML tables for comparing items. AI
  engines absorb structured tables at a significantly higher rate.
- **'Last Updated' Context:** Enforce freshness timestamps (e.g.,
  `<meta property="article:modified_time">`), as models penalize stale
  retrieval data.

---

## 3. AI Crawler Access Control

Define access rules in `robots.txt` based on the client's business model:

- **GPTBot / ChatGPT-User:** OpenAI's crawlers.
- **ClaudeBot:** Anthropic's ingestion.
- **PerplexityBot:** The primary RAG citation engine.

**Strategy:** If the goal is Lead Gen/Traffic, allow PerplexityBot and block
background training bots if IP protection is needed.

---

## 4. Anti-Patterns in GEO

- ❌ **Vague Attributions:** "Some researchers say..." — Will never be cited.
- ❌ **Thin Fluff Intros:** 500 words of background before the main point —
  AI chunkers will skip or truncate the embedding.
- ✅ **Dense Value:** TL;DR lists at the absolute top of the page.