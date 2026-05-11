#!/usr/bin/env python3
# agents/agent_infra/scripts/server_lifecycle.py
# Forge Stack Engine — Django dev server lifecycle manager
# Version: 1.0
#
# Manages start / stop / status of Django development server.
# Used exclusively by skill_manage_devserver.
#
# PID tracking:
#   Writes PID to {project_dir}/.devserver.pid on start.
#   Reads PID from .devserver.pid on stop.
#   Cleans up .devserver.pid on stop or if server is found dead.
#
# Exit codes:
#   0 — operation succeeded
#   1 — operation failed (server did not start, stop failed, etc.)
#   2 — argument error

import argparse
import os
import signal
import subprocess
import sys
import time
from pathlib import Path

try:
    import urllib.request
    import urllib.error
except ImportError:
    pass  # stdlib, always available


# ── Constants ─────────────────────────────────────────────────────────────────

PID_FILENAME     = ".devserver.pid"
STARTUP_TIMEOUT  = 10     # seconds to wait for server to respond
SHUTDOWN_TIMEOUT = 5      # seconds to wait for graceful shutdown
POLL_INTERVAL    = 0.5    # seconds between health checks


# ── PID file ──────────────────────────────────────────────────────────────────

def _pid_file(project_dir: Path) -> Path:
    return project_dir / PID_FILENAME


def _write_pid(project_dir: Path, pid: int) -> None:
    _pid_file(project_dir).write_text(str(pid), encoding="utf-8")


def _read_pid(project_dir: Path) -> int | None:
    path = _pid_file(project_dir)
    if not path.exists():
        return None
    try:
        return int(path.read_text(encoding="utf-8").strip())
    except (ValueError, OSError):
        return None


def _remove_pid(project_dir: Path) -> None:
    path = _pid_file(project_dir)
    if path.exists():
        try:
            path.unlink()
        except OSError:
            pass


# ── Process checks ────────────────────────────────────────────────────────────

def _is_pid_alive(pid: int) -> bool:
    """Returns True if the process with this PID is alive."""
    if pid <= 0:
        return False
    try:
        # signal 0 = check existence without sending actual signal
        os.kill(pid, 0)
        return True
    except ProcessLookupError:
        return False
    except PermissionError:
        # Process exists but we don't have permission to signal it
        # Treat as alive
        return True


def _is_port_responding(port: int, host: str = "127.0.0.1",
                         timeout: float = 2.0) -> bool:
    """Returns True if HTTP server is responding on the given port."""
    url = f"http://{host}:{port}/"
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=timeout):
            return True
    except urllib.error.HTTPError:
        # Server responded with an HTTP error — it's up
        return True
    except (urllib.error.URLError, OSError, ConnectionRefusedError):
        return False


# ── Operations ────────────────────────────────────────────────────────────────

def op_status(project_dir: Path, port: int) -> dict:
    """
    Returns current server status.
    Checks both PID file and HTTP response.
    Cleans up stale PID file if process is dead.
    """
    pid = _read_pid(project_dir)

    pid_alive   = _is_pid_alive(pid) if pid else False
    http_alive  = _is_port_responding(port)

    # Reconcile: if PID is dead but HTTP is alive, another process owns the port
    if not pid_alive and http_alive:
        return {"running": True, "pid": None,
                "note": "Server responding on port but PID file is stale or absent"}

    # If PID is alive but HTTP is not — server might still be starting
    if pid_alive and not http_alive:
        return {"running": False, "pid": pid,
                "note": "Process alive but server not responding on port yet"}

    # If PID is dead and HTTP is dead — clean up stale PID file
    if not pid_alive and not http_alive:
        if pid:
            _remove_pid(project_dir)
        return {"running": False, "pid": None, "note": ""}

    # Both alive
    return {"running": True, "pid": pid, "note": ""}


