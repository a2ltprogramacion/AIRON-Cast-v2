# Backlog — Café Cenit

> Generado por `requirements_architect` · Slug: `cafe-cenit`

## Resumen Round-Robin

| ID  | Tarea                                                                  | Agente              | Prioridad | Dependencias   | Estado |
| --- | ---------------------------------------------------------------------- | ------------------- | --------- | -------------- | ------ |
| T01 | Identidad visual: design tokens y component specs                      | `ux-ui_specialist`  | 10        | —              | READY  |
| T02 | Copy de venta: hero, proceso, productos, testimonios, meta SEO        | `writer`            | 9         | T01            | READY  |
| T03 | Configuración base Astro 5 + Tailwind v4 + baseline files             | `frontend_worker`   | 8         | T01, T02       | READY  |
| T04 | Implementar Layout.astro + SeoHead.astro                               | `frontend_worker`   | 7         | T03            | READY  |
| T05 | Implementar Navbar + CurrencySwitcher + WhatsAppFloat                  | `frontend_worker`   | 6         | T03, T04       | READY  |
| T06 | Implementar Hero, Process, Products, Testimonials, Contact, Footer     | `frontend_worker`   | 5         | T03, T04, T05  | READY  |
| T07 | Integrar todo en `index.astro` con script de moneda                    | `frontend_worker`   | 4         | T06            | READY  |
| T08 | Lint + `astro build` + smoke test responsive                           | `tester`            | 3         | T07            | READY  |
| T09 | Auditoría QA final + veredicto                                         | `qa_auditor`        | 2         | T08            | READY  |
| T10 | README para Carlos (guía de mantenimiento)                             | `docs`              | 1         | T09            | READY  |

---

## T01: Identidad visual

**Agente:** `ux-ui_specialist`
**Prioridad:** 10
**Dependencias:** —
**Modelo sugerido:** deepseek-v4

**Descripción:**
Definir design tokens (paleta cálida confirmada, tipografía, espaciado) y especificaciones de componentes en `src/styles/design-tokens.json` y `src/styles/component-specs.md`. Aplicar arquetipo "Modern Clinic" + acentos artesanales.

**Criterios de aceptación:**
- [ ] `design-tokens.json` con 9 colores de marca + tipografía + escala
- [ ] `component-specs.md` con wireframes ASCII de las 7 secciones
- [ ] ADR-002-paleta.md registrado

---

## T02: Copy de venta

**Agente:** `writer`
**Prioridad:** 9
**Dependencias:** T01
**Modelo sugerido:** deepseek-v4

**Descripción:**
Generar textos persuasivos en español neutro/venezolano para hero (2 frases), proceso, fichas de 3 productos, placeholders de testimonios, contacto, y meta tags SEO.

**Criterios de aceptación:**
- [ ] `site.json` con datos de marca + contacto
- [ ] `products.json` con 3 fichas (descripción, notas, precio, peso)
- [ ] `process.json` con 3 pasos
- [ ] `testimonials.json` con 3 placeholders marcados
- [ ] `seo.json` con title, description, OG, Twitter cards

---

## T03: Configuración base

**Agente:** `frontend_worker`
**Prioridad:** 8
**Dependencias:** T01, T02
**Modelo sugerido:** deepseek-v4

**Descripción:**
Crear `package.json`, `astro.config.mjs`, `tsconfig.json`, `netlify.toml`, `public/robots.txt`, `public/humans.txt`, `src/styles/global.css` con `@theme` cargando design tokens.

**Criterios de aceptación:**
- [ ] `npm install` funciona sin errores
- [ ] `npm run build` produce `dist/` sin warnings
- [ ] `global.css` usa `@theme` con todos los tokens (sin HEX sueltos en HTML)
- [ ] `robots.txt` bloquea `/admin/` y referencia sitemap
- [ ] `humans.txt` acredita a A2LT Soluciones
- [ ] `netlify.toml` tiene 6+ headers de seguridad

---

## T04: Layout + SeoHead

**Agente:** `frontend_worker`
**Prioridad:** 7
**Dependencias:** T03
**Modelo sugerido:** deepseek-v4

