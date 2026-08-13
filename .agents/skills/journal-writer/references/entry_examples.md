# Entry Examples — AIRON‑Cast Journal

## Example: task entry

```json
{
  "agent_name": "frontend_worker",
  "task_description": "Generated Hero section component for landing-01",
  "skills_used": ["astro-landing-kit", "tailwind-architecture"],
  "duration_minutes": 25,
  "output_artifacts": [
    "workspace/landing-01/src/components/Hero.astro",
    "workspace/landing-01/src/styles/hero.css"
  ],
  "notes": "Component matches wireframe spec from ux-ui_specialist."
}
```

## Example: problem entry

```json
{
  "title": "SQLite database locked during concurrent writes",
  "context": "Two agents attempted to log execution simultaneously via memory_manager",
  "root_cause": "SQLite connection not using WAL mode; default journal_mode=delete caused lock contention",
  "solution": "Enabled PRAGMA journal_mode=WAL in memory_manager.py connection setup",
  "mitigation": "All database connections now use WAL mode by default; added connection timeout of 5s",
  "affected_components": ["memory_manager.py"],
  "severity": "medium",
  "recurrence_risk": "low"
}
```

## Example: adr entry

```json
{
  "title": "Use SQLite FTS5 for journal search instead of ChromaDB",
  "context": "Needed full‑text search across journal entries without external vector database dependency",
  "decision": "SQLite FTS5 with custom tokenizer for Spanish/English mixed content",
  "alternatives_considered": [
    "ChromaDB (requires API key or local server, not $0 budget)",
    "Elasticsearch (overkill, adds infrastructure)",
    "grep‑based search (too slow for 100+ entries)"
  ],
  "reasoning": "FTS5 ships with Python's sqlite3 module, zero extra dependencies. Works within $0 budget. Sufficient for journal entry volume (<10k entries).",
  "consequences": "Search quality is lexical, not semantic. For complex queries, fall back to manual review. Acceptable trade‑off for zero cost.",
  "status": "accepted",
  "supersedes": ""
}
```

## Example: pattern entry

```json
{
  "title": "Skills with file output must auto‑create target directories",
  "description": "Skills that generate files into workspace/ should call os.makedirs(exist_ok=True) before any write operation, rather than assuming the directory exists.",
  "evidence": [
    "20260603-150845_problem_sqlite-lock-contention.md",
    "20260602-093000_problem_missing-workspace-dir.md"
  ],
  "recommendation": "Add os.makedirs() guard at the start of every skill script that writes to workspace/<project>/. Include in skill‑creator‑pro template.",
  "applies_to": "All skills with file output (utility, integration types)",
  "first_seen": "2026-06-02"
}
```

## Example: field entry

```json
{
  "skill_or_agent": "astro-landing-kit",
  "project_context": "E‑commerce landing page — fashion retail",
  "usage_description": "Used to build product showcase sections with filtering",
  "outcome": "Components rendered correctly in production. Client satisfied with performance.",
  "friction_points": "Client requested dark mode toggle; kit only provides light theme by default",
  "suggested_improvement": "Add dark mode variant CSS and a toggle component to astro-landing-kit",
  "operator_rating": 4
}
```