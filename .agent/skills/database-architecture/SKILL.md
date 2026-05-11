---
name: database-architecture
description: "Ingeniería de Arquitectura de Bases de Datos A2LT. Guía las decisiones entre Postgres vs SQLite, selección de ORM, estrategias de indexación, diseño de schemas (PKs/FKs) y optimización de N+1 queries."
allowed-tools: Read, Write, Edit, Glob, Grep
---

# Database Architecture & Optimization (A2LT Standard)

This robust, standalone skill governs all interactions involving the persistence layer: from selecting the exact RDBMS down to indexing strategies and query optimizations.

---

## 1. Database Selection Protocol

Never default to heavy infrastructure blindly.

- **PostgreSQL (Neon/Supabase):** Default for interconnected user relationships, heavy concurrent transactions, or PostGIS mapping.
- **SQLite (Turso/Local):** Highly recommended for Edge-deployed apps, isolated microservices, read-heavy dashboards, or B2B SaaS where tenants can be physically sharded into isolated `.db` files.

---

## 2. Schema Construction, Normalization & Keys

- **Normalization First:** Design the relational structure conceptually (1NF, 2NF, 3NF minimum) before writing physical `models.py` or `.sql` constraints.
- **Primary Keys:**
  - `UUIDv4/v7` for APIs scaling horizontally and to prevent ID enumeration.
  - `ULID` (UUID + Sortable time) for sequential clustering.
  - `Auto-increment INT` only for strictly internal, low-scale mapping tables.
- **Timestamp Strategy:** Enforce `created_at`, `updated_at`, and `deleted_at` (soft deletes) on all entities. **Always use timezones (`TIMESTAMPTZ`)**.
- **Foreign Key Cascades:** Be explicit. Use `ON DELETE RESTRICT` for financial ledgers, and `ON DELETE CASCADE` only for pure child-dependencies.

---

## 3. The `JSONField` Exception Layer

While A2LT strictly mandates classical relational paradigms, PostgreSQL's `JSONB` (`JSONField` in Django) is acceptable **ONLY** for:

- Natively unstructured, variant payload data.
- External webhook responses where columns undergo excessive thrashing.
  Do **NOT** use `JSONField` to bypass explicit Foreign Key relationships or standard table associations.

---

## 3. Indexing Strategy

Never deploy without explicitly mapping the index paths.

1. **B-Tree (Default):** For exact matches, ranges, and sorting (`>`, `<`, `=`).
2. **Partial Indexes:** Create indexes filtered by a `WHERE` clause (e.g., heavily querying ONLY `status = 'active'`).
3. **Composite/Covering Indexes:** If a query constantly hits `(user_id, status)`, build a composite index on both.
4. **Anti-Pattern:** Do not index boolean flags (`is_active`) unless combined contextually with other columns (low cardinality destroys index efficiency).

---

## 4. Query Optimization & ORMs

- **The N+1 Mutilation:** Never loop over a queryset to perform distinct DB fetches. Always use `select_related()` (for ForeignKeys) or `prefetch_related()` (for ManyToMany) in Django, or complex `JOIN` logic in Typescript ORMs (Drizzle/Prisma).
- **SELECT Limit:** `SELECT *` is forbidden in high-throughput endpoints. Extract exclusively the required columns (`.only('id', 'name')`).
- **Explain Analyze:** If a query exceeds 100ms, run `EXPLAIN ANALYZE` to detect Seq Scans (Sequential Scans) hitting tables lacking indexes.
