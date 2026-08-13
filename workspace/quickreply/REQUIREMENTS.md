# Quickreply - Requerimientos

> Generado por `requirements_architect` · Slug: `quickreply`
> Version: 1.0.0 · Fecha: 2026-06-06

---

## 1. Vision General

**Problema.** Un vendedor en marketplace de Facebook (caso: g3multistore vende como pagina "Tienda g3 Multistore") recibe entre 20 y 50 mensajes privados por dia con preguntas repetitivas: "Tienen baterias para moto?", "Hacen envios a [ciudad]?", "Cual es el precio del taladro?", "Aceptan mercado pago?". Hoy las respuestas se redactan a mano cada vez o se copian desde notas de celular. Esto consume 30-60 minutos diarios y produce respuestas inconsistentes (precios desactualizados, datos de contacto mal escritos).

**Solucion.** Una aplicacion web **interna** (uso del Operador, no del cliente final) que:
1. Almacena una biblioteca de mensajes pre-redactados, organizados por categoria de producto y tipo de consulta.
2. Permite buscar en milisegundos el mensaje correcto por palabra clave, categoria o tag.
3. Copia el mensaje al portapapeles con un click (o `Ctrl+K` + Enter).
4. Soporta **variables** simples (ej. `{{cliente_nombre}}`, `{{producto_consultado}}`) que el vendedor completa al copiar.
5. Mantiene un **bloque de contacto global** (direccion, telefono, Instagram, horarios) que se inyecta en cada copia y se edita en un solo lugar.

**Lo que NO es.** NO es un chatbot, NO automatiza respuestas, NO se conecta a la API de Messenger. Es una herramienta de productividad **manual** que respeta los Terminos de Servicio de Facebook y el estilo personal del vendedor.

---

## 2. Stack Tecnologico (resumen, ver ADR-001 para detalle)

| Capa | Tecnologia | Justificacion corta |
|------|------------|---------------------|
| Backend | Django 5 + DRF 3.15 | Admin gratis, ORM maduro, SQLite nativo, ecosistema conocido |
| BD | SQLite 3 con FTS5 | Cero config, mismo motor que el ecosistema ya usa, full-text en espanol |
| Frontend | Astro 5 | Estatico por default, optimo para contenido, minimo JS |
| Estilos | Tailwind CSS v4 | CSS-First `@theme`, tokens desde JSON, sin config JS |
| Interactividad | Alpine.js 3 | 15kb, declarativo, sin build step complejo |
| Tests backend | pytest + pytest-django | Coverage >80% obligatorio |
| Tests frontend | Playwright | Smoke test E2E del flujo principal |
| API | REST con JSend envelope | Consistente con el ecosistema, simple de consumir |

---

## 3. Estructura de Paginas

| Ruta | Proposito | Componentes principales |
|------|-----------|--------------------------|
| `/` | Buscador + lista de mensajes | SearchBar, CategoryFilter, MessageList, MessageCard |
| `/messages/new` (modal) | Crear mensaje | MessageForm |
| `/messages/{id}/edit` (modal) | Editar mensaje | MessageForm precargado |
| `/categories` | Gestion de categorias | CategoryList, CategoryForm |
| `/contact` | Editar bloque de contacto | ContactForm |
| `/usage` | Dashboard rapido de uso | RecentList, MostUsedList |

**Mobile-first**, ancho objetivo 375px (uso principal desde celular). Breakpoint desktop en 768px.

---

## 4. Componentes Reutilizables

| Componente | Uso | Props clave |
|------------|-----|-------------|
| `Layout.astro` | Shell con header + slot | title, description |
| `SearchBar.astro` | Input con debounce 300ms | placeholder, x-model |
| `MessageCard.astro` | Card de mensaje en lista | message, onCopy, onEdit |
| `MessageList.astro` | Lista virtualizable simple | messages, loading, empty |
| `CategoryFilter.astro` | Sidebar de categorias con conteo | categories, selected |
| `MessageForm.astro` | Form crear/editar | message, mode |
| `VariablesModal.astro` | Modal de variables antes de copiar | message |
| `Toast.astro` | Notificacion "Copiado" 2s | message, type |
| `ContactBlock.astro` | Snippet global de contacto | (lee de config) |

---

## 5. Modelo de Dominio (resumen, ver ADR-002 para detalle)

```
Category (1) ──< Message (N) >── (N) Tag (via JSONField)
                     │
                     └──< UsageLog (1:N)
```

- **Category**: `id, name, color, icon, sort_order, is_archived`
- **Message**: `id, title, content, category_id, variables (JSONField), tags (JSONField), is_favorite, is_archived, usage_count, last_used_at, created_at, updated_at`
- **UsageLog**: `id, message_id, copied_at, ip_address (opcional)`
- **ContactBlock** (config global, singleton): `address, phone, instagram, schedule, payment_methods`

---

## 6. Casos de Uso Principales

