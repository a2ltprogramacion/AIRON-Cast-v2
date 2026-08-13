# ADR-002: Modelo de Datos de Quickreply

- **Estado:** Aceptado
- **Fecha:** 2026-06-06
- **Decisor:** ux-ui_specialist (con input de backend_specialist)
- **Proyecto:** quickreply

## Contexto

Quickreply almacena mensajes de respuesta, categorias, metricas de uso y un bloque de contacto global. El modelo debe:

1. Soportar busqueda full-text rapida en espanol (FTS5).
2. Permitir variables en mensajes (placeholders `{{nombre}}`).
3. Registrar metricas de uso para ranking por popularidad.
4. Ser simple de mantener (single-user, sin concurrencia, SQLite).
5. Evitar joins complejos (queremos queries directas).

## Decision

### Entidades principales

```
projects (existente)
   |
   +--< categories (N)
   |       id, name, color, icon, sort_order, is_archived
   |
   +--< messages (N) >---- tags (JSONField)
   |       id, title, content, category_id, variables (JSONField),
   |       tags (JSONField), is_favorite, is_archived,
   |       usage_count, last_used_at, created_at, updated_at
   |
   +--< usage_logs (N)  (hijo de messages)
   |       id, message_id, copied_at
   |
   +-- contact_block (singleton)
           id=1, address, phone, instagram, schedule, payment_methods
```

### Schema SQL

```sql
CREATE TABLE categories (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    name        TEXT    NOT NULL UNIQUE,
    color       TEXT    NOT NULL DEFAULT 'category-1',
    icon        TEXT,
    sort_order  INTEGER NOT NULL DEFAULT 0,
    is_archived INTEGER NOT NULL DEFAULT 0,
    created_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE messages (
    id            INTEGER PRIMARY KEY AUTOINCREMENT,
    title         TEXT    NOT NULL UNIQUE,
    content       TEXT    NOT NULL,
    category_id   INTEGER REFERENCES categories(id) ON DELETE SET NULL,
    variables     TEXT    NOT NULL DEFAULT '[]',  -- JSON: ["cliente_nombre"]
    tags          TEXT    NOT NULL DEFAULT '[]',  -- JSON: ["oferta", "nuevo"]
    is_favorite   INTEGER NOT NULL DEFAULT 0,
    is_archived   INTEGER NOT NULL DEFAULT 0,
    usage_count   INTEGER NOT NULL DEFAULT 0,
    last_used_at  TEXT,
    created_at    TEXT    NOT NULL DEFAULT (datetime('now')),
    updated_at    TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE usage_logs (
    id         INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id INTEGER NOT NULL REFERENCES messages(id) ON DELETE CASCADE,
    copied_at  TEXT    NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE contact_block (
    id              INTEGER PRIMARY KEY CHECK (id = 1),  -- singleton
    address         TEXT,
    phone           TEXT,
    instagram       TEXT,
    schedule        TEXT,
    payment_methods TEXT,        -- JSON: ["Mercado Pago", "Efectivo"]
    updated_at      TEXT NOT NULL DEFAULT (datetime('now'))
);

-- FTS5 virtual table
CREATE VIRTUAL TABLE messages_fts USING fts5(
    title, content, tags,
    content=messages,
    content_rowid=id
);

-- Triggers para sincronizar FTS
CREATE TRIGGER messages_ai AFTER INSERT ON messages BEGIN
    INSERT INTO messages_fts(rowid, title, content, tags)
    VALUES (NEW.id, NEW.title, NEW.content, NEW.tags);
END;

CREATE TRIGGER messages_ad AFTER DELETE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, title, content, tags)
    VALUES ('delete', OLD.id, OLD.title, OLD.content, OLD.tags);
END;

CREATE TRIGGER messages_au AFTER UPDATE ON messages BEGIN
    INSERT INTO messages_fts(messages_fts, rowid, title, content, tags)
    VALUES ('delete', OLD.id, OLD.title, OLD.content, OLD.tags);
    INSERT INTO messages_fts(rowid, title, content, tags)
    VALUES (NEW.id, NEW.title, NEW.content, NEW.tags);
END;
```

### Campos clave explicados

| Campo | Tipo | Razon |
|-------|------|-------|
| `messages.variables` | JSONField | Lista de nombres de variables detectadas en `content`. Se extrae con regex `{{(\w+)}}` al guardar. Permite saber que modal abrir al copiar. |
| `messages.tags` | JSONField | Tags libres en formato string. Buscables via FTS5 (concatenados en el indice). |
| `messages.usage_count` | Integer | Denormalizado para no tener que contar logs en cada GET. Se incrementa en `POST /messages/{id}/copy/`. |
| `messages.last_used_at` | Timestamp | Igual: denormalizado para ordenar por reciente. |
| `usage_logs` | Tabla separada | Auditoria detallada. Permite analytics ("a que hora copio mas?"). |
| `contact_block.id=1` | Singleton | Solo hay un bloque de contacto por app. El CHECK lo enforce a nivel DB. |

