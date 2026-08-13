# Instrucciones para Gemini 3.1 Pro — AIRON-Cast Documentación
**Lee primero:** `HANDOFF_CONTEXT.md` completo antes de continuar.

---

## Por qué tú

Gemini 3.1 Pro tiene acceso nativo al proyecto en Antigravity y capacidad de
leer los archivos ya existentes (AGENTS.md, manifest.json, rules/global.md)
directamente desde el editor. Tus instrucciones asumen que puedes leer esos
archivos antes de escribir. Tu asignación es todos los archivos Markdown.

**Antes de escribir cualquier archivo: abre y lee en Antigravity:**
- `AGENTS.md`
- `manifest.json`
- `rules/global.md`

Todo lo que generes debe ser consistente con esos tres documentos.

---

## Tu asignación: 15 archivos Markdown

### BLOQUE A — Agents (en este orden)

#### `agents/strategist.md`

**Rol:** Círculo 1 — Análisis y diseño. Primera instancia que toca cualquier
proyecto nuevo. Nunca ejecuta código, solo analiza y planifica.

**Contenido obligatorio:**
- Rol y misión del agente (2-3 líneas, sin fluff).
- Modelo asignado: (Sugerido por Estratega).
- Proceso paso a paso que sigue al recibir un nuevo proyecto:
  1. Lee `spec.md` si existe, o solicita al operador la descripción del proyecto.
  2. Consulta `context7` para verificar stack tecnológico apropiado.
  3. Consulta `notebooklm` para patrones de proyectos similares previos.
  4. Genera el blueprint: lista de tareas con agente asignado, prioridad y
     dependencias.
  5. Registra proyecto y tareas en la DB vía `memory_manager.py`.
  6. Escribe `output/[slug]/spec.md` con el blueprint aprobado.
  7. Levanta bandera "Blueprint listo" y cede al orchestrator.
- Criterios de calidad del blueprint (qué hace que sea aceptable).
- Condiciones para escalar a HITL.
- Lo que NO puede hacer (extraído directamente de manifest.json → strategist → forbidden).

---

#### `agents/orchestrator.md`

**Rol:** Círculo 2 — Control táctico. Mueve tareas entre estados y coordina
el taskforce. No ejecuta trabajo de desarrollo.

**Contenido obligatorio:**
- Rol y misión.
- Modelo asignado: (Sugerido por Estratega).
- Loop de orquestación (cómo decide qué agente activa en cada momento):
  1. Consulta `v_ready_tasks` para ver qué está disponible.
  2. Selecciona la tarea de mayor prioridad según el workflow activo.
  3. Verifica jurisdicción del agente en `manifest.json`.
  4. Activa el agente de taskforce correspondiente.
  5. Monitorea: cuando el agente termina, verifica output contra schema.
  6. Si OK: mueve tarea a COMPLETED, desbloquea dependientes, activa siguiente.
  7. Si FALLA: gestiona reintento (máx 3) o escala a HITL.
- Protocolo de handoff entre agentes (cómo le pasa el contexto al siguiente).
- Condiciones para escalar a HITL.
- Lo que NO puede hacer (de manifest.json → orchestrator → forbidden).

---

#### `agents/taskforce/frontend.md`

**Rol:** Desarrollo de interfaces. HTML, CSS, JS, frameworks frontend.

**Contenido obligatorio:**
- Rol y misión.
- Modelo asignado: (Sugerido por Estratega). Revisión final: (Sugerido por Estratega).
- Stack por defecto (proponer basado en el contexto del operador):
  - Para landing pages / corporativas: HTML5 + CSS3 + JS vanilla o Alpine.js
  - Para web apps: según spec del proyecto (preguntar al strategist)
- Proceso de trabajo paso a paso.
- Cuándo y cómo invocar `StitchMCP` (para generación de UI).
- Cuándo y cómo invocar `context7` (para documentación de frameworks).
- Cómo registrar cada artefacto generado (usando memory_manager).
- Criterios de "tarea completada" (qué debe cumplir el código para levantar
  bandera de finalización).
- Lo que NO puede hacer (de manifest.json → taskforce → frontend → forbidden).

---

#### `agents/taskforce/backend.md`

**Rol:** Lógica de servidor, APIs, modelos de datos, integraciones.

**Contenido obligatorio:**
- Rol y misión.
- Modelo asignado: (Sugerido por Estratega). Revisión: (Sugerido por Estratega).
- Stack por defecto del operador: Python + Django (Django 5 es el estándar
  confirmado en proyectos del operador).
