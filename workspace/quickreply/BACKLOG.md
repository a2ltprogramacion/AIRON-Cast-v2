# BACKLOG — QuickReply

## Definición

**Nombre:** QuickReply
**Slug:** quickreply
**Tipo:** Aplicación web Django standalone
**Cliente:** Interno (Argenis / A2LT Soluciones)
**Fecha de creación:** 2026-06-11

---

## Objetivo

Aplicación web local para despachar respuestas de venta en Marketplace de Facebook y otras redes sociales. Permite buscar mensajes predefinidos con tokens de precio que se renderizan dinámicamente desde un inventario de productos en Excel.

---

## Funcionalidad

### Core
- [x] Carga de inventario de productos desde Excel (`.xlsx`, hoja `G3 Multi`)
- [x] Motor de renderizado de tokens `{CODIGO_usd}` y `{CODIGO_bcv}`
- [x] Buscador en tiempo real de plantillas de mensajes
- [x] Copiar al portapapeles con feedback visual
- [x] UI responsiva con cards colapsables (expand/collapse)

### Modelos de datos
- [x] `Product` — codigo (PK), producto, tipo, precio_usd, precio_bcv, actualizado_el
- [x] `MessageTemplate` — titulo, categoria, contenido, timestamps

### Endpoints
- [x] `GET /` — Dashboard principal
- [x] `POST /upload/` — Carga de Excel con feedback de errores
- [x] `GET /search/?q=` — Búsqueda con renderizado de tokens (JSON)

### Pendiente
- [ ] CRUD completo de plantillas desde UI (crear/editar/eliminar mensajes)
- [ ] Panel de administración Django decorado
- [ ] Historial de uso (cuántas veces se copió cada mensaje)
- [ ] Exportar mensajes a JSON/CSV
- [ ] Gestión de categorías desde UI
- [ ] Tests automatizados
- [ ] Integración futura con API de software de administración

---

## Stack tecnológico

- **Backend:** Django 6.x + SQLite
- **Procesamiento Excel:** pandas + openpyxl
- **Frontend:** HTML5 + Tailwind CSS (CDN) + Vanilla JS
- **Servidor:** `runserver 127.0.0.1:8123`
- **Ubicación:** `workspace/quickreply/src/`

---

## Decisiones arquitectónicas (ADR)

| Fecha | Decisión | Justificación |
|-------|----------|---------------|
| 2026-06-11 | Tailwind CSS sobre Bootstrap | Mayor control, más ligero, el operador se siente cómodo con Tailwind |
| 2026-06-11 | Nombre de app: QuickReply | Simple, descriptivo, sin asociación a cliente |
| 2026-06-11 | Tokens con formato `{CODIGO_usd}` / `{CODIGO_bcv}` |清晰, unambiguous, fácil de escribir en mensajes |
| 2026-06-11 | Excel con hoja "G3 Multi" | Compatibilidad con archivo existente del operador |
| 2026-06-11 | App nombre `reply` (no `messages`) | Evitar colisión con Django messages framework |

---

## Formato del Excel de precios

El archivo debe llamarse `quickreply_precios.xlsx` y contener:

| Columna | Tipo | Descripción |
|---------|------|-------------|
| TIPO | texto | Categoría del producto (opcional) |
| CODIGO | texto | Clave única (PK) |
| PRODUCTO | texto | Descripción del producto |
| PRECIO $ PUBLICADO | número | Precio en USD (divisas) |
| PRECIO $ BCV PUB. | número | Precio paralelo en USD |

> Nota: ambas columnas de precio están expresadas en USD. BCV es el "precio paralelo" para Venezuela.

---

## Formato de tokens en mensajes

```
{CODIGO_usd}  →  Reemplaza por precio en dólares (ej: 45.00)
{CODIGO_bcv}  →  Reemplaza por precio paralelo con formato local (ej: 75,00)
{CODIGO}      →  No existe por ahora (reservado)
```

Si el código no existe en la base de datos, se reemplaza por `[AGOTADO / CONSULTAR]`.