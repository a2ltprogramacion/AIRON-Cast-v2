# ECOSYSTEM EVOLUTION — AIRON‑Cast

> **Propósito:** Guía de procedimientos para modificar skills, agentes y reglas sin romper el ecosistema.  
> **Audiencia:** Cualquier LLM o desarrollador que interactúe con AIRON‑Cast.  
> **Principio rector:** Los agentes dependen de skills. Las skills tienen contratos. Si el contrato no cambia, los agentes no se tocan.
> **Última actualización:** 2026-06-06 — Ecosistema v1.2.0: proyecto `quickreply` (13/13 tareas, 93 tests, 99% coverage) ejecutado end-to-end. Caso de éxito documentado abajo.

---

## 1. Regla de Oro

**Nunca modifiques un agente si la skill que usa solo cambió internamente.**

Si una skill mejora su implementación pero mantiene la misma interfaz (entradas y salidas), los agentes que la usan **no necesitan actualizarse**. Se benefician automáticamente de la mejora.

Ejemplo:
- `a2lt-brand-kit` optimiza el CSS del footer.
- El agente `frontend_worker` sigue llamando a `get_component_css("footer")`.
- Resultado: el agente obtiene el nuevo CSS sin modificar una línea de su perfil.

---

## 2. Cuándo SÍ modificar un agente

Solo en estos tres casos:

| Caso | Disparador | Acción requerida |
|------|------------|------------------|
| **Cambio de interfaz** | La skill cambia el nombre de una función, añade un parámetro obligatorio o modifica el formato de salida. | Actualizar todos los agentes que la referencian. |
| **División de skill** | Una skill se separa en dos o más skills independientes. | Actualizar `assigned_skills` en los perfiles de los agentes afectados. |
| **Cambio de propósito** | La skill ya no resuelve lo mismo (ej: antes devolvía CSS, ahora genera componentes Astro completos). | Revisar jurisdicción y reglas del agente. Puede requerir reasignación de tareas. |

---

## 3. Protocolo de Versionado Semántico

Toda skill tiene un número de versión en su frontmatter (`SKILL.md`). El versionado sigue el estándar `MAJOR.MINOR.PATCH`:

| Cambio | Versión | ¿Afecta agentes? |
|--------|---------|-------------------|
| Corrección de bugs, optimización interna | `PATCH` (1.0.0 → 1.0.1) | No |
| Nueva funcionalidad compatible hacia atrás | `MINOR` (1.0.0 → 1.1.0) | No |
| Ruptura de interfaz, cambio de contrato | `MAJOR` (1.0.0 → 2.0.0) | **Sí** |

**Regla estricta:** Antes de aplicar un cambio `MAJOR`, el `meta_factory` debe listar todos los agentes que usan esa skill (consultando `manifest.json`) y presentar un plan de actualización al Operador.

---

## 4. Orden de Operaciones ante un Cambio

### 4.1 Cambio PATCH o MINOR (sin riesgo)

1. Modificar la implementación de la skill.
2. Ejecutar validadores (`yaml-validator` para el frontmatter, tests internos).
3. Incrementar la versión en `SKILL.md`.
4. Actualizar `manifest.json` con la nueva versión.
5. Documentar en ADR si el cambio es significativo.

**No se toca ningún agente.**

### 4.2 Cambio MAJOR (con riesgo)

1. **Diagnóstico previo:** `meta_factory` consulta `manifest.json` y lista los agentes que usan la skill.
2. **Plan de migración:** se prepara un documento con los cambios necesarios en cada agente.
3. **Aprobación del Operador:** el plan se presenta. Sin aprobación explícita, no se avanza.
4. **Ejecución ordenada:**
   - Primero: modificar la skill y su `SKILL.md` (versión `MAJOR`).
   - Segundo: modificar cada perfil de agente afectado.
   - Tercero: actualizar `manifest.json`.
5. **Validación post‑cambio:** ejecutar `qa_auditor` sobre los agentes modificados.
6. **Documentar:** ADR obligatorio explicando la ruptura y la migración.

---

## 5. Contratos Implícitos entre Skills y Agentes

Cada skill referenciada en un perfil de agente establece un contrato no escrito:

