#!/usr/bin/env python3
"""
airon_supervisor.py — Watchdog de servicios del ecosistema AIRON-Cast.

Loop principal:
    1. Verificar que el dashboard esta respondiendo en :8765
    2. Verificar que central_intelligence.db existe
    3. Si algo falta -> relanzar / registrar warning
    4. Loguear a logs/supervisor.log
    5. Dormir 300s (5 minutos)

Alcance: SOLO servicios del ecosistema.
NO supervisa: backends/frontends de workspace/<slug>/ (esos son proyectos
entregados a clientes y viven fuera del ecosistema).

Ciclo de vida:
- Lanzado por: start_airon.bat opcion [1] o primer dispatch de airon_executor
- Detenido por: tools/stop_supervisor.py (SIGTERM) o cierre de Windows
- Auto-revivido por: airon_executor.py dispatch() si no detecta PID vivo
- Doble-instancia: detectado via PID file + tasklist/os.kill
"""
from __future__ import annotations

import atexit
import os
import signal
import subprocess
import sys
import time
import urllib.request
from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.service_supervisor import (  # noqa: E402
    DASHBOARD_HEALTHZ,
    DASHBOARD_SCRIPT,
    DB_PATH,
    LOG_DIR,
    PID_FILE,
    SUPERVISOR_INTERVAL_SECONDS,
    SUPERVISOR_LOG,
    is_supervisor_alive,
)


LOG_MAX_BYTES = 1_000_000
LOG_KEEP_LINES = 200
STARTED_AT = datetime.now()


def log(message: str) -> None:
    """Escribe una linea con timestamp al log."""
    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    line = f"[{ts}] {message}\n"
    try:
        with open(SUPERVISOR_LOG, "a", encoding="utf-8") as f:
            f.write(line)
        print(line, end="", flush=True)
    except Exception as e:
        print(f"[supervisor] error escribiendo log: {e}", file=sys.stderr)


def rotate_log_if_needed() -> None:
    """Si supervisor.log > 1MB, truncar a las ultimas 200 lineas."""
    if not SUPERVISOR_LOG.exists():
        return
    if SUPERVISOR_LOG.stat().st_size < LOG_MAX_BYTES:
        return
    try:
        with open(SUPERVISOR_LOG, "r", encoding="utf-8", errors="ignore") as f:
            lines = f.readlines()
        keep = lines[-LOG_KEEP_LINES:] if len(lines) > LOG_KEEP_LINES else lines
        backup = SUPERVISOR_LOG.with_suffix(".log.bak")
        if backup.exists():
            backup.unlink()
        SUPERVISOR_LOG.rename(backup)
        with open(SUPERVISOR_LOG, "w", encoding="utf-8") as f:
            f.writelines(keep)
            f.write(f"[{datetime.now():%Y-%m-%d %H:%M:%S}] log rotado (>{LOG_MAX_BYTES} bytes)\n")
    except Exception as e:
        print(f"[supervisor] error rotando log: {e}", file=sys.stderr)


def write_pidfile(pid: int) -> None:
    PID_FILE.write_text(str(pid), encoding="utf-8")


def cleanup() -> None:
    """Borra el PID file. Llamado al recibir senal o al salir."""
    try:
        if PID_FILE.exists():
            PID_FILE.unlink()
            log("PID file eliminado, supervisor saliendo.")
    except Exception as e:
        print(f"[supervisor] error limpiando PID file: {e}", file=sys.stderr)


def register_signal_handlers() -> None:
    """Maneja SIGTERM/SIGINT (Unix). En Windows, atexit cubre el caso."""
    if sys.platform == "win32":
        return
    def handler(signum, frame):
        log(f"Senal {signum} recibida, saliendo.")
        cleanup()
        sys.exit(0)
    signal.signal(signal.SIGTERM, handler)
    signal.signal(signal.SIGINT, handler)


def check_dashboard() -> bool:
    """True si el dashboard escucha en :8765 (socket connect).

    Usa socket en vez de urllib para evitar self-deadlock si se invoca
    desde el dashboard y para no gastar recursos haciendo HTTP.
    """
    import socket
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(2)
            s.connect(("127.0.0.1", 8765))
            return True
    except (socket.timeout, ConnectionRefusedError, OSError) as e:
        log(f"dashboard :8765 caido ({type(e).__name__})")
        return False


def check_db() -> bool:
    """True si central_intelligence.db existe y no esta vacio."""
    if not DB_PATH.exists():
        log(f"DB no encontrada: {DB_PATH}")
        return False
    if DB_PATH.stat().st_size < 100:
        log(f"DB sospechosa (tamano {DB_PATH.stat().st_size} bytes)")
        return False
    return True


def start_dashboard() -> bool:
    """Lanza dashboard_server.py detached. Retorna True si arranco."""
    try:
        from core.service_supervisor import launch_dashboard_detached
        log(f"lanzando dashboard: {DASHBOARD_SCRIPT.name}")
        proc_pid = launch_dashboard_detached()
        time.sleep(0.5)
        if check_dashboard():
            log(f"dashboard :8765 healthy (PID {proc_pid})")
            return True
        log(f"dashboard :8765 lanzado (PID {proc_pid}) pero sin responder aun")
        return True
    except Exception as e:
        log(f"error lanzando dashboard: {e}")
        return False


def run() -> None:
    """Loop principal del supervisor."""
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    write_pidfile(os.getpid())
    register_signal_handlers()
    atexit.register(cleanup)

    uptime_start = time.time()
    log(f"supervisor iniciado (PID {os.getpid()}, intervalo {SUPERVISOR_INTERVAL_SECONDS}s)")
    log(f"alcanze: ecosistema AIRON-Cast (dashboard :8765, DB). NO supervisa proyectos.")

    cycle = 0
    while True:
        cycle += 1
        try:
            rotate_log_if_needed()

            dashboard_was_up = check_dashboard()
            db_ok = check_db()

            if not dashboard_was_up:
                start_dashboard()
            if not db_ok:
                log("ADVERTENCIA: la DB no existe o esta corrupta. El supervisor no la recrea (responsabilidad del operador via init_ecosystem.py).")

            if cycle % 12 == 0:
                hours = (time.time() - uptime_start) / 3600
                log(f"heartbeat: ciclo {cycle}, uptime {hours:.1f}h, dashboard={'up' if dashboard_was_up else 'recovered'}, db={'ok' if db_ok else 'missing'}")

        except KeyboardInterrupt:
            log("KeyboardInterrupt recibido, saliendo.")
            break
        except Exception as e:
            log(f"error inesperado en ciclo {cycle}: {e}")

        time.sleep(SUPERVISOR_INTERVAL_SECONDS)


if __name__ == "__main__":
    if is_supervisor_alive():
        print("Otro supervisor ya esta corriendo (PID file existe). Saliendo.", file=sys.stderr)
        sys.exit(0)
    run()
