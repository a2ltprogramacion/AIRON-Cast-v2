---
name: geo-optimization
description: "Generative Engine Optimization (GEO) para motores de búsqueda RAG (Perplexity, Claude, ChatGPT, Gemini). Diseña contenido estático para garantizar citaciones como fuente de autoridad mediante Entidades, Datos Originales y Citas Expertas."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# GEO (Generative Engine Optimization) Fundamentals

This skill is distinct from traditional SEO. It defines how content must be architected so that AI Agents (acting as Search Engines) parse, retrieve, and CITE the content as a primary source.

---

## 1. RAG Retrieval Priorities

AI Engines don't rank based on backlinks the way Google does. They retrieve based on Semantic Density and Extraction Viability.

**The Golden Factors:**

1. **Semantic Relevance (~40%):** Does this text directly answer the user's vector query without fluff?
2. **Authority & Entity Signals (~15%):** Is the author explicitly named with credentials? Does the domain exist in the Knowledge Graph?
3. **Extraction Formatting:** If an AI cannot easily parse the data, it will not cite it.

---

## 2. The AI-Citation Engineering Checklist

When generating or restructuring content for GEO, enforce these components:

- **Original Data / Statistics:** AI engines actively favor content with hard, unique numbers.
- **Expert Quotes:** Embed `<blockquote>` or explicit quote blocks attributing value to a named expert (Authority Transfer).
- **Direct Definitions:** Use clear "X is Y" sentence structures immediately beneath H2/H3 tags.
- **Table Comparisons:** Instead of prose, use Markdown/HTML tables for comparing items. AI engines absorb structured tables at a significantly higher rate.
- **'Last Updated' Context:** Enforce freshness timestamps (e.g., `<meta property="article:modified_time">`), as models penalize stale retrieval data.

---

## 3. AI Crawler Access Control

Depending on the client's business model, define access rules in `robots.txt`:

- **GPTBot / ChatGPT-User:** OpenAI's crawlers.
- **ClaudeBot:** Anthropic's ingestion.
- **PerplexityBot:** The primary RAG citation engine.
- **Strategy:** If the goal is **Lead Gen/Traffic**, allow `PerplexityBot` and block background training bots if IP protection is needed.

---

## 4. Anti-Patterns in GEO

- **❌ Vague Attributions:** "Some researchers say..." -> Will never be cited.
- **❌ Thin Fluff Intros:** 500 words of background before the main point -> AI chunkers will skip or truncate the embedding.
- **✅ Dense Value:** TL;DR lists at the absolute top of the page.