- Proceso de trabajo paso a paso.
- Cuándo consultar `context7` (siempre antes de implementar un patrón
  nuevo de Django o librería externa).
- Manejo de variables de entorno (nunca credenciales en código fuente).
- Cómo registrar migraciones como artefactos.
- Criterios de "tarea completada".
- Lo que NO puede hacer (de manifest.json).

---

#### `agents/taskforce/ux.md`

**Rol:** Revisión de experiencia de usuario. No escribe código nuevo — revisa
y reporta sobre lo que frontend generó.

**Contenido obligatorio:**
- Rol y misión.
- Modelo asignado: (Sugerido por Estratega).
- Checklist de revisión UX que aplica a CADA entrega de frontend:
  (consistencia visual, flujos de navegación, mobile-first, accesibilidad básica,
  claridad de CTAs, tiempos de carga estimados, errores de formulario).
- Cómo genera el `ux_report` (schema en manifest.json).
- Criterio de severidad: cuándo un issue es `critical` (bloquea avance)
  vs `high/medium/low` (registra pero no bloquea).
- Cuándo usa `StitchMCP` (para proponer variantes visuales cuando sea necesario).
- Lo que NO puede hacer (de manifest.json).

---

#### `agents/taskforce/qa.md`

**Rol:** Validación técnica final. Último filtro antes de que un proyecto
se marque como entregable.

**Contenido obligatorio:**
- Rol y misión.
- Modelo asignado: (Sugerido por Estratega) (el único agente del taskforce con Sonnet).
- Proceso de verificación:
  1. Verificar checksum de TODOS los artefactos del proyecto.
  2. Revisar que `docs/` esté actualizada.
  3. Revisar código contra los criterios de calidad de `rules/global.md`.
  4. Generar `qa_report` (schema en manifest.json).
- Si `approved_for_delivery = false` con issues `critical`: STOP,
  devolver al agente responsable con descripción exacta del problema.
- Cuándo escala a HITL.
- Lo que NO puede hacer (de manifest.json).

---

#### `agents/taskforce/docs.md`

**Rol:** Documentación técnica y de usuario.

**Contenido obligatorio:**
- Rol y misión.
- Modelo asignado: (Sugerido por Estratega).
- Qué documenta por defecto en cada proyecto:
  - `README.md` del proyecto (instalación, uso, estructura).
  - `docs/frontend.md` (componentes y decisiones de UI).
  - `docs/backend.md` (API endpoints, modelos, decisiones de arquitectura).
  - `docs/qa-report.md` (consolidado de QA).
- Regla crítica: **nunca inventar comportamientos**. Solo documentar lo que
  existe y fue verificado.
- Cuándo consultar `notebooklm` (para patrones de documentación previos).
- Lo que NO puede hacer (de manifest.json).

---

### BLOQUE B — Skills (en este orden)

**Regla general de SKILL.md:** Un SKILL.md no describe qué es la herramienta
— describe exactamente cuándo y cómo el agente debe usarla. Sin eso, la skill
queda flotando sin activarse. Cada SKILL.md debe responder:
1. ¿Cuándo se activa? (condición explícita)
2. ¿Cómo se llama? (parámetros exactos o ejemplos)
3. ¿Qué se hace con el resultado?

---

#### `skills/memory/SKILL.md`

**Propósito:** Instrucciones para que el agente interactúe correctamente con
la capa de persistencia (memory_manager.py + state.json).

**Secciones obligatorias:**
- Cuándo leer el state.json (siempre al iniciar cualquier tarea).
- Cuándo escribir un checkpoint (siempre ANTES de ejecutar, no después).
- Cómo registrar un artefacto (método exacto de memory_manager).
- Cómo actualizar el estado de una tarea.
- Qué hacer si `memory_manager.py` lanza `MemoryManagerError`.

---

#### `skills/context7/SKILL.md`

**Propósito:** Cuándo y cómo consultar documentación técnica oficial via context7.

**Secciones obligatorias:**
- Condición de activación: "Antes de usar una librería o framework que no
  estás 100% seguro de su API actual" — ejemplos concretos.
- Cómo hacer la consulta (resolve-library-id primero, luego query-docs).
- Qué hacer con el resultado (integrarlo al contexto, no copiarlo al artefacto).
- Cuándo NO usar context7 (si ya tienes el contexto en el turno activo).