| Skill | Contrato implícito |
|-------|---------------------|
| `ui-ux-pro-max` | Proporciona tokens de diseño, paletas y tipografías consultables. |
| `a2lt-brand-kit` | Devuelve CSS, plantillas HTML y SVGs de la marca A2LT. |
| `tailwind-architecture` | Ofrece patrones de configuración de Tailwind y layouts. |
| `astro-landing-kit` | Proporciona componentes Astro predefinidos para landing pages. |
| `context7-resolver` | Resuelve consultas técnicas sobre documentación oficial. |
| `testing-tdd-architecture` | Ejecuta pruebas automatizadas con Playwright. |
| `skill-creator-pro` | Genera nuevas skills modulares. |
| `agent-creator-pro` | Genera nuevos perfiles de agentes. |
| `stitch-designer` | Prototipado UI vía StitchMCP. |
| `audit-code-review` | Auditoría de código: funcionalidad, calidad, seguridad, cobertura. |
| `agent-skill-scout` | Búsqueda de skills y agentes en repositorios externos. |
| `brainstorming` | Propuestas de diseño antes de commitear cambios. |
| `journal-writer` | Memoria institucional del ecosistema. |
| `manifest-updater` | Gestión del manifest.json. |
| `yaml-validator` | Validación de metadatos YAML de componentes. |
| `django-patterns` | Patrones de arquitectura Django y DRF para producción. |
| `database-architecture` | Patrones de arquitectura de bases de datos PostgreSQL y SQLite. |
| `api-patterns` | Patrones de diseño de APIs REST con Django REST Framework. |
| `seo-content-strategy` | Estrategia de contenidos SEO: clusters, LSI, densidad KW, refresh. |
| `seo-onpage-architecture` | Arquitectura On-Page: meta tags, schema, featured snippets. |
| `seo-technical-audit` | Auditoría técnica SEO: indexación, Core Web Vitals, score 0-100. |
| `geo-optimization` | Generative Engine Optimization (GEO) para motores RAG. |
| `institutional-memory` | Memoria institucional interna: ADRs y patrones vía FTS5. |
| `notebooklm-mcp-integration` | Integración con Google NotebookLM vía MCP y CLI. |
| `architecture-documentation` | Plantillas README, Changelogs, documentación inline. |

**Si modificas una skill, revisa su contrato.** Si el contrato sigue cumpliéndose, los agentes están a salvo.

---

## 6. Blindaje Anti‑Huérfanos

- **Frontmatter obligatorio** en todo `SKILL.md`:
  ```yaml
  assigned_agents: [@role]
  last_used: YYYY-MM-DD
  version: 1.0.0
  scope: restricted
  ```
- **Auditoría:** `meta_factory` ejecuta chequeo de huérfanos cada 14 días.
- **Archivado:** skills sin uso → `skills/archived/`. Restauración solo con aprobación del Operador.

---

## 7. Qué hacer si eres un LLM en una sesión nueva

Si estás leyendo esto sin acceso al historial completo de la conversación:

1. **Lee primero** `AGENTS.md`, `ceo.md` y `jurisdiction.md`. Son la constitución del ecosistema.
2. **Revisa** `manifest.json` para conocer el estado actual de agentes y skills.
3. **Antes de proponer cualquier cambio**, consulta la tabla de contratos implícitos (§5).
4. **Si un cambio afecta a más de un agente**, sigue el protocolo de cambio `MAJOR` (§4.2).
5. **Nunca modifiques un agente sin verificar si la skill que usa cambió su interfaz.**
6. **Respeta el versionado semántico** (§3). Si no sabes si un cambio es `MINOR` o `MAJOR`, pregunta al Operador.

---

## 8. Backlog de Evolución del Ecosistema

> **Origen:** Informe forense AIRON-Cast Legacy vs Actual (2026-06-03).  
> **Criterio de prioridad:** Crítica > Alta > Media > Baja.  
> **Estado:** 📋 Pendiente | 🔧 En progreso | ✅ Completado

### 🔴 Fase A: Blindaje del ecosistema (Crítico)

