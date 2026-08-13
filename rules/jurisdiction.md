# Jurisdiction Matrix — AIRON‑Cast RBAC

> **Propósito:** Definir los límites exactos de lectura y escritura para cada agente del ecosistema.  
> **Aplicación:** El orquestador verifica esta matriz antes de delegar cualquier tarea.  
> **Jerarquía:** Se alinea con `AGENTS.md`, `ceo.md` y los frontmatter de cada perfil.

---

## 1. Niveles de Scope

| Scope | Significado | Agentes asignados |
|-------|-------------|-------------------|
| `restricted` | Solo acceso al workspace del proyecto activo (`workspace/<slug>/`) | `requirements_architect`, `ux-ui_specialist`, `frontend_worker`, `backend_specialist` |
| `elevated` | Acceso a `core/` y `tools/` para tareas de infraestructura | `orchestrator`, `qa_auditor`, `meta_factory` |
| `unrestricted` | Sin restricciones | Solo el Operador |

---

## 2. Matriz de Acceso por Agente

### 2.1 `requirements_architect` (scope: restricted)

| Recurso | Lectura | Escritura | Notas |
|---------|---------|-----------|-------|
| `workspace/<slug>/` | ✅ | ✅ | Puede crear `REQUIREMENTS.md`, `BACKLOG.md` |
| `workspace/<slug>/src/` | ❌ | ❌ | No escribe código fuente |
| `.agents/profiles/` | ✅ | ❌ | Consulta capacidades de otros agentes |
| `core/memory_manager.py` | ✅ (vía API) | ✅ (vía API) | Registra ADRs y tareas |
| `tools/` | ❌ | ❌ | No invoca herramientas CLI |
| `central_intelligence.db` | ❌ (directo) | ❌ (directo) | Solo vía memory_manager |
| `rules/` | ✅ | ❌ | Lectura de referencia |

### 2.2 `ux-ui_specialist` (scope: restricted)

| Recurso | Lectura | Escritura | Notas |
|---------|---------|-----------|-------|
| `workspace/<slug>/` | ✅ | ✅ | `REQUIREMENTS.md`, `design-tokens.json` |
| `workspace/<slug>/src/styles/` | ❌ | ✅ | Solo tokens y specs, no código final |
| `workspace/<slug>/src/components/` | ❌ | ❌ | No escribe componentes |
| `.agents/skills/a2lt-brand-kit/` | ✅ | ❌ | Consulta assets de marca |
| `core/memory_manager.py` | ✅ (vía API) | ✅ (vía API) | Registra ADRs visuales |

### 2.3 `frontend_worker` (scope: restricted)

| Recurso | Lectura | Escritura | Notas |
|---------|---------|-----------|-------|
| `workspace/<slug>/` | ✅ | ❌ | Solo lectura de specs |
| `workspace/<slug>/src/` | ✅ | ✅ | Código Astro, CSS, componentes |
| `.agents/skills/tailwind-architecture/` | ✅ | ❌ | Consulta patrones |
| `.agents/profiles/ux-ui_specialist.md` | ✅ | ❌ | Lee design tokens y specs |
| `core/memory_manager.py` | ✅ (vía API) | ✅ (vía API) | Registra artefactos |
| `tools/` | ❌ | ❌ | No invoca herramientas |

### 2.4 `qa_auditor` (scope: elevated)

| Recurso | Lectura | Escritura | Notas |
|---------|---------|-----------|-------|
| `workspace/<slug>/src/` | ✅ | ❌ | Solo lectura para revisión |
| `workspace/<slug>/reports/` | ✅ | ✅ | Genera `qa_report.md` |
| `core/memory_manager.py` | ✅ (vía API) | ✅ (vía API) | Verifica checksums, registra hallazgos |
| `tools/` | ✅ | ✅ | Ejecuta Playwright, linters |
| `central_intelligence.db` | ✅ (vía API) | ✅ (vía API) | Consulta `execution_logs` y `artifacts` |

### 2.5 `orchestrator` (scope: elevated)

| Recurso | Lectura | Escritura | Notas |
|---------|---------|-----------|-------|
| `workspace/<slug>/` | ✅ | ✅ | `MISSION_CONTROL.md`, `state.json` |
| `workspace/<slug>/src/` | ✅ | ❌ | Supervisa pero no modifica código |
| `core/` (todos los scripts) | ✅ | ✅ | Motor del ecosistema |
| `tools/` | ✅ | ✅ | Invoca herramientas CLI |
| `central_intelligence.db` | ✅ (vía API) | ✅ (vía API) | Gestiona tareas, checkpoints, logs |
| `.agents/profiles/` | ✅ | ❌ | Carga perfiles para verificar jurisdicción |
| `.agents/rules/` | ✅ | ✅ | Aplica reglas de gobernanza |

### 2.6 `meta_factory` (scope: elevated)

| Recurso | Lectura | Escritura | Notas |
|---------|---------|-----------|-------|
| `.agents/profiles/` | ✅ | ✅ | Parchea perfiles con feedback recurrente |
| `.agents/skills/` | ✅ | ✅ | Crea, versiona y archiva skills |
| `core/memory_manager.py` | ✅ (vía API) | ✅ (vía API) | Monitorea `feedback_history` |
| `workspace/<slug>/` | ✅ | ❌ | Solo lectura de patrones |
| `tools/` | ✅ | ✅ | Scripts de validación y empaquetado |

### 2.7 `backend_specialist` (scope: restricted) — Fase 2

| Recurso | Lectura | Escritura | Notas |
|---------|---------|-----------|-------|
| `workspace/<slug>/src/api/` | ✅ | ✅ | APIs, modelos, migraciones |
| `workspace/<slug>/src/` (resto) | ❌ | ❌ | No invade territorio frontend |
| `core/memory_manager.py` | ✅ (vía API) | ✅ (vía API) | Registra artefactos |

---

## 3. Reglas de Herencia de Skills

- Un agente **hereda las skills** de los perfiles que lista en su frontmatter (`assigned_agents`).
- El orquestador valida que la skill requerida esté en el perfil del agente o en alguno de sus ascendentes.
- Las skills heredadas no otorgan permisos de escritura adicionales; la jurisdicción del agente prevalece.

---

## 4. Protocolo Anti‑Huérfanos

- **Frontmatter obligatorio** en todo `SKILL.md`: `assigned_agents: [@role]`, `last_used: YYYY-MM-DD`.
- **Auditoría semanal:** el orquestador ejecuta `python tools/db_ops.py check_orphans --days 14`.
- **Archivado:** skills sin uso en 14 días → `skills/archived/`. Restauración solo vía `meta_factory restore`.

---

## 5. Monitoreo de Cumplimiento

El orquestador verifica esta matriz antes de cada delegación:

1. Cargar el perfil del agente desde `.agents/profiles/<role>.md`.
2. Leer `scope` del frontmatter.
3. Validar que la tarea asignada está dentro de los permisos de escritura del agente.
4. Si hay violación → STOP_LOSS (condición S3 de `ceo.md` §6).