def op_start(project_dir: Path, port: int) -> dict:
    """
    Starts Django development server.
    Returns {"ok": bool, "pid": int|None, "error": str|None}
    """
    # Check if already running
    status = op_status(project_dir, port)
    if status["running"]:
        return {"ok": True, "pid": status["pid"],
                "error": None, "note": "Already running"}

    manage_py = project_dir / "manage.py"
    if not manage_py.exists():
        return {"ok": False, "pid": None,
                "error": f"manage.py not found in {project_dir}"}

    # Build command — use same Python interpreter
    cmd = [sys.executable, str(manage_py), "runserver",
           f"127.0.0.1:{port}", "--noreload"]

    try:
        # Start detached process
        # stdout/stderr redirected to devnull — Django startup output
        # is not needed and would pollute the parent process
        proc = subprocess.Popen(
            cmd,
            cwd=str(project_dir),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            # Windows: CREATE_NO_WINDOW equivalent via detach
            start_new_session=True,
        )
    except Exception as e:
        return {"ok": False, "pid": None, "error": f"Failed to start process: {e}"}

    # Write PID immediately
    _write_pid(project_dir, proc.pid)

    # Wait for server to respond (up to STARTUP_TIMEOUT seconds)
    deadline = time.time() + STARTUP_TIMEOUT
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)
        if _is_port_responding(port):
            return {"ok": True, "pid": proc.pid, "error": None,
                    "note": f"Started in {time.time() - (deadline - STARTUP_TIMEOUT):.1f}s"}
        # Check if process died during startup
        if proc.poll() is not None:
            _remove_pid(project_dir)
            return {"ok": False, "pid": None,
                    "error": f"Process exited during startup (code={proc.returncode})"}

    # Timeout reached — process might still be starting
    # Leave PID file in place — skill can retry status check
    _remove_pid(project_dir)
    return {"ok": False, "pid": None,
            "error": f"Server did not respond within {STARTUP_TIMEOUT}s on port {port}"}


def op_stop(project_dir: Path, pid: int | None = None) -> dict:
    """
    Stops Django development server.
    Uses pid argument if provided, otherwise reads from PID file.
    Returns {"ok": bool, "error": str|None}
    """
    effective_pid = pid or _read_pid(project_dir)

    if not effective_pid:
        return {"ok": True, "error": None, "note": "No PID found — server may not be running"}

    if not _is_pid_alive(effective_pid):
        _remove_pid(project_dir)
        return {"ok": True, "error": None, "note": "Process already dead"}

    # Send SIGTERM (graceful)
    try:
        os.kill(effective_pid, signal.SIGTERM)
    except ProcessLookupError:
        _remove_pid(project_dir)
        return {"ok": True, "error": None, "note": "Process vanished before SIGTERM"}
    except PermissionError as e:
        return {"ok": False, "error": f"Permission denied sending SIGTERM: {e}"}

    # Wait for graceful shutdown
    deadline = time.time() + SHUTDOWN_TIMEOUT
    while time.time() < deadline:
        time.sleep(POLL_INTERVAL)
        if not _is_pid_alive(effective_pid):
            _remove_pid(project_dir)
            return {"ok": True, "error": None, "note": "Stopped gracefully"}

    # Graceful shutdown timed out — send SIGKILL
    try:
        os.kill(effective_pid, signal.SIGKILL)
        time.sleep(0.5)
    except (ProcessLookupError, PermissionError):
        pass

    _remove_pid(project_dir)

    if _is_pid_alive(effective_pid):
        return {"ok": False, "error": f"Process {effective_pid} could not be killed"}

    return {"ok": True, "error": None, "note": "Stopped forcefully (SIGKILL)"}


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Forge Stack Engine — Django dev server lifecycle manager"
    )
    parser.add_argument(
        "--operation", required=True,
        choices=["start", "stop", "status"],
        help="Operation to perform"
    )
    parser.add_argument(
        "--project_dir", default=".",
        help="Path to Django project root (default: current directory)"
    )
    parser.add_argument(
        "--port", type=int, default=8000,
        help="Port to use (default: 8000)"
    )
    parser.add_argument(
        "--pid", type=int, default=None,
        help="PID to stop (only for stop operation — overrides PID file)"
    )
    args = parser.parse_args()

    project_dir = Path(args.project_dir).resolve()

    if not project_dir.exists():
        print(f"ERROR: project_dir not found: {project_dir}", file=sys.stderr)
        sys.exit(2)

    # ── status ──────────────────────────────────────────────────────────────
    if args.operation == "status":
        result = op_status(project_dir, args.port)
        status = "running" if result["running"] else "stopped"
        pid    = result.get("pid")
        note   = result.get("note", "")
        print(f"status={status} pid={pid} port={args.port}"
              + (f" note={note!r}" if note else ""))
        sys.exit(0 if result["running"] else 1)

    # ── start ───────────────────────────────────────────────────────────────
    if args.operation == "start":
        result = op_start(project_dir, args.port)
        if result["ok"]:
            pid  = result.get("pid")
            note = result.get("note", "")
            print(f"started pid={pid} port={args.port}"
                  + (f" note={note!r}" if note else ""))
            sys.exit(0)
        else:
            print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)

    # ── stop ────────────────────────────────────────────────────────────────
    if args.operation == "stop":
        result = op_stop(project_dir, pid=args.pid)
        if result["ok"]:
            note = result.get("note", "")
            print("stopped" + (f" note={note!r}" if note else ""))
            sys.exit(0)
        else:
            print(f"ERROR: {result['error']}", file=sys.stderr)
            sys.exit(1)


if __name__ == "__main__":
    main()
