# Quickreply

> Busca, filtra y copia mensajes de respuesta para Marketplace de Facebook en segundos.
> Construido para g3multistore y vendedores que responden el mismo tipo de pregunta 20 veces al dia.

![Status](https://img.shields.io/badge/status-MVP-success)
![Tests](https://img.shields.io/badge/tests-93%20passed-success)
![Coverage](https://img.shields.io/badge/coverage-99%25-success)
![Stack](https://img.shields.io/badge/stack-Django%20%2B%20DRF%20%2B%20Astro%20%2B%20Tailwind-blue)

---

## Que hace

Quickreply es una biblioteca de mensajes pre-escritos optimizada para vendedores de Marketplace de Facebook. Reemplaza el ciclo "abrir notas → buscar → copiar → pegar" por un buscador con un solo click.

**Funcionalidades principales:**

- Busqueda full-text rapida con SQLite FTS5
- Filtros por categoria (14 categorias inferidas automaticamente)
- Marcador de favoritos
- Variables `{{placeholder}}` con preview en vivo
- Copiar al portapapeles con un click
- Atajos de teclado: `Ctrl+K` (buscar), `Esc` (limpiar), flechas (navegar), `Enter` (copiar)
- Bloque de contacto corporativo (telefono, Instagram, direccion, horario) editable
- Mobile-first responsive (375px → desktop)
- Dark mode automatico segun preferencia del sistema

**No hace (por diseno):**

- No envia mensajes automaticamente (violaria ToS de Facebook)
- No accede a la API de Messenger (no existe API publica)
- No hace scraping de chats

---

## Quickstart

### Requisitos

- Python 3.11+
- Node.js 18+
- pip + npm

### 1. Backend (Django)

```bash
cd workspace/quickreply/src/api

# Crear virtualenv (opcional)
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # macOS/Linux

# Instalar dependencias
pip install -r requirements.txt

# Inicializar base de datos (solo la primera vez)
python manage.py migrate

# (Opcional) Importar los 23 mensajes reales del seed
python manage.py import_messages ../seed/mensajes_originales.txt

# Iniciar servidor
python manage.py runserver
# -> http://localhost:8000
```

### 2. Frontend (Astro)

En otra terminal:

```bash
cd workspace/quickreply/src/frontend

# Instalar dependencias
npm install

# Crear .env (opcional, default apunta a localhost:8000)
cp .env.example .env

# Iniciar dev server
npm run dev
# -> http://localhost:4321

# Build para produccion
npm run build
npm start
```

### 3. Uso

1. Abre `http://localhost:4321` en el navegador
2. Escribe lo que queres responder (ej. "precio bomba", "horario", "disponible")
3. Click en **Copiar** o presiona `Enter` sobre el mensaje resaltado
4. Si el mensaje tiene variables, completa los valores y click **Copiar**
5. Pega en el chat de Facebook Marketplace

---

## Estructura del Proyecto

```
workspace/quickreply/
├── BACKLOG.md                   # 13 tareas del proyecto
├── REQUIREMENTS.md              # 11 secciones con criterios de aceptacion
├── MISSION_CONTROL.md           # Bitacora narrativa
├── seed/
│   └── mensajes_originales.txt  # 23 mensajes reales del operador
├── adrs/                        # Decisiones arquitectónicas
│   ├── ADR-001-stack.md
│   └── ADR-002-data-model.md
├── src/
│   ├── styles/                  # Design tokens (T02)
│   │   ├── design-tokens.json
│   │   └── component-specs.md
│   ├── api/                     # Backend Django
│   │   ├── manage.py
│   │   ├── quickreply/{settings,urls,wsgi,asgi}.py
│   │   ├── catalog/
│   │   │   ├── models.py        # Category, Message, UsageLog, ContactBlock
│   │   │   ├── views.py         # ViewSets + 5 custom actions
│   │   │   ├── serializers.py
│   │   │   ├── urls.py
│   │   │   ├── parser.py        # Parser del seed
│   │   │   └── migrations/
│   │   └── tests/               # 93 tests, 99% coverage
│   └── frontend/                # Frontend Astro 5
│       ├── package.json
│       ├── astro.config.mjs
│       ├── src/
│       │   ├── layouts/Layout.astro
│       │   ├── components/      # 7 componentes
│       │   ├── pages/           # 2 paginas
│       │   ├── lib/api.ts       # Cliente TypeScript
│       │   ├── scripts/         # TS modular
│       │   └── styles/global.css # Tailwind v4 + tokens
│       └── tests/test_smoke.py  # 9 tests E2E
└── reports/
    ├── test_report.md
    └── audit_report.md
```

---

## Stack Tecnologico

| Capa | Tecnologia | Por que |
|---|---|---|
| Backend | Django 5.1 + DRF 3.15 | Rapidez de desarrollo, admin gratis, ecosistema maduro |
| DB | SQLite con FTS5 | Cero configuracion, full-text nativo, ideal para <100K mensajes |
| Busqueda | FTS5 + triggers | Sub-50ms incluso con miles de mensajes |
| Frontend | Astro 5 | SSG + islands, minima JS, SEO-friendly |
| CSS | Tailwind v4 | Tokens consistentes, sin config JS, @theme CSS-first |
| Interactividad | Alpine.js | Sprinkles reactivos sin React |
| Lenguaje backend | Python 3.11+ | Ecosistema AI-friendly |
| Lenguaje frontend | TypeScript | Type safety sin overhead |
| Adapter | Node 24+ | Produccion simple con `npm start` |

Ver `adrs/ADR-001-stack.md` para justificacion completa.

---

## API REST

Base URL: `http://localhost:8000/api/`

### Mensajes

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/messages/` | Listar (filtros: `q`, `category`, `tag`, `is_favorite`, `include_archived`) |
| POST | `/messages/` | Crear |
| GET | `/messages/{id}/` | Detalle |
| PATCH | `/messages/{id}/` | Actualizar parcial |
| DELETE | `/messages/{id}/` | Archivar (soft delete) |
| POST | `/messages/{id}/copy/` | Marcar como copiado (incrementa `usage_count`, registra `UsageLog`) |
| GET | `/messages/recent/` | Ultimos 10 copiados |
| GET | `/messages/most_used/` | Top 10 mas copiados |
| GET | `/messages/?q=texto` | Busqueda full-text con wildcard prefix |
| POST | `/messages/import_seed/` | Importar desde archivo (cuerpo: `{"file_path": "..."}`) |
| GET | `/messages/export/` | Exportar todos a JSON |

### Categorias

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/categories/` | Listar (filtros: `is_archived`, `color`, ordering: `sort_order`, `name`, `-message_count`) |
| POST | `/categories/` | Crear |
| PATCH | `/categories/{id}/` | Actualizar |
| DELETE | `/categories/{id}/` | Archivar |

### ContactBlock (singleton)

| Metodo | Endpoint | Descripcion |
|---|---|---|
| GET | `/contact/` | Obtener bloque (siempre el mismo) |
| PUT | `/contact/` | Actualizar bloque |

---

## Modelo de Datos

```
Category
├── name (unique)
├── color (token: category-1..8)
├── icon (emoji opcional)
├── sort_order
├── is_archived
└── message_count (denormalizado)

Message
├── title (unique)
├── content (text con {{variables}})
├── category (FK → Category)
├── tags (JSONField: ["oferta","disponible"])
├── is_favorite (bool)
├── is_archived (bool, soft delete)
├── usage_count (denormalizado, incrementado en copy)
├── last_used_at (timestamp)
└── variables (extraidas del content en save())

UsageLog (auditoria)
├── message (FK → Message)
└── copied_at (auto)

ContactBlock (singleton)
├── phone
├── instagram
├── address
├── schedule
└── updated_at
```

Ver `adrs/ADR-002-data-model.md` para el modelo extendido con indices, constraints y triggers.

---

## Variables `{{placeholder}}`

Cualquier mensaje puede contener variables que se reemplazan al copiar:

**Ejemplo en seed:**

```
Hola {{cliente_nombre}}, el {{producto}} esta disponible para entrega inmediata.
```

**Flujo:**

1. Click en "Copiar" en la card
2. Se abre modal pidiendo los valores
3. Preview en vivo abajo
4. Click "Copiar" → texto al portapapeles con valores reemplazados
5. Pegar en chat de Facebook

**Validacion automatica:**

- Las variables se extraen en `Message.save()` con regex `\{\{(\w+)\}\}`
- Se validan al renderizar (sustitucion silenciosa si falta valor)
- Aparecen como pills mono en la card

---

## Testing

```bash
# Backend
cd src/api
python -m pytest catalog/tests/ --cov=catalog
# -> 93 passed, 99% coverage

# Frontend smoke test (requiere servers activos)
cd src/frontend
python -m pytest tests/test_smoke.py -v
# -> 9 tests
```

Ver `reports/test_report.md` para detalle.

---

## Decisiones Arquitectonicas (ADRs)

| # | Decision | Estado |
|---|---|---|
| ADR-001 | Stack: Django+DRF+SQLite/FTS5 + Astro+Tailwind+Alpine | Aceptada |
| ADR-002 | Modelo de datos: 4 entidades + denormalizacion + soft delete | Aceptada |

---

## Licencia

Privado - A2LT Soluciones / Argenis.

---

> Construido con AIRON-Cast, 11 agentes y 0 USD en APIs.
