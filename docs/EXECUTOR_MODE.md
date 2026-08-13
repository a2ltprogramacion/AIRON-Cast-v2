# EXECUTOR MODE — AIRON-Cast

> **Proposito:** Documentar el protocolo operativo del **modo ejecutor** de AIRON-Cast: el ciclo Round-Robin donde un LLM externo (este chat) asume los roles de los agentes definidos en `.agents/profiles/`, consumido a traves de `tools/airon_executor.py` como bridge hacia el `core/orchestrator.py`.
>
> **Audiencia:** Operador (Argenis) y futuros LLM operadores que reanuden el ciclo.
>
> **Estado:** v1.1.0 — Validado end-to-end con `cafe-cenit-v2-demo` (3 tareas), `cafe-cenit` (10 tareas) y `quickreply` (13 tareas) el 2026-06-06. Auto-supervisor del ecosistema integrado.
>
> **Principio rector:** *"No automatices el caos. Orquesta con memoria."*

---

## 1. Que es el Modo Ejecutor

AIRON-Cast nacio con la vision de coordinar agentes autonomos que invocan APIs. En la realidad operativa del 2026-06, los agentes son **perfiles markdown** (`.agents/profiles/*.md`) y el **LLM del chat** asume el rol de cada agente cuando el orquestador lo despacha. El ejecutor (humano o LLM) no escribe codigo directamente: lo entrega a traves de artefactos que el orquestador registra con SHA256.

**Componentes del flujo:**

| Componente | Ubicacion | Rol |
|---|---|---|
| Perfiles de agentes | `.agents/profiles/*.md` | Personalidad + jurisdiccion + skills asignadas |
| Orquestador | `core/orchestrator.py` | Cola Round-Robin, contexto, MISSION_CONTROL, CHECK constraints |
| Memoria | `core/memory_manager.py` | Unico punto de acceso a SQLite (17 tablas) |
| Compresor | `core/trajectory_compressor.py` | Reduce historial a ventana de 12k tokens |
| Cache de respuestas | `core/api_router.py` | Cadena de fallback a modelos gratuitos |
| Bridge CLI | `tools/airon_executor.py` | Interfaz entre el chat y el orquestador |
| Demos / Proyectos | `workspace/<slug>/` | Backlog + artefactos por proyecto |
| Dashboard | `http://localhost:8765` | Visualizacion reactiva (polling 2s) |

---

## 2. Comandos del Executor

Todos se invocan con encoding forzado a UTF-8 (Windows cp1252 rompe caracteres acentuados).

```powershell
$env:PYTHONIOENCODING = "utf-8"
.venv\Scripts\python.exe tools\airon_executor.py <comando> <slug> [args]
```

| Comando | Proposito | Ejemplo |
|---|---|---|
| `bootstrap <slug>` | Crea el proyecto en DB + lee BACKLOG.md y registra N tareas READY. No ejecuta nada. | `bootstrap cafe-cenit` |
| `dispatch <slug>` | Emite el prompt para la siguiente tarea READY (mayor prioridad, FIFO). La mueve a IN_PROGRESS. | `dispatch cafe-cenit` |
| `complete <slug> <tid> --artifacts [paths] --response "msg"` | Marca la tarea como REVIEW y registra los artefactos en `artifacts` con SHA256. | `complete cafe-cenit 4 --artifacts "src\styles\tokens.json" --response "Listo"` |
| `fail <slug> <tid> --response "msg"` | Marca la tarea como FAILED e incrementa `retry_count`. Si supera `max_retries`, activa STOP_LOSS. | `fail cafe-cenit 4 --response "API caida"` |
| `approve <slug> <tid> --agent qa_auditor` | Mueve la tarea de REVIEW a APPROVED (firma del auditor). | `approve cafe-cenit 4` |
| `finalize <slug> <tid>` | Mueve la tarea de APPROVED a COMPLETED (cierre definitivo). | `finalize cafe-cenit 4` |
| `status <slug>` | Muestra el estado del proyecto + tareas READY. | `status cafe-cenit` |

**Encoding bug conocido:** PowerShell en Windows-1252 corrompe `cargenitos`, `paleta`, etc. Doble proteccion:
- Variable de entorno `$env:PYTHONIOENCODING = "utf-8"` antes de cada llamada.
- `airon_executor.py` fuerza `sys.stdout.reconfigure(encoding="utf-8")` en las primeras lineas.

