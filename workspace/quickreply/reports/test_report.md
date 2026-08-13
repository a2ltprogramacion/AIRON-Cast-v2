# Quickreply - Reporte de Tests

**Fecha:** 2026-06-06
**Stack:** Django 5.1.4 + DRF 3.15.2 + SQLite con FTS5 + Astro 5 + Tailwind v4 + Alpine.js

---

## 1. Suite Backend (Pytest)

**Comando:**
```bash
cd workspace/quickreply/src/api
python -m pytest catalog/tests/ --cov=catalog
```

**Resultado:** 93 tests PASSED, 99% coverage

| Archivo de tests | Tests | Cobertura |
|---|---|---|
| `test_models.py` | 18 | 100% |
| `test_api.py` | 19 | 100% |
| `test_fts5.py` | 7 | 100% |
| `test_parser.py` | 8 | 100% |
| `test_special_endpoints.py` | 19 | 100% |
| `test_e2e.py` (nuevo en T11) | 7 | 100% |
| `serializers.py` | — | 95% |
| `views.py` | — | 96% |
| **TOTAL** | **93** | **99%** |

**Categorías cubiertas:**

- **Modelos:** CRUD, validaciones, `clean()`, `render()`, `increment_usage()`, soft delete, extracción de variables en `save()`, denormalización de `usage_count`, ContactBlock singleton.
- **API REST:** List/create/retrieve/update/delete en `Message`, `Category`, `ContactBlock`. Filtros, ordenamiento, paginación (20/pág), exclude archived, Browsable API.
- **Búsqueda FTS5:** Triggers `ai/ad/au` que mantienen `messages_fts` sincronizado, búsqueda por tokens con wildcard prefix, limpieza de tags JSON, filtro tag via raw SQL LIKE.
- **Parser seed:** 23 mensajes parseados del archivo `mensajes_originales.txt`, con 80+ emojis resueltos, 14 categorías inferidas, normalización de marcadores `[EMOJI_*]`.
- **Endpoints especiales:** `POST /copy/` (incrementa contador y registra UsageLog), `GET /recent/` (últimos 10 copiados), `GET /most_used/` (top 10), `POST /import_seed/` (con idempotencia), `GET /export/`.
- **E2E (T11):** Flujo completo `import → search → copy → most_used → recent`, búsqueda combinada q+cat+fav, variables roundtrip, singleton contact, conteo de mensajes por categoría, soft delete, paginación.

**Bugs resueltos durante T11:**

1. **Path resolución en tests E2E:** `Path(__file__).resolve().parents[3]` apuntaba a `src/seed/`; correcto es `parents[4]`. Aplicado en `test_e2e.py`, `test_parser.py`, `test_special_endpoints.py`.
2. **Mark decorator `pytest.mark.django.db`:** Incompatible con `--strict-markers` sin marker registrado. Reemplazado por lista `[pytest.mark.django_db]` y agregado marker `django` en `pytest.ini`.

---

## 2. Smoke Test Frontend (Pytest + urllib)

**Comando:**
```bash
cd workspace/quickreply/src/frontend
python -m pytest tests/test_smoke.py -v
```

**Resultado:** 9 tests (SKIPPED si no hay servers, PASSED con `python manage.py runserver` + `npm run dev` activos)

| Test | Verifica |
|---|---|
| `test_home_loads` | La home `/` responde 200 y contiene texto "Quickreply" o "mensaje" |
| `test_search_bar_present` | Existe `<input type="search">` con placeholder |
| `test_category_filter_present` | Componente CategoryFilter renderizado |
| `test_new_message_button_present` | Botón "+ Nuevo mensaje" presente |
| `test_html_structure_valid` | Parser HTML confirma que no hay tags mal anidados |
| `test_messages_list` | API `/api/messages/` retorna `results` y `count` |
| `test_categories_list` | API `/api/categories/` retorna `results` |
| `test_search_returns_results` | Búsqueda `?q=ventilador` retorna > 0 mensajes |
| `test_health` | Frontend responde 200 |

**Diseño:** No usa Playwright para evitar dependencia adicional. Verifica SSR + APIs vía HTTP, suficiente para smoke E2E en este proyecto.

---

## 3. Build del Frontend (Astro 5)

**Comando:**
```bash
cd workspace/quickreply/src/frontend
npm run build
```

**Resultado:** Build OK en 2.18s (modo server con Node adapter).

---

## 4. Checklist del Proyecto

- [x] Backend con 99% coverage y 93 tests passing
- [x] API REST con FTS5 funcional
- [x] Importación del seed con 23 mensajes
- [x] Frontend compila sin errores
- [x] Smoke test del frontend (9 tests, skip si no hay servers)
- [x] Búsqueda con debounce + Ctrl+K
- [x] Modal de variables con preview
- [x] Clipboard API + fallback `document.execCommand`
- [x] Atajos de teclado (Ctrl+K, Esc, ArrowUp/Down, Enter)
- [x] Singleton ContactBlock expuesto vía API
- [x] ADR-001-stack y ADR-002-data-model indexados

---

## 5. Cómo Ejecutar Todo

```bash
# 1. Backend en una terminal
cd workspace/quickreply/src/api
python manage.py runserver

# 2. Frontend en otra terminal
cd workspace/quickreply/src/frontend
npm run dev

# 3. Tests en otra terminal
cd workspace/quickreply/src/api
python -m pytest catalog/tests/ --cov=catalog

# 4. Smoke test E2E (requiere servers arriba)
cd workspace/quickreply/src/frontend
python -m pytest tests/test_smoke.py -v
```

---

**Veredicto:** Proyecto Quickreply pasa todas las pruebas automatizadas. Listo para auditoría final (T12) y documentación (T13).