**Descripción:**
Componente `Layout.astro` con `<html lang="es_VE">`, fuentes Fraunces + Inter precargadas, slot principal, y `<SeoHead />` con los 12 meta tags.

**Criterios de aceptación:**
- [ ] `Layout.astro` con tipografía y meta tags
- [ ] `SeoHead.astro` con title, description, canonical, OG (5), Twitter (1), robots, author
- [ ] Validador HTML pasa sin errores críticos

---

## T05: Chrome (Navbar + Switcher + WhatsApp Float)

**Agente:** `frontend_worker`
**Prioridad:** 6
**Dependencias:** T03, T04
**Modelo sugerido:** deepseek-v4

**Descripción:**
Navbar sticky con blur, switcher USD⇄Bs., y botón flotante de WhatsApp con pulse animation. Script TS para switcher con fetch a `dolarapi.com` y fallback.

**Criterios de aceptación:**
- [ ] Navbar siempre visible con blur al scroll
- [ ] Switcher muestra "USD" / "Bs." y actualiza los 3 precios con animación
- [ ] Si API BCV falla, switcher muestra "No disponible" y USD sigue visible
- [ ] Botón WhatsApp siempre visible (mobile + desktop), animación pulse, abre chat con mensaje

---

## T06: Secciones (Hero, Process, Products, Testimonials, Contact, Footer)

**Agente:** `frontend_worker`
**Prioridad:** 5
**Dependencias:** T03, T04, T05
**Modelo sugerido:** deepseek-v4

**Descripción:**
Implementar las 6 secciones consumiendo `src/content/*.json`. Mobile-first 375px.

**Criterios de aceptación:**
- [ ] Hero: badge + H1 (2 frases) + subtítulo + 2 CTAs + imagen provisional
- [ ] Process: grid 3 columnas en desktop, stack en mobile
- [ ] Products: 3 cards con notas, precio USD, switcher, botón WhatsApp por producto
- [ ] Testimonials: 3 cards con placeholders claros marcados
- [ ] Contact: form HTML5 con validación nativa
- [ ] Footer: 4 columnas con redes sociales (SVG) y crédito A2LT

---

## T07: Integración en index.astro

**Agente:** `frontend_worker`
**Prioridad:** 4
**Dependencias:** T06
**Modelo sugerido:** deepseek-v4

**Descripción:**
Componer la página `index.astro` con todas las secciones en orden, importar el script de switcher, y verificar que ancla correctamente.

**Criterios de aceptación:**
- [ ] `index.astro` con 7 secciones en orden
- [ ] Script de switcher se ejecuta en cliente (`<script>` con `is:inline`)
- [ ] Smooth scroll entre anchors funciona

---

## T08: Tests

**Agente:** `tester`
**Prioridad:** 3
**Dependencias:** T07
**Modelo sugerido:** (no requiere LLM)

**Descripción:**
Ejecutar `npm run build`, revisar warnings, validar que el HTML resultante tenga los anchors correctos y que el JS no rompa.

**Criterios de aceptación:**
- [ ] `astro build` exit code 0, sin warnings críticos
- [ ] `dist/index.html` existe
- [ ] Tamaños de bundle razonables (< 200KB JS)

---

## T09: Auditoría QA

**Agente:** `qa_auditor`
**Prioridad:** 2
**Dependencias:** T08
**Modelo sugerido:** (no requiere LLM)

**Descripción:**
Auditoría visual con checklist de criterios de aceptación, validación de design tokens, contraste WCAG, integridad de archivos.

**Criterios de aceptación:**
- [ ] `reports/qa_report.md` con verdict PASSED
- [ ] Sin issues CRITICAL o HIGH
- [ ] Approved for delivery

---

## T10: Documentación

**Agente:** `docs`
**Prioridad:** 1
**Dependencias:** T09
**Modelo sugerido:** deepseek-v4

**Descripción:**
Generar `README.md` para Carlos con: cómo cambiar precios, fotos, testimonios, WhatsApp, dominio, deploy.

**Criterios de aceptación:**
- [ ] README con instrucciones paso a paso para tareas comunes
- [ ] Sección troubleshooting (API BCV, deploy, dominio)