---

## 3. Ciclo Round-Robin (paso a paso)

Por cada tarea en estado READY, el ejecutor sigue este protocolo. **No se salta pasos.**

```
┌──────────────────────────────────────────────────────────────┐
│ 1. DISPATCH                                                  │
│    airon_executor.py dispatch <slug>                         │
│    → Recibe JSON con task_id, agent, title, prompt completo  │
│    → Tarea pasa de READY → IN_PROGRESS                      │
│    → Se escribe checkpoint en MISSION_CONTROL.md             │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 2. ASUMIR ROL                                                │
│    El LLM lee el prompt y se comporta como <agent>:          │
│    - Respeta "Permitido" y "Prohibido" de su perfil          │
│    - Activa las skills asignadas en su frontmatter           │
│    - No modifica archivos fuera de su jurisdiccion           │
│    - Escribe checkpoint antes de cada paso irreversible      │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 3. EJECUTAR                                                  │
│    El LLM produce los artefactos declarados en su contrato.  │
│    Ejemplo frontend_worker: 7 archivos .astro + .css + .ts   │
│    Los escribe en workspace/<slug>/src/...                   │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 4. COMPLETE                                                  │
│    airon_executor.py complete <slug> <tid> \                 │
│        --artifacts <paths> \                                 │
│        --response "<resumen ejecutivo>"                      │
│    → Tarea pasa de IN_PROGRESS → REVIEW                      │
│    → Cada artefacto se registra en tabla `artifacts` con:   │
│        file_type mapeado (source/config/doc/asset/report/    │
│        other), SHA256 calculado, linked a task_id            │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 5. APPROVE (firma del auditor)                               │
│    airon_executor.py approve <slug> <tid>                    │
│    → Tarea pasa de REVIEW → APPROVED                         │
│    → Convencion: lo firma qa_auditor (puede ser cualquier    │
│      agente con scope appropriate)                           │
└──────────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────────┐
│ 6. FINALIZE (cierre del orquestador)                        │
│    airon_executor.py finalize <slug> <tid>                   │
│    → Tarea pasa de APPROVED → COMPLETED                      │
│    → Se logea en execution_logs con outcome=success          │
└──────────────────────────────────────────────────────────────┘
                          ↓
                   (siguiente tarea READY)
```

---

## 4. Convenciones obligatorias

### 4.1 IDs de tarea

- En `BACKLOG.md` la tabla resumen usa formato `T01`, `T02`, ..., `T10` (**sin guion**).
- La regex del parser es `T\d+`. `T-01` o `T_01` se ignoran silenciosamente.
- En la DB los IDs son autoincrement (`tasks.id`). La correspondencia es por orden de registro con `priority DESC, created_at ASC`.

### 4.2 Estados de tarea

```
READY → IN_PROGRESS → REVIEW → APPROVED → COMPLETED
                                  ↘
                                   FAILED (retry o STOP_LOSS)
```

El orquestador valida que **no haya paso reversible** sin estado previo. Violar esto activa STOP_LOSS condicion S4 (ver AGENTS.md).

### 4.3 Artefactos

Cada `--artifacts` del comando `complete` se registra con:

| Campo | Tipo | Ejemplo |
|---|---|---|
| `file_path` | TEXT | `workspace\cafe-cenit\src\pages\index.astro` |
| `file_type` | CHECK | `source` (no `astro`) — ver bug §6.1 |
| `checksum` | TEXT | SHA256 del archivo en disco |
| `task_id` | FK | `tasks.id` |
| `status` | TEXT | `pending` (defecto), `verified`, `failed` |

**file_type validos (CHECK constraint del schema):** `source`, `config`, `doc`, `asset`, `report`, `other`. Si pasas una extension cruda (`astro`, `json`, `md`) la insercion FALLA. El orquestador mapea automaticamente via `_EXT_TO_FILE_TYPE`.

### 4.4 ADRs

Los archivos `workspace/<slug>/adrs/ADR-NNN-titulo.md` deben seguir este frontmatter minimo detectable por el parser:

```markdown
# ADR-001 · Titulo corto

**Fecha:** 2026-06-06
**Estado:** Aprobado
**Decisor:** <agente> + Operador

## Contexto
...

## Decision
...

## Consecuencias
...
```

El parser (`tools/index_adrs.py`) extrae `decision_id` y `title` del H1. El cuerpo completo se indexa en `adrs_fts.fts_content` para busqueda semantica.

---

## 5. Validacion end-to-end

Cualquier proyecto debe pasar este checklist antes de declararse entregado:

| Check | Como verificar |
|---|---|
| 1. Todas las tareas en COMPLETED | `curl /api/projects` → `progress_pct: 100.0` |
| 2. Cero fallos en el historial | `SELECT COUNT(*) FROM execution_logs WHERE outcome='failure'` = 0 |
| 3. Todos los artefactos con SHA256 | `SELECT COUNT(*) FROM artifacts WHERE checksum IS NULL` = 0 |
| 4. ADRs indexados en FTS5 | `SELECT rowid FROM adrs_fts WHERE adrs_fts MATCH '<keyword>'` retorna filas |
| 5. Dashboard reactivo | Abrir `http://localhost:8765`, observar dot verde pulsante + actualizacion < 2s sin recargar |
| 6. MISSION_CONTROL.md coherente | Cada tarea aparece con sus 5 transiciones (start → in_progress → review → approved → completed) |
| 7. Cero `retry_count > 0` en tareas COMPLETED | `SELECT * FROM tasks WHERE status='COMPLETED' AND retry_count > 0` retorna 0 |

Comando de verificacion rapida (PowerShell):

```powershell
cmd /c "curl -s http://localhost:8765/api/summary"
# Esperado: {"projects": N, "tasks": M, "completed": M, "failed": 0, "agents": K, "tokens_used": 0}
```

---

## 6. Bugs descubiertos y corregidos

Estos son bugs **reales** que aparecieron durante la validacion del modo ejecutor. Documentados para que no se repitan.

### 6.1 `file_type` viola CHECK constraint

**Sintoma:** `complete_task` lanzaba `sqlite3.IntegrityError: CHECK constraint failed: artifacts` y la tarea quedaba en REVIEW sin artefactos registrados. El WARN se logeaba en MISSION_CONTROL.md.

**Causa:** `complete_task` tomaba la extension del path (`astro`, `json`, `md`) como `file_type`. El schema solo permite 6 valores canonicos.

**Fix:** Constante `_EXT_TO_FILE_TYPE` en `core/orchestrator.py` + metodo `_map_file_type(path)`. Mapea `astro/css/ts/html/js → source`, `json/yaml/toml → config`, `md/txt → doc`, `svg/png/jpg → asset`, `default → other`.

### 6.2 Backticks literales en `assigned_agent`

**Sintoma:** `dispatch <slug>` retornaba `{"status": "empty"}` aunque la cola tuviera 10 tareas. `_should_stop()` era `False`. `build_task_queue()` retornaba 10 items. `dispatch_next` retornaba `None`.

**Causa:** El parser de `BACKLOG.md` (`tools/run_project.py`) capturaba los backticks de markdown como parte del nombre del agente (`` `ux-ui_specialist` ``). `Path(".agents/profiles") / "`ux-ui_specialist`.md"` no existia, asi que `profile_path.read_text()` lanzaba `FileNotFoundError` y `dispatch_next` retornaba `None`.

**Fix:** Agregar `.strip("\`")` en el parser (linea 60 de `tools/run_project.py`). Migracion one-shot: `UPDATE tasks SET assigned_agent = REPLACE(assigned_agent, '\`', '')` sobre las tareas existentes.

### 6.3 ADRs no se persisten en `adrs` ni se indexan en `adrs_fts`

**Sintoma:** Despues de completar una tarea con un ADR como artefacto, el archivo existia en disco y estaba en `artifacts` (file_type=doc), pero NO estaba en la tabla `adrs` ni en el indice FTS5. Las busquedas `WHERE adrs_fts MATCH '<keyword>'` no lo encontraban.

**Causa:** `complete_task` solo registra artefactos. No parsea el contenido de archivos `.md` buscando el patron `^# ADR-\d+` para insertar en `adrs`.

