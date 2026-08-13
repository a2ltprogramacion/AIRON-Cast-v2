"""
service_supervisor.py — Logica compartida entre supervisor y executor.

Decision arquitectonica: la logica vive en core/ porque es transversal.
- tools/airon_supervisor.py  (watchdog que corre en background)
- tools/airon_executor.py     (cada dispatch verifica que el supervisor este vivo)

Esto evita duplicacion y permite tests unitarios sin levantar procesos reales.

Alcance: SOLO servicios del ecosistema AIRON-Cast.
NO supervisa: backends/frontends de workspace/<slug>/ (esos son proyectos
entregados a clientes y viven fuera del ecosistema).
"""
from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
import urllib.request
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parent.parent
PID_FILE = REPO_ROOT / ".airon_supervisor.pid"
LOG_DIR = REPO_ROOT / "logs"
SUPERVISOR_LOG = LOG_DIR / "supervisor.log"

DASHBOARD_PORT = 8765
DASHBOARD_URL = f"http://localhost:{DASHBOARD_PORT}"
DASHBOARD_HEALTHZ = f"{DASHBOARD_URL}/healthz"

SUPERVISOR_SCRIPT = REPO_ROOT / "tools" / "airon_supervisor.py"
DASHBOARD_SCRIPT = REPO_ROOT / "tools" / "dashboard_server.py"

DB_PATH = REPO_ROOT / "central_intelligence.db"

HEALTHCHECK_TIMEOUT = 1.0
SUPERVISOR_INTERVAL_SECONDS = 300
SUPERVISOR_BOOT_GRACE = 0.3

# Marcada True desde tools/dashboard_server.py al iniciar. Sirve para que
# quick_healthcheck NO haga self-socket-connect cuando se ejecuta dentro
# del dashboard server (causaria self-deadlock porque BaseHTTPRequestHandler
# es serial y bloqueante).
_INSIDE_DASHBOARD_PROCESS = False


def is_supervisor_alive() -> bool:
    """True si el proceso del supervisor existe.

    Multiplataforma:
    - Windows: usa `tasklist /FI` para verificar el PID
    - Unix: usa `os.kill(pid, 0)` (signal 0 = check existencia)
    """
    if not PID_FILE.exists():
        return False
    try:
        raw = PID_FILE.read_text(encoding="utf-8").strip()
        pid = int(raw)
    except (ValueError, OSError):
        PID_FILE.unlink(missing_ok=True)
        return False

    try:
        if sys.platform == "win32":
            CREATE_NO_WINDOW = 0x08000000
            r = subprocess.run(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True, timeout=2,
                creationflags=CREATE_NO_WINDOW,
            )
            alive = f" {pid} " in r.stdout or f" {pid}\n" in r.stdout
            if not alive and f"{pid}" in r.stdout:
                alive = True
            if not alive:
                PID_FILE.unlink(missing_ok=True)
            return alive
        else:
            os.kill(pid, 0)
            return True
    except (subprocess.TimeoutExpired, ProcessLookupError, PermissionError, OSError):
        if isinstance(sys.exc_info()[1], ProcessLookupError):
            PID_FILE.unlink(missing_ok=True)
        return False


def _pythonw_or_python() -> str:
    """Retorna la ruta a pythonw.exe si existe (sin consola), si no sys.executable."""
    if sys.platform == "win32":
        pwoff = Path(sys.executable).parent / "pythonw.exe"
        if pwoff.exists():
            return str(pwoff)
    return sys.executable


def launch_supervisor_detached() -> int:
    """Lanza el supervisor como proceso detached. Retorna PID.

    - Windows: DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    - Unix: start_new_session=True (setsid)
    """
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = open(SUPERVISOR_LOG, "a", encoding="utf-8")

    kwargs: dict[str, Any] = {
        "stdout": log_file,
        "stderr": log_file,
        "stdin": subprocess.DEVNULL,
        "close_fds": True,
    }

    if sys.platform == "win32":
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    proc = subprocess.Popen([_pythonw_or_python(), str(SUPERVISOR_SCRIPT)], **kwargs)
    return proc.pid


def launch_dashboard_detached() -> int:
    """Lanza el dashboard como proceso TRULY detached.

    Importante: usa pythonw.exe en Windows para que NO abra consola visible.
    usa DETACHED_PROCESS para que sobreviva al cierre del shell padre.
    """
    DASHBOARD_OUT = LOG_DIR / "dashboard.out.log"
    DASHBOARD_ERR = LOG_DIR / "dashboard.err.log"
    LOG_DIR.mkdir(parents=True, exist_ok=True)
    out_file = open(DASHBOARD_OUT, "a", encoding="utf-8")
    err_file = open(DASHBOARD_ERR, "a", encoding="utf-8")

    kwargs: dict[str, Any] = {
        "stdout": out_file,
        "stderr": err_file,
        "stdin": subprocess.DEVNULL,
        "close_fds": True,
        "cwd": str(REPO_ROOT),
    }

    if sys.platform == "win32":
        DETACHED_PROCESS = 0x00000008
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        kwargs["creationflags"] = DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True

    proc = subprocess.Popen([_pythonw_or_python(), str(DASHBOARD_SCRIPT)], **kwargs)
    return proc.pid


def ensure_supervisor_running() -> dict:
    """Idempotente. Si el supervisor no esta vivo, lo lanza.

    Retorna dict con estado para logging/debug.
    """
    if is_supervisor_alive():
        return {"status": "running", "action": "none"}

    pid = launch_supervisor_detached()
    time.sleep(SUPERVISOR_BOOT_GRACE)

    if is_supervisor_alive():
        return {"status": "launched", "action": "started", "pid": pid}
    return {"status": "launch_pending", "action": "started", "pid": pid}


def quick_healthcheck() -> dict:
    """Chequeo rapido de servicios del ecosistema. No bloqueante.

    Disenado para invocarse antes de cada dispatch. Si el dashboard
    esta caido, NO se bloquea: solo se reporta en logs.

    Importante: si este metodo se invoca DENTRO del propio dashboard server
    (por ejemplo, desde el handler /api/health), NO hace socket connect a
    8765 porque el BaseHTTPRequestHandler es serial y eso causaria
    self-deadlock intermitente. En su lugar, marca dashboard_up=True sin
    verificar (si esta respondiendo, esta vivo).
    """
    dashboard_up = False
    dashboard_error = None
    in_dashboard = _INSIDE_DASHBOARD_PROCESS

    if in_dashboard:
        dashboard_up = True
        dashboard_error = None
    else:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(HEALTHCHECK_TIMEOUT)
                s.connect(("127.0.0.1", DASHBOARD_PORT))
                dashboard_up = True
        except (socket.timeout, ConnectionRefusedError, OSError) as e:
            dashboard_error = type(e).__name__

    return {
        "dashboard_up": dashboard_up,
        "dashboard_url": DASHBOARD_URL,
        "dashboard_error": dashboard_error,
        "db_exists": DB_PATH.exists(),
        "db_size_bytes": DB_PATH.stat().st_size if DB_PATH.exists() else 0,
        "supervisor_alive": is_supervisor_alive(),
    }


def mark_inside_dashboard_process() -> None:
    """Marca este proceso como servidor del dashboard.

    Llamar UNA vez al inicio del dashboard server para que quick_healthcheck
    sepa que NO debe hacer self-socket-connect (causaria self-deadlock).
    """
    global _INSIDE_DASHBOARD_PROCESS
    _INSIDE_DASHBOARD_PROCESS = True
