# MISSION_CONTROL — QuickReply

## Registro de sesiones

### Sesión 1 — 2026-06-11

**Objetivo:** Crear aplicación web para despachar respuestas de marketplace.

**Acciones realizadas:**
- Creación de proyecto Django standalone en `workspace/quickreply/src/`
- Modelos: `Product` y `MessageTemplate` con campos según especificación
- Utils: `cargar_excel()` con detección inteligente de columnas y hojas; `render_template()` con regex para tokens
- Vistas: dashboard, upload_excel (con diagnóstico), search_templates (API JSON)
- UI: Template Tailwind CSS oscuro, cards colapsables, copiar al portapapeles, debounce 250ms
- Seeds: 26 mensajes precargados (categorías: Ventiladores, Bombas, Piscina, Herramientas, Electrodomesticos, etc.)
- Carga de Excel: 396 productos cargados desde `quickreply_precios.xlsx`

**Problemas resueltos:**
- Colisión de nombre `messages` con Django built-in → renombrado a `reply`
- Cache `.pyc` con código viejo → limpazza de `__pycache__`
- Hoja Excel con whitespace en nombre → detección con `.strip()`
- Plantillas con fórmulas → se usa `data_only=True` en openpyxl

**Pendiente:**
- CRUD de plantillas desde UI
- Decoración del admin
- Tests

**Estado del proyecto:** ACTIVE
**Checkpoint:** Todo el código en `workspace/quickreply/src/reply/`