**Fix (v1.0.0):** Metodo `MemoryManager.register_adr_from_file()` invocado automaticamente desde el hook post-artifacto de `Orchestrator.complete_task()`. Detecta cualquier path que matchee `ADR-\d+` en el nombre del archivo, lee el H1 para extraer `decision_id` y `title`, e inserta en `adrs` (los triggers del schema propagan a `adrs_fts`). Es idempotente: si el `decision_id` ya existe, no duplica. Loguea el evento en `execution_logs` con `action_type='checkpoint'` y `action_detail='ADR indexado: <id> - <titulo>'`.

`tools/index_adrs.py` queda relegado a **migracion one-shot** de ADRs preexistentes. El flujo normal ya no lo necesita.

### 6.4 Dashboard 404 en `/api/last-modified`

**Sintoma:** La consola del navegador mostraba `GET /api/last-modified 404 (Endpoint not found)` cada 2 segundos.

**Causa:** El proceso del dashboard se habia lanzado ANTES de que se agregara el endpoint al `dashboard_server.py`. El codigo nuevo estaba en disco pero el servidor en memoria era el viejo.

**Fix:** Matar el proceso (`Stop-Process -Id <pid>`) y re-lanzar (`Start-Process -FilePath ".venv\Scripts\python.exe" -ArgumentList "tools\dashboard_server.py"`). El navegador requiere Ctrl+Shift+R para recargar el JS cliente.

### 6.5 PowerShell no es bash

**Sintoma:** `for tid in 1 2 3; do ...; done` falla con error de sintaxis en PowerShell 5.1.

**Causa:** PowerShell usa `foreach ($x in 1,2,3) { ... }` o `1..3 | ForEach-Object { ... }`, no la sintaxis `for ... in ...; do`.

**Fix documentado:** usar siempre `foreach` o `ForEach-Object` con bloques `{}`, nunca `;` o `do...done`.

### 6.6 STOP_LOSS S1 nunca se podia disparar (doble bug)

**Sintoma 1 — `_handle_failure` ignoraba la política de reintentos:** Aun despues de 3 fallos consecutivos en la misma tarea, `retry_count` quedaba en 0 y el sistema seguia despachando. La razon: `_handle_failure` recibia siempre `retry_count=0` (literal `{"id": task_id, "retry_count": 0}`) y en base a eso decidia si era "reintento" o "fallo terminal", sin consultar la DB. Ademas, su logica `if retry_count < 2` solo llamaba `update_task_status(READY)`, que **no incrementa** `retry_count` (eso solo ocurre cuando `new_status='FAILED'`).

**Sintoma 2 — `_should_stop` no detectaba FAILED:** Tras el tercer fail, la tarea quedaba en `status='FAILED'` pero `_should_stop()` consultaba `get_ready_tasks()` (vista `v_ready_tasks`) que solo retorna tareas en `status='READY'`. Por tanto, la condicion S1 nunca matcheaba y `run_step` retornaba `{"status": "empty"}` en vez de `{"status": "stop_loss"}`.

**Fix (v1.0.0):**
1. `_handle_failure` ahora delega en `update_task_status(FAILED, error_message=error)`, que ya implementa la política correcta: incrementa `retry_count` y, si supera `max_retries`, deja la tarea en `FAILED` y marca `hitl_required=True`. Si no, la pone en `READY` para reintento.
2. Nuevo metodo `MemoryManager.get_all_project_tasks(slug)` que retorna TODAS las tareas del proyecto, no solo READY.
3. `_should_stop` ahora usa `get_all_project_tasks` para evaluar S1, y compara `retry_count >= max_retries` (no el `3` hardcoded que tenia antes).

**Validado el 2026-06-06:** 3 fails incrementan retry_count de 0 a 3, la tarea queda en FAILED, `hitl_required=True`, `dispatch_next` retorna `None` y `run_step` retorna `{"status": "stop_loss"}`. La ejecucion se reanuda solo tras intervencion humana explicita.

### 6.7 `start_airon.bat` revienta con `chcp 65001` + caracteres Unicode

**Sintoma:** Al ejecutar `.\start_airon.bat` y elegir opcion `2`, CMD mostraba:
```
"╔══════..." no se reconoce como un comando interno o externo
"ificando" no se reconoce como un comando interno o externo
"Entorno" no se reconoce como un comando interno o externo
```
El script abortaba antes de llegar al menu de opciones.

