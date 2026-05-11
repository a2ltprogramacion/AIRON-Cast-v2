# compatibility.md
# Agent: agent_architect
# Purpose: Known compatibility rules and anti-patterns
# Version: 1.0

---

## RULE
Verify against this file before finalizing any tech stack decision.
HARD conflicts must not proceed without explicit operator override.

---

## HARD CONFLICTS (never combine)

### H001 — Django + SQLite in production
```
Issue:      SQLite cannot handle concurrent writes at scale.
            La Forja uses SQLite internally — project DB must be PostgreSQL.
Resolution: Always use PostgreSQL 16+ for web_app and api projects.
```

### H002 — Astro SSR + Decap CMS
```
Issue:      Decap CMS requires static file serving.
            Incompatible with Astro SSR adapter modes.
Resolution: Use Astro SSG (static output) when Decap CMS is present.
```

### H003 — ChromaDB CUDA on GTX 1060 3GB for inference
```
Issue:      3GB VRAM insufficient for most inference workloads.
Resolution: sentence-transformers uses GPU for embeddings only (small model).
            LM Studio inference is CPU-only (offload=0).
```

### H004 — DRF SimpleJWT + Session Authentication simultaneously
```
Issue:      Conflicting backends cause unpredictable permission behavior.
Resolution: JWT for APIs. Session auth for Django Admin only.
```

---

## SOFT CONFLICTS (proceed with caution)

### S001 — Astro + React Islands + Tailwind JIT
```
Issue:      React island styles may not be purged correctly in some versions.
Resolution: Add React component paths explicitly to tailwind.config.js content array.
Severity:   Warning — test build output before delivery.
```

### S002 — Django CORS + gunicorn workers > 1
```
Issue:      Multiple workers + session-based auth requires shared session backend.
Resolution: If using JWT only (recommended), no issue.
Severity:   Warning — only applies if session auth is active.
```

### S003 — PostgreSQL 16 + psycopg2 connection pooling
```
Issue:      Django opens one connection per request — can exhaust max_connections.
Resolution: For production: add pgbouncer.
            For development/SMB scale: default is acceptable.
Severity:   Info — not relevant for La Forja local development.
```

---

## LAYER COMPATIBILITY MATRIX

### web_app
```
Presentation  ->  Astro 4+ / Tailwind 3+
    | (fetches)
Application   ->  Django REST Framework
    | (reads/writes)
Domain        ->  Django ORM + Models
    | (persists)
Infrastructure -> PostgreSQL 16+

Compatible: ALL above OK
Incompatible: Django + SQLite (H001) BLOCKED
```

### landing
```
Presentation  ->  Astro 4+ SSG / Tailwind 3+
Content       ->  Decap CMS (requires SSG mode)
Infrastructure -> Static hosting

Compatible: ALL above OK
Incompatible: SSR mode + Decap (H002) BLOCKED
```

### api
```
Interface     ->  DRF + drf-spectacular
Domain        ->  Django ORM + Models + Serializers
Infrastructure -> PostgreSQL 16+

Compatible: ALL above OK
```

### automation
```
Trigger       ->  GHL Webhooks or Scheduler
Processing    ->  Python + httpx + GHL API v2
State         ->  SQLite (local) or GHL Custom Objects

Compatible: ALL above OK
Note: SQLite acceptable for automation state (not web_app DB)
```

---

## VERSIONING RULES

1. Never mix major versions of Django (4.x + 5.x) in same project.
2. Always match DRF version to Django — see stack_versions.md.
3. Astro major updates require component audit.
4. PostgreSQL: always target 16.x for new projects.
