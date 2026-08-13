# ADR-001: Stack Tecnologico de Quickreply

- **Estado:** Aceptado
- **Fecha:** 2026-06-06
- **Decisor:** requirements_architect (con aprobacion del Operador)
- **Proyecto:** quickreply

## Contexto

Quickreply es una aplicacion web interna para un unico usuario (vendedor de marketplace de Facebook) que necesita:
1. Backend con API REST para mensajes, categorias y metricas de uso.
2. Base de datos local (sin servicios en la nube) con busqueda full-text.
3. Frontend rapido, mobile-first, con minima friccion de interaccion (escribir poco, copiar rapido).
4. Costos $0 (sin servicios pagos, sin CDN externa, sin auth providers).
5. Stack conocido por el ecosistema AIRON-Cast, para que los agentes existentes puedan desarrollarlo sin aprender tecnologias nuevas.

## Decision

| Capa | Tecnologia | Version objetivo |
|------|------------|------------------|
| Backend framework | Django | 5.x |
| API | Django REST Framework | 3.15.x |
| Base de datos | SQLite | 3.x (incluye FTS5) |
| Busqueda full-text | SQLite FTS5 | nativo |
| Frontend framework | Astro | 5.x |
| Estilos | Tailwind CSS | 4.x (con `@theme`) |
| Interactividad | Alpine.js | 3.x |
| Tests backend | pytest + pytest-django | ultimas |
| Tests frontend | Playwright | ultimas |
| Encoding | UTF-8 estricto | en DB y todos los scripts |

## Alternativas Consideradas

### Backend

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **Django + DRF** (elegido) | Admin gratis, ORM maduro, ecosistema conocido, perfiles `backend_specialist` y skill `django-patterns` listos | Mas pesado que Flask | OK |
| Flask + SQLAlchemy | Mas ligero, flexible | Sin admin, hay que escribir mas boilerplate, sin skill dedicada | Rechazado |
| FastAPI | Asincrono, moderno, type hints | Admin no incluido, ecosistema Python+frontend menos maduro para nuestro caso | Descartado |

### Frontend

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **Astro + Tailwind + Alpine** (elegido) | SSG optimo, minimo JS, skill `astro-landing-kit` disponible, mismo stack que ya usamos en cafe-cenit | Menos adecuado para SPA complejos | OK |
| Next.js + React | Ecosistema grande, SSR/SSG | Mas JS, overkill para single-user, requiere mas tiempo de setup | Descartado |
| SvelteKit | Compilacion rapida, menos JS | Skill no disponible, nuevo para el equipo | Descartado |
| HTML plano + Vanilla JS | Cero dependencias, maximo control | UI desactualizada, sin tokens, dificil de mantener | Rechazado |

### Base de datos

| Opcion | Pros | Contras | Veredicto |
|--------|------|---------|-----------|
| **SQLite + FTS5** (elegido) | Cero config, archivo unico, FTS5 nativo en espanol, mismo motor que el ecosistema | No escala a multi-usuario concurrente | OK para MVP |
| PostgreSQL | Mejor para concurrencia, FTS con `tsvector` | Requiere instalacion, no es trivial en Windows, overkill | Descartado para v1 |
| MongoDB | Flexible, JSON nativo | Sin FTS confiable en espanol, licencia, otra skill | Descartado |

## Consecuencias

### Positivas

- **Reuso de skills**: `django-patterns`, `api-patterns`, `astro-landing-kit`, `tailwind-architecture`, `testing-tdd-architecture` se aplican directamente.
- **Costo $0**: todo es open source, sin servicios externos.
- **Mobile-first**: Astro genera HTML estatico, carga rapida en celular.
- **Debugging facil**: SQLite es un archivo, se puede abrir y ver.
- **Admin gratis**: Django admin sirve para inspeccionar mensajes sin escribir UI extra.
- **FTS5 ya conocido**: el ecosistema ya lo usa para `adrs_fts`, mismo motor.

### Negativas

- **SQLite no escala**: si en el futuro se quiere multi-usuario, hay que migrar a Postgres. La migracion es viable pero no trivial.
- **No hay servidor de apps dedicado**: el Operador debe correr `python manage.py runserver` localmente. Aceptable para single-user.
- **Django + Astro son dos procesos**: hay que gestionar dos terminales (backend y frontend). Aceptable, documentado en README.

### Riesgos asumidos

- **R1**: Si el volumen de mensajes crece a >10k, FTS5 sigue siendo rapido (<100ms) pero la UI puede necesitar virtualizacion. Aceptable para v1.
- **R2**: Si el Operador quiere acceso remoto, hay que exponer el backend (ngrok, Tailscale, etc.). Out-of-scope v1.

## Plan de Implementacion

1. **T03** (backend_specialist): setup Django + modelos
2. **T04** (backend_specialist): API REST basica
3. **T05** (backend_specialist): FTS5 + filtros
4. **T06** (backend_specialist): endpoints especiales + parser del seed
5. **T07-T10** (frontend_worker): UI completa
6. **T11** (tester): pytest + Playwright
7. **T12** (qa_auditor): audit final
8. **T13** (docs): README

## Referencias

- Perfil del agente: `.agents/profiles/backend_specialist.md`
- Perfil del agente: `.agents/profiles/frontend_worker.md`
- Skill: `.agents/skills/django-patterns/SKILL.md`
- Skill: `.agents/skills/astro-landing-kit/SKILL.md`
- Skill: `.agents/skills/tailwind-architecture/SKILL.md`
- Skill: `.agents/skills/api-patterns/SKILL.md`
- Constitucion: `AGENTS.md` (presupuesto $0, jurisdiccion, principios operativos)