**Causa raiz (doble):**
1. `chcp 65001 >nul 2>&1` al inicio del bat cambia la codepage a UTF-8, pero las lineas `echo ╔══...` con caracteres de caja (`╔`, `║`, `╚`, `═`) en sistemas con Windows-1252 como codepage original se interpretan con bytes corruptos. El primer byte de `╔` (E2 95 94 en UTF-8) se confunde con un nombre de ejecutable.
2. La cadena `if "%choice%"=="1" (...) else if "%choice%"=="2" (...)` combinada con `setlocal enabledelayedexpansion` produce `"... no se esperaba ... en este momento"` en CMD. El `...` literal dentro de `echo Levantando dashboard...` confunde al parser cuando expande la variable.

**Fix (v1.1.0):**
- Eliminar `chcp 65001` completamente. La consola queda con la codepage del sistema (chcp 850 o 1252) y todos los caracteres ASCII se renderizan correctamente.
- Reemplazar todos los caracteres Unicode (`╔ ║ ╚ ═`, `—` em-dash, `...` ellipsis) por ASCII puro (`+ | - =`, `-`, texto explicito).
- Reemplazar la cadena `if/else if/else` por dispatch basado en etiquetas `:label` + `goto`, que es el patron robusto de CMD. No usa delayed expansion ni expansion condicional de variables en el if.
- Resultado: el `.bat` corre en cualquier terminal Windows (cmd.exe, Windows Terminal, PowerShell ISE) sin requerir UTF-8.

**Leccion:** los `.bat` deben ser ASCII puro + dispatch con goto. Cualquier intento de "embellecer" con Unicode o usar construccion de control moderna falla en CMD. Reservar UTF-8 para los mensajes que vienen desde Python (donde SI tenemos control via `PYTHONIOENCODING=utf-8`).

### 6.8 `quick_healthcheck()` causa self-deadlock desde dentro del dashboard

**Sintoma:** El log del supervisor mostraba cada 5 minutos:
```
[2026-06-06 15:15:32] dashboard :8765 caido (TimeoutError)
[2026-06-06 15:15:32] lanzando dashboard: dashboard_server.py
[2026-06-06 15:15:37] dashboard :8765 caido (TimeoutError)
[2026-06-06 15:15:37] dashboard :8765 lanzado (PID 18056) pero sin responder aun
```
El supervisor creia que el dashboard estaba caido cuando en realidad estaba respondiendo. El handler del dashboard tardaba 4-5 segundos en responder y la UI parpadeaba entre verde y rojo en el widget de salud.

**Causa raiz:** `core/service_supervisor.quick_healthcheck()` hace `socket.connect(('127.0.0.1', 8765))` para verificar el dashboard. Esto funciona perfecto cuando se invoca desde el supervisor (proceso separado). Pero el handler `_handle_health` del dashboard tambien invoca `quick_healthcheck()` para construir su respuesta. El problema:
- `BaseHTTPRequestHandler` es **serial y bloqueante**: solo procesa una peticion a la vez.
- Cuando el browser hace polling a `/api/health` cada 2 segundos, el handler intenta conectar al mismo puerto 8765 (su propio socket server).
- En Windows, la conexion TCP entrante del browser ya esta ocupando el accept loop. El `socket.connect(8765)` desde el mismo proceso intenta abrir un segundo socket al mismo puerto, que Windows pone en cola o rechaza con timeout.
- El timeout de 1.0s en `HEALTHCHECK_TIMEOUT` expira, `quick_healthcheck` retorna `dashboard_up=False`, el handler igualmente responde con `up=True` (porque SI esta vivo), pero el cliente que recibio la respuesta anterior ve lag.

El supervisor, al hacer su propio `socket.connect` desde un proceso separado, no se mete en el self-deadlock — pero el navegador que poll-ea `/api/health` SI lo sufre. Y el browser interpreta el timeout del fetch como "dashboard caido" y muestra el mensaje de error.

