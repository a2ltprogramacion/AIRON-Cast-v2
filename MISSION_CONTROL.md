# MISSION_CONTROL — AIRON-Cast Ecosystem

> Bitácora narrativa de alto nivel del ecosistema.
> Las tareas viven en `central_intelligence.db`; este archivo es resumen legible.

---

## 2026-06-06 — Implementación del Auto-Supervisor

### Hito
AIRON-Cast ahora supervisa automáticamente sus propios servicios (dashboard y DB) sin depender de Scheduled Task, servicios de Windows ni configuración específica de la máquina.

### Arquitectura
- **Watchdog portable** (5 min de intervalo) que vive en el repo, no en el sistema operativo
- **Auto-curación** vía `airon_executor.py dispatch` (cada turno del LLM revive el supervisor si murió)
- **Cero dependencias nuevas** — solo stdlib Python

### Componentes nuevos
| Archivo | Líneas | Rol |
|---|---|---|
| `core/service_supervisor.py` | 145 | Lógica compartida: PID check, launch detached, health check vía socket |
| `tools/airon_supervisor.py` | 180 | Loop principal del watchdog, log a `logs/supervisor.log` |
| `tools/stop_supervisor.py` | 130 | CLI para detener ordenadamente |
| `tools/test_service_supervisor.py` | 175 | 16 tests con mocks de subprocess + socket |

### Componentes modificados
| Archivo | Cambio |
|---|---|
| `tools/airon_executor.py` | +`ensure_supervisor_running()` antes de dispatch, +subcomando `health` |
| `tools/dashboard_server.py` | +endpoint `/healthz` (200 OK), +handler `/api/health` con estado completo |
| `dashboard/index.html` | +widget "🩺 Salud de Servicios" con 4 cards (dashboard, supervisor, DB, log) |
| `start_airon.bat` | +opción [2] dashboard + supervisor automático |
| `AGENTS.md` | +sección 8 "Auto-Supervisión de Servicios del Ecosistema" |
| `.gitignore` | +`.airon_supervisor.pid`, +`logs/`, +estándar Python |

### Verificación
- ✅ 16/16 tests `pytest tools/test_service_supervisor.py` PASS
- ✅ Smoke test: dashboard muerto → revive en 2s
- ✅ Widget del dashboard se alimenta de `GET /api/health` cada 2s
- ✅ Portabilidad confirmada: ningún path absoluto, ningún servicio Windows

### Bugs resueltos durante implementación
1. **Self-deadlock en `/api/health`:** `urllib.request.urlopen` desde el propio dashboard al mismo puerto causa deadlock porque `BaseHTTPRequestHandler` es serial. Solución: usar `socket.connect()` con timeout para health check, evitando HTTP self-call.
2. **wmic colgado:** `wmic process where ProcessId=X` en Windows puede tardar >30s. Solución: omitir `started_at` en Windows (Unix usa `/proc/<pid>/stat` que es instantáneo).
3. **PID file race condition:** `ensure_supervisor_running` retornaba el PID del Popen (proceso que lo lanzó) en vez del supervisor. Solución: usar `is_supervisor_alive()` post-launch (verifica vía tasklist) para confirmar.

### Lecciones
- **Health checks deben ser self-contained:** un servicio no debería intentar hablar HTTP consigo mismo. Usar `socket.connect()` con timeout para "está escuchando?" en lugar de HTTP roundtrip.
- **BaseHTTPRequestHandler es serial y bloqueante:** cualquier `subprocess.run` o `urllib` dentro de un handler puede colgar el servidor. Mantener handlers cortos y defensivos (try/except con fallbacks).
- **El ecosistema supervisa el ecosistema, no los proyectos:** separación arquitectónica clara. El supervisor nunca toca `workspace/`.