| # | Tarea | Estado |
|---|-------|--------|
| A1 | Crear `requirements.txt` | ✅ Completado |
| A2 | Migrar `hitl_gateway.py` | ✅ Completado |
| A3 | Migrar `checksum_verifier.py` | ✅ Completado |
| A4 | Migrar `validator.py` | ✅ Completado |

### 🟠 Fase B: Herramientas del meta_factory (Alta)

| # | Tarea | Estado |
|---|-------|--------|
| B1 | Migrar skill `agent-creator-pro` | ✅ Completado |
| B2 | Migrar skill `yaml-validator` | ✅ Completado |
| B3 | Migrar skill `journal-writer` | ✅ Completado |
| B4 | Migrar skill `brainstorming` | ✅ Completado |
| B5 | Migrar skill `manifest-updater` | ✅ Completado |
| B6 | Migrar `generate_agent_profile.py` a `tools/` | ✅ Completado |
| B7 | Migrar `validate_agent_profile.py` a `tools/` | ✅ Completado |
| B8 | Migrar `list_agents.py` a `tools/` | ✅ Completado |

### 🟡 Fase C: Skills referenciadas por agentes (Alta)

| # | Tarea | Estado |
|---|-------|--------|
| C1 | Migrar skill `stitch-designer` | ✅ Completado |
| C2 | Migrar/fusionar `audit-code-review` + `audit-lint-validate` + `clean-code` | ✅ Completado |
| C3 | Fusionar `find-skills` + `find-agents` + `skill-search` en `agent-skill-scout` | ✅ Completado |

### 🟢 Fase D: Expansión del taskforce (Media)

| # | Tarea | Estado |
|---|-------|--------|
| D1 | Crear perfil `pm.md` | ✅ Completado |
| D2 | Crear perfil `writer.md` | ✅ Completado |
| D3 | Crear perfil `docs.md` | ✅ Completado |
| D4 | Crear perfil `tester.md` | ✅ Completado |
| D5 | Crear workflow `system.md` | ✅ Completado |

### 🔵 Fase E: Deuda técnica de schema (Media)

| # | Tarea | Estado |
|---|-------|--------|
| E1 | Migrar tabla `model_usage` | ✅ Completado |
| E2 | Migrar trigger `checkpoints_cleanup` | ✅ Completado |
| E3 | Migrar vista `v_last_checkpoint` | ✅ Completado |
| E4 | Añadir CHECK constraints | ✅ Completado |
| E5 | Mejorar vista `v_project_status` con `progress_pct` | ✅ Completado |

### ⚪ Fase F: Herramientas y skills de dominio (Baja)

| # | Tarea | Estado |
|---|-------|--------|
| F1 | Crear `tools/db_ops.py` | ✅ Completado |
| F2 | Implementar `dashboard/index.html` + `dashboard_server.py` | ✅ Completado |
| F3 | Crear `tools/init_ecosystem.py` | ✅ Completado |
| F4 | Crear `start_airon.bat` | ✅ Completado |
| F5 | Migrar skills de backend: `django-patterns`, `database-architecture`, `api-patterns` | ✅ Completado |
| F6 | Migrar skills de SEO: `seo-content-strategy`, `seo-onpage-architecture`, `seo-technical-audit` | ✅ Completado |
| F7 | Migrar skill `geo-optimization` | ✅ Completado |
| F8 | Crear skill `institutional-memory` (antes `notebooklm` interno) | ✅ Completado |
| F9 | Crear skill `notebooklm-mcp-integration` (conexión externa Google NotebookLM) | ✅ Completado |
| F10 | Crear skill `architecture-documentation` | ✅ Completado |
| F11 | Actualizar `manifest.json` con 11 agentes, skills y MCPs | ✅ Completado |
| F12 | Actualizar perfil `orchestrator.md` con R07 (workflows) y paso 0 | ✅ Completado |

### ⚫ Descartados (no se migrarán)