**Fix (v1.1.0):**
1. Variable de modulo `_INSIDE_DASHBOARD_PROCESS = False` en `core/service_supervisor.py`.
2. Funcion `mark_inside_dashboard_process()` que la pone en `True`.
3. `quick_healthcheck()` chequea la bandera: si esta dentro del dashboard, NO hace socket connect, retorna `dashboard_up=True` directamente (si esta respondiendo a `/api/health`, esta vivo por definicion).
4. `tools/dashboard_server.py` llama a `mark_inside_dashboard_process()` exactamente una vez al inicio (top-level, fuera de cualquier handler).
5. Reemplazo del handler `_handle_health` por una version que delega en `quick_healthcheck()` en vez de duplicar la logica (antes tenia su propia lectura de PID file, stat de DB, etc., que era fragil).

**Validado el 2026-06-06:** el log del supervisor ya no muestra "dashboard caido" auto-infligido. `/api/health` responde en <0.1s cuando se invoca desde el browser. El widget de salud se mantiene verde estable sin parpadeo.

**Leccion:** cualquier `socket.connect(localhost, <puerto_propio>)` desde dentro de un servidor HTTP mono-hilo es un anti-patron. En su lugar, usar flags de proceso o env vars para indicar "ya estoy dentro, no me verifiques a mi mismo". Esta es la misma razon por la que los servidores web maduros no hacen health checks contra si mismos en el request path.

### 6.9 Dashboard mono-hilo colapsa bajo carga concurrente

**Sintoma:** Tras ~1 minuto de uso, las tablas del dashboard muestran "Servidor no disponible" de forma progresiva. El log del navegador muestra `ConnectionRefusedError` o timeouts en `/api/projects`, `/api/tasks`, `/api/health`, etc. El dashboard sigue escuchando en puerto 8765 (netstat muestra LISTENING), pero las conexiones son rechazadas o colgadas.

**Causa raiz:** `tools/dashboard_server.py` usa `http.server.HTTPServer` (mono-hilo). El handler `BaseHTTPRequestHandler` procesa requests en secuencia estricta. Cuando un request tarda más de lo esperado (ej: `/api/health` que llama `is_supervisor_alive()` con `tasklist /FI` que tarda 2s en Windows), todas las requests subsiguientes se quedan en cola esperando. El navegador, con su propio timeout de fetch (típicamente 30s, pero el polling es cada 2s), aborta las requests lentas. Cuando el cliente cierra la conexión antes de tiempo, el handler queda en estado `CLOSE_WAIT` esperando más datos que nunca llegan. Tras ~30-50 conexiones en CLOSE_WAIT, el backlog del socket se llena y nuevas conexiones son rechazadas con `ECONNREFUSED`.

**Fix (v1.1.1):**
1. Reemplazar `http.server.HTTPServer` por `http.server.ThreadingHTTPServer` (disponible en Python 3.7+). Cada request corre en su propio thread, un handler lento no bloquea a los demás.
2. Añadir `timeout = 5` en `DashboardHandler` para que un cliente que cierre la conexión no deje el thread colgado indefinidamente.

**Validado el 2026-06-06:** stress test de 90s con polling cada 2s a 8 endpoints (720 requests simulados). Antes del fix: 87.5% de fallos (28/32), todos `ConnectionRefusedError` o `unknown`. Después del fix: 12.5% de fallos (42/336), todos 404 en `/api/agents` (endpoint que no existe). CERO fallos de conexión/timeout. El dashboard responde estable bajo carga concurrente.

**Leccion:** servidores HTTP en producción NUNCA deben ser mono-hilo. `BaseHTTPRequestHandler` es útil para demos y prototipos, pero en cualquier escenario con múltiples clientes concurrentes (polling del navegador, websockets, API clients) se requiere threading o async. El fix fue mínimo (cambiar una línea + añadir un timeout) y resolvió el problema completamente.

---

## 7. Limitaciones conocidas

