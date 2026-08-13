---
name: database-architecture
version: 1.0.0
type: backend
subtype: skill
tier: all
description: |
  Patrones de arquitectura de bases de datos para PostgreSQL y SQLite.
  Cubre selección de RDBMS, diseño de schemas, índices, migraciones,
  estrategias de claves y optimización de consultas.
  Activar cuando `backend_specialist` necesite diseñar modelos de datos,
  crear migraciones u optimizar consultas.
  Trigger phrases: "diseño de schema", "índices", "migración",
  "optimizar consulta", "database architecture", "crear tabla",
  "seleccionar base de datos".
  No activar para consultas Django ORM básicas (usar `django-patterns`).
triggers:
  primary: ["diseño de schema", "database architecture", "crear índice"]
  secondary: ["migración", "optimizar consulta", "modelo de datos",
             "PostgreSQL vs SQLite", "elegir base de datos"]
  context: ["backend development", "database design"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - backend_specialist
last_used: 2026-06-05
scope: restricted
---

# Database Architecture Patterns — AIRON‑Cast

Production-grade database design patterns for PostgreSQL (production) and
SQLite (development and edge deployments). Covers RDBMS selection, schema
design, indexing, migrations, and query optimization.

---

## 1. Database Selection Protocol

Never default to heavy infrastructure blindly.

- **PostgreSQL (Neon/Supabase):** Default for interconnected user
  relationships, high concurrent transactions, financial data integrity,
  or PostGIS mapping.
- **SQLite (Turso/Local):** Highly recommended for edge-deployed apps,
  isolated microservices, read-heavy dashboards, or multi-tenant B2B SaaS
  where tenants can be sharded into isolated `.db` files.

---

## 2. Schema Design Principles

### 2.1 Naming Conventions

- Tables: plural snake_case (`users`, `product_categories`)
- Columns: singular snake_case (`created_at`, `is_active`)
- Primary keys: `id BIGSERIAL` (PostgreSQL) or `INTEGER PRIMARY KEY AUTOINCREMENT` (SQLite)
- Foreign keys: `{referenced_table_singular}_id` (`category_id`)
- Timestamps: `created_at`, `updated_at` on every table; `deleted_at` for soft deletes
- Boolean columns: prefix with `is_` or `has_` (`is_active`, `has_subscription`)

### 2.2 Primary Key Strategies

| Strategy | When to use |
|----------|-------------|
| `BIGSERIAL` / `INTEGER AUTOINCREMENT` | Internal tables, low-scale mapping |
| `UUIDv4` | Public-facing APIs, horizontal scaling, prevents ID enumeration |
| `ULID` | When sortable unique identifiers are needed |

### 2.3 Timestamp Strategy

- Always use timezone-aware timestamps: `TIMESTAMPTZ` in PostgreSQL
- Every table must include `created_at` and `updated_at`
- Soft deletes: add `deleted_at` column, never hard-delete user data

### 2.4 Constraints

Always define constraints at the database level, not just in application code.

```sql
CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(200) NOT NULL,
    slug VARCHAR(200) NOT NULL UNIQUE,
    price DECIMAL(10,2) NOT NULL CHECK (price >= 0),
    stock INTEGER NOT NULL DEFAULT 0 CHECK (stock >= 0),
    category_id BIGINT NOT NULL REFERENCES categories(id)
        ON DELETE RESTRICT,
    is_active BOOLEAN NOT NULL DEFAULT true,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    deleted_at TIMESTAMPTZ,
    UNIQUE(name, category_id)
);
```

### 2.5 Foreign Key Cascades

- `ON DELETE RESTRICT`: financial ledgers, audit logs, anything irreversible
- `ON DELETE CASCADE`: pure child dependencies (order_items when order deleted)

---

## 3. The JSONField Exception

`JSONB` (PostgreSQL) or `JSONField` (Django) is acceptable ONLY for:

- Natively unstructured, variant payload data
- External webhook responses where schema thrashing is excessive

**Never use JSONField to bypass explicit Foreign Key relationships.**

---

## 4. Indexing Strategy

### 4.1 When to Index

- Primary keys (automatic)
- Foreign keys (always)
- Columns used in WHERE clauses frequently
- Columns used in ORDER BY and JOIN conditions

### 4.2 When NOT to Index

- Small tables (< 1000 rows)
- Boolean columns with 50/50 split (low cardinality) — unless combined
  contextually with other columns
- Columns rarely queried

### 4.3 Index Types

```sql
-- B-tree (default, good for equality and range queries)
CREATE INDEX idx_orders_user_id ON orders(user_id);

-- Partial index (indexes only rows matching condition)
CREATE INDEX idx_active_products
    ON products(name)
    WHERE is_active = true;

-- Composite index (column order matters)
CREATE INDEX idx_orders_user_date
    ON orders(user_id, created_at DESC);

-- Covering index (includes extra columns for index-only scans)
CREATE INDEX idx_orders_covering
    ON orders(user_id, status)
    INCLUDE (total_amount);

-- Unique index (enforces uniqueness)
CREATE UNIQUE INDEX idx_users_email ON users(email);
```

### 4.4 Anti-Patterns

- Indexing boolean flags alone (low cardinality → index ignored)
- Over-indexing write-heavy tables (each index slows INSERT/UPDATE/DELETE)

---

## 5. Migration Patterns

### 5.1 Rules

- Every schema change goes through a migration file
- Migrations are versioned and never modified after being applied
- Always include a rollback plan before production execution
- Test on a copy of production data first

### 5.2 Django Migrations

```bash
python manage.py makemigrations
python manage.py migrate
python manage.py showmigrations
python manage.py migrate app_name 0003_previous  # rollback
```

---

## 6. Query Optimization

### 6.1 EXPLAIN ANALYZE

Always analyze query plans before deploying to production.

```sql
EXPLAIN ANALYZE
SELECT p.name, c.name as category
FROM products p
JOIN categories c ON c.id = p.category_id
WHERE p.is_active = true
ORDER BY p.created_at DESC
LIMIT 20;
```

Look for:
- `Seq Scan` on large tables → add index
- `Nested Loop` with high row counts → add index on join column
- High `cost` values → restructure query

### 6.2 N+1 Prevention

Never loop over a queryset to perform distinct database fetches.

```python
# ❌ N+1: one query for products + N queries for categories
products = Product.objects.all()
for p in products:
    print(p.category.name)

# ✅ Eager loading
products = Product.objects.select_related('category').all()

# ✅ For ManyToMany
products = Product.objects.prefetch_related('tags').all()
```

### 6.3 SELECT Column Limiting

```python
# ❌ Fetches all columns
Product.objects.filter(is_active=True)

# ✅ Only what's needed
Product.objects.filter(is_active=True).only('id', 'name', 'price')
```

### 6.4 Bulk Operations

```python
# Bulk create
new_logs = [SystemLog(message=f"Event {i}") for i in range(1000)]
SystemLog.objects.bulk_create(new_logs)

# Bulk update
products = Product.objects.filter(category=old_cat)
for p in products:
    p.is_active = False
Product.objects.bulk_update(products, ['is_active'])
```

---

## 7. Database-Specific Features

### 7.1 PostgreSQL

```sql
-- Full-text search
CREATE INDEX idx_products_search ON products
    USING GIN(to_tsvector('spanish', name));

-- Window functions
SELECT user_id, amount,
    RANK() OVER (PARTITION BY user_id ORDER BY created_at DESC)
FROM transactions;
```

### 7.2 SQLite

```sql
-- FTS5 for full-text search
CREATE VIRTUAL TABLE products_fts USING fts5(name, description);

-- Enable WAL mode for concurrent reads
PRAGMA journal_mode = WAL;

-- Enable foreign keys
PRAGMA foreign_keys = ON;