---

#### `skills/notebooklm/SKILL.md`

**Propósito:** Cuándo y cómo consultar la knowledge base del proyecto.

**MCPs disponibles a usar:**
  `notebook_list`, `notebook_get`, `notebook_query`, `notebook_add_text`

**Secciones obligatorias:**
- Consulta antes de iniciar: qué buscar en notebooklm al empezar un proyecto
  (patrones similares, decisiones previas, errores conocidos).
- Escritura de conocimiento nuevo: cuándo y qué guardar
  (solo decisiones confirmadas, soluciones a problemas no triviales).
- Cuándo NO guardar (no guardar output de cada tarea rutinaria — solo
  conocimiento reutilizable).
- Formato de lo que se guarda (título descriptivo + contexto + decisión tomada).

---

#### `skills/ghl/SKILL.md`

**Propósito:** Operaciones en GoHighLevel vía la skill existente del operador.

**Contexto:** El operador ya tiene una skill de GHL funcionando que hace
consultas a su subcuenta. Esta SKILL.md coordina cuándo usarla dentro de
workflows de AIRON-Cast.

**Secciones obligatorias:**
- Cuándo activar la skill GHL (solo en workflows `/ghl-admin`, `/ghl-bot`,
  `/ghl-snapshot` — nunca en workflows de desarrollo web o backend genérico).
- Qué tipo de consultas puede hacer (solo lectura de datos para contexto,
  no modificar la cuenta directamente sin RFC aprobado).
- Cómo integrar los datos retornados al contexto del agente.
- Escalación obligatoria a HITL si la skill retorna error de autenticación.

---

### BLOQUE C — Workflows (en este orden)
**Para cada workflow, el formato es idéntico:**

```markdown
# Workflow: [nombre]
## Objetivo
## Modelos por fase
## Agentes y orden de ejecución
## Paso a paso del flujo
## Criterios de completado
## Artefactos esperados en output/
## Condiciones de pausa / HITL
```

---

#### `workflows/web-design.md`
Páginas corporativas y landing pages. Agentes: strategist → frontend → ux → docs → qa.

#### `workflows/web-app.md`
Aplicaciones web responsive. Agentes: strategist → backend → frontend → ux → qa → docs.

#### `workflows/ghl-admin.md`
Workflows de marketing, citas, reportes en GHL. Agentes: strategist → (agente
especializado GHL, que usa skill/ghl) → docs → qa.

#### `workflows/ghl-bot.md`
Bots Conversation IA y Voz IA. Incluye: generación de prompt del bot
(9 secciones estándar del operador: Contexto, Rol, Objetivos, Técnicas,
Cartera, Restricciones, Acciones Obligatorias, Diagrama, Ejemplos) y
configuración de base de conocimientos en GHL.
Agentes: strategist → (redactor de prompts) → qa.

#### `workflows/ghl-snapshot.md`
Diseño de snapshots para nichos específicos. Agentes: strategist → frontend
(para assets) → (configurador GHL) → docs → qa.

#### `workflows/erp-pos.md`
Módulos ERP-POS Core (Django 5 + PostgreSQL 16 + Astro 4, para SMBs venezolanos).
Agentes: strategist → backend → frontend → ux → qa → docs.

#### `workflows/custom.md`
Soluciones personalizadas. Workflow genérico adaptable. El strategist define
los agentes necesarios en el blueprint inicial.

#### `workflows/system.md`
Workflow interno de AIRON-Cast (mantenimiento del propio framework,
actualización de skills, incorporación de nuevos agentes).

---

## Reglas de entrega para Gemini

- Lee los archivos existentes en Antigravity antes de escribir. No asumir.
- Todos los archivos en español. Términos técnicos en inglés donde corresponda.
- Tono técnico, directo. Sin introductorias tipo "Este agente es responsable de...
  En este documento encontrarás..." — ir directo al contenido.
- Extensión apropiada: agents entre 60-120 líneas, skills 30-60 líneas,
  workflows 40-80 líneas. Nada más, nada menos.
- Los workflows deben ser ejecutables, no decorativos — el agente debe poder
  leer el workflow y saber exactamente qué hacer en cada paso.

## Formato de entrega

Un archivo por respuesta, con su ruta completa como encabezado:
```
### agents/strategist.md
[contenido]
```

No entregar todos en una sola respuesta — entregar de a 2-3 archivos para
mantener calidad sobre cantidad.