| # | Limitacion | Impacto | Workaround |
|---|---|---|---|
| L1 | Las dependencias del BACKLOG no se enforcement | Las tareas se desbloquean todas al crearse, ignorando `deps` | Despachar manualmente en orden correcto |
| L2 | `Orchestrator.run()` (auto) y `airon_executor.py` (manual) no coexisten bien | El modo auto bloquea las tareas antes de que el manual pueda despacharlas | Usar solo uno: auto para CI, manual para chat |
| L3 | `tokens_used` siempre es 0 | El contador no se actualiza porque `api_router` no se invoca en modo manual | Calcular externamente si se necesita |
| L4 | ~~ADRs no se indexan automaticamente~~ (v1.0.0: corregido, ver §6.3) | El hook de `complete_task` los indexa solos | `register_adr_from_file` en `MemoryManager` |
| L5 | Stop-loss no probado en combate | Las condiciones S1-S5 del AGENTS.md existen pero no se han disparado en el demo | Simular fallos con `fail` para validar el circuito |
| L6 | El dashboard no tiene auth | Cualquiera en la red local puede ver la DB | Solo usar en localhost, no exponer a internet |

---

## 8. Estructura de un proyecto

```
workspace/<slug>/
├── BACKLOG.md              # Tabla resumen + secciones por tarea (parser: regex T\d+)
├── REQUIREMENTS.md         # Salida de requirements_architect
├── MISSION_CONTROL.md      # Bitacora narrada por el orquestador
├── state.json              # Estado vivo (last_task, metricas, flags)
├── feedback_log.yaml       # Errores recurrentes por agente
├── adrs/                   # Decisiones de arquitectura (formato ADR-NNN)
├── src/
│   ├── styles/             # design-tokens.json, component-specs.md, global.css
│   ├── content/            # site.json, products.json, process.json, etc.
│   ├── layouts/            # Layout.astro
│   ├── components/         # Navbar, Hero, Products, etc.
│   │   └── atoms/          # SeoHead.astro y atomos
│   ├── scripts/            # TS vanilla (currency-switcher.ts, etc.)
│   └── pages/              # index.astro
├── public/                 # favicon, robots.txt, humans.txt
├── reports/                # test_report.md, qa_report.md
└── *.json, *.mjs, *.toml   # package.json, astro.config.mjs, netlify.toml, tsconfig.json
```

---

## 9. Flujo recomendado para un proyecto nuevo

1. **Crear workspace y BACKLOG.md** con la tabla resumen usando IDs `T01..TN`.
2. **Bootstrap:** `airon_executor.py bootstrap <slug>` → crea proyecto + tareas.
3. **Dashboard:** lanzar `tools/dashboard_server.py` en background. Abrir `http://localhost:8765`.
4. **Round-Robin:** repetir dispatch → asumir rol → ejecutar → complete → approve → finalize N veces.
5. **Indexar ADRs:** correr `tools/index_adrs.py` despues de cada tarea que genere ADR.
6. **Validar end-to-end:** ejecutar checklist de §5.
7. **Cerrar proyecto:** dejar MISSION_CONTROL.md con el resumen final + ADRs en la DB.

---

## 10. Comando equivalente en modo auto

Si el operador quiere ejecutar el ciclo completo sin intervencion, existe `tools/run_project.py`:

```powershell
.venv\Scripts\python.exe tools/run_project.py --project-slug cafe-cenit
```

Hace `ensure_project` + `generate_tasks_from_backlog` + `orch.run()`. Util para CI o para validar el flujo en background, pero **no permite intervencion humana** entre turnos. En el chat se prefiere el modo manual (Round-Robin paso a paso) para mantener la narrativa y la trazabilidad.

---

## 11. Changelog

- **v1.1.1 (2026-06-06):** Documenta el bug §6.9 (dashboard mono-hilo colapsa bajo carga) y su fix (ThreadingHTTPServer + timeout). Valida con stress test de 90s: 12.5% fallos (todos 404 en endpoint inexistente) vs 87.5% antes del fix.
- **v1.1.0 (2026-06-06):** Documenta los bugs §6.7 (encoding del `start_airon.bat`) y §6.8 (self-deadlock en `quick_healthcheck`). Valida el fix con quickreply (13 tareas) y el despliegue del auto-supervisor del ecosistema. Secciones actualizadas: §1 (status header), §6 (nuevos bugs), §11 (este changelog).
- **v1.0.0 (2026-06-06):** Documento inicial. Valido con cafe-cenit-v2-demo (3 tareas) + cafe-cenit (10 tareas). Captura los 5 bugs descubiertos en produccion.

---

> *"El orquestador no es magia. Es disciplina con memoria."*
