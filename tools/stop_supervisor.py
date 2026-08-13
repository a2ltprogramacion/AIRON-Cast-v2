#!/usr/bin/env python3
"""
stop_supervisor.py — Detiene ordenadamente el supervisor de AIRON-Cast.

Uso:
    python tools/stop_supervisor.py          # SIGTERM, espera hasta 5s
    python tools/stop_supervisor.py --force  # SIGKILL si no responde

Si no hay supervisor corriendo (PID file no existe o proceso muerto),
sale silenciosamente con codigo 0. El proximo dispatch lo revivira.

Tambien detiene el dashboard asociado (mismo arbol de procesos en Unix,
o via taskkill /T en Windows).
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.service_supervisor import (  # noqa: E402
    DASHBOARD_SCRIPT,
    PID_FILE,
    is_supervisor_alive,
    DASHBOARD_PORT,
)

# Flags para suprimir ventana de consola en Windows
_CREATE_NO_WINDOW = 0x08000000 if sys.platform == "win32" else 0


def _run_silent(*args, **kwargs):
    """subprocess.run con CREATE_NO_WINDOW en Windows."""
    if sys.platform == "win32":
        kwargs.setdefault("creationflags", _CREATE_NO_WINDOW)
    return subprocess.run(*args, **kwargs)


def kill_pid(pid: int, force: bool = False) -> bool:
    """Mata un PID. Retorna True si el proceso ya no existe."""
    if sys.platform == "win32":
        cmd = ["taskkill", "/PID", str(pid), "/T", "/F" if force else ""]
        cmd = [c for c in cmd if c]
        try:
            _run_silent(cmd, capture_output=True, timeout=5)
        except Exception:
            pass
    else:
        sig = "-9" if force else "-TERM"
        try:
            _run_silent(["kill", sig, str(pid)], capture_output=True, timeout=5)
        except Exception:
            pass
    time.sleep(0.3)
    return not _pid_exists(pid)


def _pid_exists(pid: int) -> bool:
    if sys.platform == "win32":
        try:
            r = _run_silent(
                ["tasklist", "/FI", f"PID eq {pid}"],
                capture_output=True, text=True, timeout=2,
            )
            return str(pid) in r.stdout
        except Exception:
            return False
    else:
        try:
            import os
            os.kill(pid, 0)
            return True
        except (ProcessLookupError, PermissionError):
            return False


def find_dashboard_pid() -> int | None:
    """Busca el PID de dashboard_server.py corriendo.

    Multiplataforma:
    - Windows: PowerShell Get-CimInstance con filtro por CommandLine
      (wmic esta deprecado y su salida es fragil)
    - Unix: pgrep -f
    """
    script_name = DASHBOARD_SCRIPT.name
    if sys.platform == "win32":
        try:
            # Build PS command with proper quote escaping for PowerShell
            # Filter must be: -Filter "Name='python.exe' OR Name='pythonw.exe'"
            filter_str = "Name='python.exe' OR Name='pythonw.exe'"
            ps_cmd = (
                "Get-CimInstance Win32_Process -Filter \""
                + filter_str + "\" "
                "| Where-Object { $_.CommandLine -and $_.CommandLine.Contains('"
                + script_name + "') } "
                "| Select-Object -ExpandProperty ProcessId"
            )
            print(f"DEBUG: ps_cmd = {ps_cmd}", file=sys.stderr)
            r = _run_silent(
                ["powershell", "-NoProfile", "-NonInteractive", "-Command", ps_cmd],
                capture_output=True, text=True, timeout=10,
            )
            print(f"DEBUG: stdout = {repr(r.stdout)}", file=sys.stderr)
            for line in r.stdout.splitlines():
                line = line.strip()
                print(f"DEBUG: line = {repr(line)}", file=sys.stderr)
                if line.isdigit():
                    return int(line)
        except Exception as e:
            print(f"DEBUG: exception = {e}", file=sys.stderr)
            return None
        return None
        return None
    else:
        try:
            r = _run_silent(
                ["pgrep", "-f", "dashboard_server.py"],
                capture_output=True, text=True, timeout=3,
            )
            for line in r.stdout.splitlines():
                line = line.strip()
                if line and line.isdigit():
                    return int(line)
        except Exception:
            pass
        return None


def main():
    parser = argparse.ArgumentParser(description="Detener el supervisor de AIRON-Cast")
    parser.add_argument("--force", action="store_true", help="SIGKILL en vez de SIGTERM")
    parser.add_argument("--stop-dashboard", action="store_true",
                        help="Tambien detener el dashboard (por defecto solo se detiene el supervisor)")
    args = parser.parse_args()

    if not PID_FILE.exists():
        print("No hay supervisor corriendo (PID file no existe).")
        return 0

    try:
        pid = int(PID_FILE.read_text(encoding="utf-8").strip())
    except Exception:
        print(f"PID file corrupto, eliminando: {PID_FILE}")
        PID_FILE.unlink(missing_ok=True)
        return 0

    if not is_supervisor_alive():
        print(f"PID {pid} no esta corriendo. Limpiando PID file.")
        PID_FILE.unlink(missing_ok=True)
        return 0

    print(f"Deteniendo supervisor (PID {pid})...")
    killed = kill_pid(pid, force=args.force)
    if killed:
        print(f"Supervisor detenido.")
    else:
        print(f"PID {pid} sigue vivo despues de 5s. Usa --force para SIGKILL.")
        return 1

    PID_FILE.unlink(missing_ok=True)

    if args.stop_dashboard:
        dp = find_dashboard_pid()
        if dp:
            print(f"Deteniendo dashboard (PID {dp})...")
            if kill_pid(dp, force=args.force):
                print("Dashboard detenido.")
            else:
                print(f"Dashboard PID {dp} no respondio. Usa --force.")
                return 1
        else:
            print("No se encontro proceso del dashboard.")

    print("Listo. El proximo `airon_executor.py dispatch` revivira el supervisor si hace falta.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