### Decisiones de diseno

1. **`variables` como JSONField y no tabla aparte**: el Operador no necesita filtrar por "mensajes con variable X". Solo necesita saber cuales son al copiar. Mantenerlo en el mismo registro evita un join.
2. **`tags` como JSONField**: igual razon. Si en el futuro se quiere filtrar por tag, se puede extraer a tabla aparte.
3. **`is_archived` en vez de `is_deleted`**: soft delete por defecto, recuperable. El campo se incluye en FTS5? NO, los archivados se excluyen del FTS trigger (decision: trigger no incluye archivados). Ver nota tecnica abajo.
4. **`usage_count` denormalizado**: alternativa era contar logs en vivo. Denormalizado = O(1) en GET. Trade-off: la tabla `usage_logs` crece, pero tiene indice por `message_id` y la rotamos si pasa de 10k registros (job manual, no en v1).
5. **FTS5 sincronizado con triggers**: patron estandar de SQLite. Mantiene el indice consistente sin intervencion de la app.
6. **Categorias con `color` predefinido**: las opciones son `category-1` a `category-8` mapeadas a tokens del design system. NO se permite color libre (mantiene consistencia visual).
7. **Singleton `contact_block`**: la app tiene UN bloque de contacto. El Operador no quiere gestionar multiples tiendas.

### Comportamiento de archivado

Cuando `messages.is_archived = 1`:
- **NO** se muestra en la lista principal
- **NO** se incluye en busquedas FTS5 por defecto
- **SI** aparece en `/usage` (para mantener historial)
- **SI** se puede restaurar (toggle del archivado)
- **SI** aparece si el operador filtra explicitamente "Mostrar archivados"

**Nota tecnica sobre FTS y archivado**: Los triggers re-indexan SIEMPRE (incluso archivados). El filtrado se hace en la query principal con `WHERE is_archived = 0` aplicado DESPUES del MATCH de FTS. Esto es valido porque FTS devuelve rowids y la query principal los filtra.

```sql
SELECT m.* FROM messages m
INNER JOIN messages_fts fts ON fts.rowid = m.id
WHERE messages_fts MATCH 'bateria'
  AND m.is_archived = 0
ORDER BY m.usage_count DESC, m.last_used_at DESC;
```

## Alternativas Consideradas

### Variables como tabla

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **JSONField en messages** (elegido) | Sin join, lista inmediata al copiar | No filtrable directamente | OK |
| Tabla `message_variables` | Normalizado, filtrable | Overkill para v1, join extra | Descartado |

### Tags como tabla

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **JSONField** (elegido) | Simple, FTS lo indexa | No hay jerarquia | OK |
| Tabla `tags` + `message_tags` | M2M, normalizado | Join extra, 2 tablas | Descartado para v1 |

### Soft delete vs hard delete

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **Soft delete (is_archived)** (elegido) | Recuperable, mantiene historial | Tabla crece | OK |
| Hard delete | Simple | Irreversible, rompe `usage_logs` FK | Descartado |

### Metricas en `usage_logs` vs denormalizado

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **Denormalizado en messages** (elegido) | GET O(1) | Inconsistencia si no se actualiza | OK con trigger en API |
| Solo `usage_logs` | Single source of truth | COUNT() en cada GET | Descartado |

## Consecuencias

### Positivas

- Queries simples: GET /messages con JOIN a categories es unico join usado en lectura normal.
- Busqueda FTS5 rapida (sub-100ms para 1000 mensajes).
- Auditoria con `usage_logs` sin afectar performance de lectura.
- Singleton de contacto enforced por CHECK constraint.

### Negativas

- Tabla `usage_logs` crece linealmente con el uso. Mitigacion: rotar cada 10k registros (job manual v1.1).
- FTS5 incluye archivados, filtro posterior. Si la tabla crece a >10k archivados, considerar FTS condicional.
- JSONField de variables y tags no es "tipado" por la DB. La validacion de formato es responsabilidad de la app.

## Plan de Implementacion

- **T03** (backend_specialist): modelos Django + migraciones + admin
- **T04** (backend_specialist): serializers + viewsets + API CRUD
- **T05** (backend_specialist): FTS5 + filtros combinados + ordenamiento
- **T06** (backend_specialist): endpoints copy/recent/most-used + importador

## Referencias

- Skill: `.agents/skills/database-architecture/SKILL.md`
- Skill: `.agents/skills/django-patterns/SKILL.md`
- ADR-001: stack tecnologico (Django + DRF + SQLite + FTS5)
- Schema del ecosistema: `core/airon_cast_schema.sql` (referencia para FTS5 pattern)
