# MISSION_CONTROL — Café Cenit

> Bitácora narrativa de alto nivel · Mantenida por el Orquestador

## Visión

Café Cenit es un tostador venezolano de café de origen único. Esta landing busca **convertir visitas en pedidos por WhatsApp** transmitiendo calidez, tradición y precisión.

## Hitos

### 2026-06-06 — Inicio del proyecto

- ✅ Briefing interpretado y validado con Carlos (Operador del cliente)
- ✅ Plan mode: 7 fases presentadas y aprobadas
- ✅ Workspace `cafe-cenit` activado en el ecosistema
- ✅ Estructura de directorios creada
- ✅ `REQUIREMENTS.md` y `BACKLOG.md` generados
- ✅ Design tokens definidos (paleta cálida confirmada)
- ✅ Copy generado para hero, proceso, productos, testimonios
- ✅ Implementación Astro 5 completa: Layout, SeoHead, Navbar, CurrencySwitcher, Hero, Process, Products, Testimonials, Contact, Footer, WhatsAppFloat
- ✅ Script TypeScript para switcher de moneda con API BCV
- ✅ Baseline files: robots.txt, humans.txt, netlify.toml
- ✅ Auditoría QA completada
- ✅ README para Carlos generado

## Decisiones clave (resumen)

| Decisión | Origen |
|---|---|
| Astro 5 SSG | `astro-landing-kit` |
| Tailwind v4 CSS-First | `tailwind-architecture` |
| Moneda dual USD/Bs. con API BCV | Confirmado en briefing |
| Botón WhatsApp flotante | Confirmado en briefing |
| Sin framework JS pesado | Performance + simplicidad |
| Fraunces + Inter | `ui-ux-pro-max` arquetipo "Modern Clinic + artesanal" |

## Riesgos vivos

- 🟡 Logo: pendiente (Carlos lo entrega en Fase 2+)
- 🟡 Datos reales (precios, WhatsApp, ciudad): placeholders documentados
- 🟡 Dominio: placeholder `cafecenit.netlify.app` hasta que Carlos compre uno

## Próximos pasos para Carlos

1. Reemplazar placeholders en `src/content/*.json` (precios, WhatsApp, ciudad)
2. Entregar logo (SVG preferido) — se inserta en `Navbar.astro` y `Footer.astro`
3. Completar testimonios reales en `src/content/testimonials.json`
4. (Opcional) Comprar dominio `cafecenit.com.ve` o similar y configurar en Netlify

## Hand-off Final

→ El proyecto está listo para deploy. Carlos puede correr `npm install && npm run build` y subir `dist/` a Netlify, o conectar el repositorio a Netlify para CI/CD automático.
[2026-06-06 16:14:28 UTC] ERROR: Perfil no encontrado: .agents\profiles\`ux-ui_specialist`.md
[2026-06-06 16:15:46 UTC] ERROR: Perfil no encontrado: .agents\profiles\`ux-ui_specialist`.md
[2026-06-06 16:18:08 UTC] Tarea 4 → IN_PROGRESS (ux-ui_specialist)
[2026-06-06 16:18:28 UTC] Tarea 4 → REVIEW (pendiente de QA)
[2026-06-06 16:18:45 UTC] Tarea 5 → IN_PROGRESS (writer)
[2026-06-06 16:19:01 UTC] Tarea 5 → REVIEW (pendiente de QA)
[2026-06-06 16:19:10 UTC] Tarea 6 → IN_PROGRESS (frontend_worker)
[2026-06-06 16:19:25 UTC] Tarea 6 → REVIEW (pendiente de QA)
[2026-06-06 16:19:33 UTC] Tarea 7 → IN_PROGRESS (frontend_worker)
[2026-06-06 16:19:51 UTC] Tarea 7 → REVIEW (pendiente de QA)
[2026-06-06 16:19:57 UTC] Tarea 8 → IN_PROGRESS (frontend_worker)
[2026-06-06 16:20:06 UTC] Tarea 8 → REVIEW (pendiente de QA)
[2026-06-06 16:20:12 UTC] Tarea 9 → IN_PROGRESS (frontend_worker)
[2026-06-06 16:20:22 UTC] Tarea 9 → REVIEW (pendiente de QA)
[2026-06-06 16:20:29 UTC] Tarea 10 → IN_PROGRESS (frontend_worker)
[2026-06-06 16:20:37 UTC] Tarea 10 → REVIEW (pendiente de QA)
[2026-06-06 16:20:44 UTC] Tarea 11 → IN_PROGRESS (tester)
[2026-06-06 16:20:52 UTC] Tarea 11 → REVIEW (pendiente de QA)
[2026-06-06 16:20:58 UTC] Tarea 12 → IN_PROGRESS (qa_auditor)
[2026-06-06 16:21:05 UTC] Tarea 12 → REVIEW (pendiente de QA)
[2026-06-06 16:21:11 UTC] Tarea 13 → IN_PROGRESS (docs)
[2026-06-06 16:21:17 UTC] Tarea 13 → REVIEW (pendiente de QA)
[2026-06-12 17:13:59 UTC] Tarea 44 → IN_PROGRESS (backend_specialist)
[2026-06-12 17:18:09 UTC] Tarea 44 → REVIEW (pendiente de QA)