| Elemento | Motivo |
|----------|--------|
| `rag-indexer`, `rag-query` (Legacy skills) | ChromaDB nunca se implementó; FTS5 los reemplaza |
| 51 scripts en `scratch/` (Legacy) | Workarounds puntuales; patrones ya extraídos |
| `.env` con GHL keys (Legacy) | Credenciales rotadas |
| `auto_commit.py` (Legacy) | Commits automáticos sin revisión no son seguros; el Operador decide tras QA |
| `context_compressor.py` (Legacy) | Redundante con `trajectory_compressor.py` en `core/` |
| `hitl_trigger.py` (Legacy) | Lógica ya integrada en `hitl_gateway.py` |
| `mobile-architecture` (skill) | No es necesaria para Fase 1; mobile-first se maneja con `tailwind-architecture` |
| Skills GHL (7 skills) | GoHighLevel no es parte del stack actual |

---

> *"Evoluciona con precisión quirúrgica. Cada skill tiene un contrato. Respétalo o documenta la ruptura."*
> — AIRON‑Cast Evolution Protocol, v1.2.0 (actualizado 2026-06-06)

---

## 9. Caso de Éxito: `quickreply` (2026-06-06)

**Proyecto:** Aplicación de biblioteca de mensajes para g3multistore (Marketplace de Facebook).
**Resultado:** 13/13 tareas completadas en sesión única, sin STOP_LOSS, sin HITL.
**Tiempo total:** ~6 horas de ejecución continua (driver LLM + orquestador).
**Costo:** $0 en APIs (todas las operaciones locales + caché).

### Métricas

| Métrica | Valor |
|---|---|
| Tareas | 13/13 (100%) |
| Tests backend | 93 passed |
| Coverage | 99% (988 statements, 14 miss) |
| Build frontend | OK en 2.22s |
| Artefactos generados | 25+ (modelos, vistas, componentes, ADR, docs) |
| ADRs indexados | 2 (stack, data-model) |
| Bugs resueltos in-flight | 6 |

### Stack validado

- **Backend:** Django 5.1.4 + DRF 3.15.2 + SQLite con FTS5 + django-filter
- **Frontend:** Astro 5 (server mode) + Tailwind v4 (CSS-first) + Alpine.js + TypeScript
- **Patrón:** SSR para carga inicial + CSR para interactividad; click handlers globales delegados

### Lecciones aprendidas (a propagar como skills)

1. **FTS5 standalone con `DELETE FROM fts WHERE rowid=OLD.id`:** El truco `'delete-command'` (`INSERT INTO fts(fts, rowid, ...) VALUES('delete', ...)`) ya no funciona en SQLite 3.14+. Usar `DELETE FROM messages_fts WHERE rowid=OLD.id` directamente en trigger `BEFORE DELETE`.
2. **Tags JSONField `__contains` con lista en SQLite:** No funciona. Usar raw `LIKE '%"tag"%'`.
3. **Parser de archivos con backticks literales:** Si el BACKLOG.md tiene `\`<agent>\`` en columna `assigned_agent`, hacer `.strip("`")` antes de pasar al orquestador.
4. **`UNIQUE (project_id, decision_id)` para ADRs:** Los ADRs son locales al proyecto, no globales. Migración aplicada manualmente en sesión.
5. **Astro `<script>` con TS inline:** Usar `// @ts-nocheck` para handlers de DOM (inferencia de tipos no soporta `dataset` en `HTMLElement`).
6. **`--strict-markers` requiere marker registrado:** `pytest.mark.django.db` falla si no esta en `pytest.ini` markers. Cambiar a `pytestmark = [pytest.mark.django.db]`.

### Skills que se hubieran podido reutilizar

- `seo-onpage-architecture` para meta tags (no usado en MVP, pero aplica para v2)
- `testing-tdd-architecture` para >80% coverage (objetivo ampliamente superado)
- `tailwind-architecture` para tokens (aplicado manualmente, sin skill)
- `astro-landing-kit` para componentes Astro base (no usado; la app es app, no landing)

### Recomendación para próximos proyectos

- Iniciar con `requirements_architect` → ADR-001 (stack) → `ux-ui_specialist` → ADR-002 (modelo) → `backend_specialist` → `frontend_worker` → `tester` → `qa_auditor` → `docs`.
- Este orden secuencial funcionó sin dependencias circulares ni STOP_LOSS.
- El parser del seed fue la pieza más compleja: 23 mensajes con 80+ emojis, 14 categorías inferidas, 100% idempotente en re-import.