| # | Actor | Accion | Resultado esperado |
|---|-------|--------|---------------------|
| CU1 | Vendedor | Busca "bateria moto" | Lista de mensajes relevantes ordenados por uso |
| CU2 | Vendedor | Click en boton "Copiar" | Mensaje en portapapeles, contador +1, toast |
| CU3 | Vendedor | Copia mensaje con variables | Modal pide `cliente_nombre`, copia con valores |
| CU4 | Vendedor | Crea nuevo mensaje | Validacion, guardado, aparece en lista |
| CU5 | Vendedor | Edita bloque de contacto | Cambios reflejados en mensajes que lo referencian |
| CU6 | Vendedor | Marca mensaje como favorito | Aparece primero en busquedas |
| CU7 | Vendedor | Importa archivo seed | 23 mensajes creados con categorias inferidas |
| CU8 | Vendedor | Archiva mensaje | No aparece en busquedas por defecto |

---

## 7. MVP Scope (v1) y Out-of-Scope

### 7.1 MVP v1 - incluido

- [x] CRUD de mensajes con busqueda FTS5
- [x] CRUD de categorias
- [x] Bloque de contacto global editable
- [x] Sistema de variables con modal
- [x] Importador del archivo seed con 23 mensajes
- [x] Copiar al portapapeles con feedback visual
- [x] Atajos: Ctrl+K (buscar), Esc (limpiar), Enter (copiar seleccionado)
- [x] Favoritos y archivado
- [x] Mobile-first responsive
- [x] Admin Django para inspeccion

### 7.2 Out-of-Scope v1 - NO incluir

- [ ] Autenticacion / login (es single-user, el Operador es el unico usuario)
- [ ] Multi-tenancy (no hay multiples tiendas)
- [ ] Webhooks o integracion con Messenger
- [ ] Sincronizacion en la nube (todo es local)
- [ ] Versionado de mensajes (no hay historial de cambios)
- [ ] Adjuntar imagenes a mensajes (solo texto)
- [ ] Envio automatico de respuestas (viola ToS)
- [ ] Rich text editor (Markdown plano es suficiente)
- [ ] i18n (solo espanol)
- [ ] Modo oscuro (se puede agregar en v2)

---

## 8. Restricciones

| # | Restriccion | Origen | Mitigacion |
|---|-------------|--------|------------|
| R1 | Cero costo en APIs externas | Operador | Stack 100% local, sin servicios pagos |
| R2 | No automatizar respuestas | ToS de Facebook | Solo copia manual, sin API de Messenger |
| R3 | No login / auth | Simplificar uso local | Single-user, deploy en localhost |
| R4 | Codificacion UTF-8 | Mensajes en espanol con acentos | Encoding estricto en todos los scripts |
| R5 | Sin emojis en artefactos generados | Politica AIRON-Cast | Reemplazar con placeholders `[EMOJI_*]` en codigo, emojis reales solo en BD |
| R6 | Coverage de tests >80% | Constitucion | pytest obligatorio, reporte de coverage en T11 |
| R7 | Sin comentarios en codigo | Politica de opencode | Codigo autoexplicativo |
| R8 | Stack conocido por el ecosistema | Operador | Solo perfiles y skills existentes, no crear nuevos |

---

## 9. Criterios de Aceptacion Generales

- [ ] Busqueda devuelve resultados en menos de 100ms para 1000 mensajes
- [ ] Copiar al portapapeles funciona en Chrome, Firefox, Safari mobile
- [ ] El importador procesa los 23 mensajes del seed sin errores
- [ ] El bloque de contacto se actualiza en todos los mensajes que lo referencian en el siguiente copiado
- [ ] La aplicacion arranca con `python manage.py runserver` + `npm run dev` sin pasos adicionales
- [ ] Tests pytest pasan con coverage >80%
- [ ] Tests Playwright cubren: busqueda, copiar, crear, usar variables
- [ ] Mobile (375px): la lista es legible, los botones son tactiles (>44px), el buscador es sticky
- [ ] Desktop (1024px+): sidebar visible, lista en 2 columnas opcional
- [ ] Sin errores en consola del navegador

---

## 10. Riesgos y Mitigaciones

| Riesgo | Probabilidad | Impacto | Mitigacion |
|--------|--------------|---------|------------|
| Clipboard API bloqueada en HTTP | Media | Alto | Fallback a `document.execCommand('copy')` |
| Parser del seed falla con formato nuevo | Alta | Bajo | Tests con casos validos y malformados, mensaje de error claro |
| FTS5 no indexa acentos correctamente | Baja | Medio | Verificar en T05, normalizar con `unaccent` si es necesario |
| Astro 5 cambia API | Baja | Medio | Lock de version en `package.json`, skill `astro-landing-kit` actualizado |
| Volumen de mensajes crece y la UI se vuelve lenta | Baja | Bajo | Paginacion + virtualizacion basica en T08 |

---

## 11. Metricas de Exito (post-lanzamiento)

- Tiempo promedio de respuesta a un cliente: <2 min (vs 5-10 min actual)
- Mensajes copiados por dia: 30-50
- Tasa de uso de variables: >40% de los mensajes
- Satisfaction del Operador: el vendedor la usa todos los dias

---

> *"La mejor herramienta de productividad es la que desaparece cuando la usas."*
> — Filosofia Quickreply
