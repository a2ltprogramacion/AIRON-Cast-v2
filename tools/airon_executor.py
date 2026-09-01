#!/usr/bin/env python3
"""
airon_executor.py — AIRON-Cast Executor Bridge

Wrapper CLI sobre Orchestrator.run_step() y complete_task().
Permite que un ejecutor externo (humano o LLM) consuma un turno a la vez
sin mantener estado entre invocaciones.

Comandos:
    dispatch <slug>                → emite prompt para la siguiente tarea READY
    complete <slug> <task_id>      → marca la tarea como REVIEW (éxito)
    fail <slug> <task_id>          → marca la tarea como FAILED (con retry)
    status <slug>                  → muestra el estado actual del proyecto

Uso típico desde el chat:
    1. python tools/airon_executor.py dispatch cafe-cenit-v2-demo
    2. (el LLM lee el prompt, asume el rol, trabaja)
    3. python tools/airon_executor.py complete cafe-cenit-v2-demo 1 \
         --artifacts workspace/cafe-cenit-v2-demo/src/styles/tokens.json
    4. Repetir hasta que status devuelva "empty"
"""

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path

# Forzar UTF-8 en stdout/stderr para evitar errores de encoding en Windows cp1252
try:
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")
except Exception:
    pass

REPO_ROOT = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(REPO_ROOT))

from core.orchestrator import Orchestrator
from core.memory_manager import MemoryManager
from tools.run_project import ensure_project, generate_tasks_from_backlog


def _print_json(obj):
    print(json.dumps(obj, indent=2, ensure_ascii=False, default=str))


def cmd_bootstrap(args):
    """Crea el proyecto y registra las tareas del BACKLOG.md (sin ejecutar)."""
    mm = MemoryManager()
    name = args.slug.replace("-", " ").title()
    project = ensure_project(mm, args.slug, name)
    tasks = generate_tasks_from_backlog(mm, project)
    _print_json({
        "status": "bootstrapped",
        "project": {"slug": project["slug"], "name": project["name"], "id": project["id"]},
        "tasks_created": len(tasks),
        "task_ids": tasks,
    })
    return 0


def cmd_dispatch(args):
    from core.service_supervisor import ensure_supervisor_running, quick_healthcheck
    sup_state = ensure_supervisor_running()
    health = quick_healthcheck()

    orch = Orchestrator(project_slug=args.slug)
    orch.load_project()
    result = orch.run_step()
    if "supervisor" not in result:
        result["supervisor"] = sup_state
    if "ecosystem_health" not in result:
        result["ecosystem_health"] = health
    _print_json(result)
    return 0 if result.get("status") == "dispatched" else 1


def cmd_complete(args):
    mm = MemoryManager()
    orch = Orchestrator(project_slug=args.slug, memory_manager=mm)
    orch.load_project()
    project = orch.project
    if not project:
        print(json.dumps({"error": f"Project '{args.slug}' not found"}))
        return 1
    
    # VALIDACIÓN: Verificar artefactos antes de completar (si el hook existe)
    validator_path = REPO_ROOT / "core" / "validator.py"
    if validator_path.exists():
        validation = subprocess.run(
            ["python", str(validator_path), str(args.task_id), "complete", args.slug],
            capture_output=True, text=True, cwd=REPO_ROOT,
        )
        if validation.returncode != 0:
            print(json.dumps({
                "status": "error",
                "task_id": args.task_id,
                "error": "Validación de artefactos fallida",
                "details": validation.stdout.strip() or validation.stderr.strip()
            }))
            return 1
    
    success = orch.complete_task(
        task_id=args.task_id,
        response=args.response or f"Task {args.task_id} completed by executor.",
        artifacts=args.artifacts or [],
        success=True,
    )
    _print_json({"status": "completed" if success else "error", "task_id": args.task_id})
    return 0 if success else 1


def cmd_fail(args):
    mm = MemoryManager()
    orch = Orchestrator(project_slug=args.slug, memory_manager=mm)
    orch.load_project()
    project = orch.project
    if not project:
        print(json.dumps({"error": f"Project '{args.slug}' not found"}))
        return 1
    success = orch.complete_task(
        task_id=args.task_id,
        response=args.response or f"Task {args.task_id} failed.",
        artifacts=[],
        success=False,
    )
    _print_json({"status": "failed" if success else "error", "task_id": args.task_id})
    return 0 if success else 1


def cmd_approve(args):
    """Mueve una tarea en REVIEW a APPROVED (acción de qa_auditor)."""
    mm = MemoryManager()
    try:
        mm.update_task_status(args.task_id, "APPROVED", args.agent or "qa_auditor")
        _print_json({"status": "approved", "task_id": args.task_id})
        return 0
    except Exception as e:
        _print_json({"error": str(e)})
        return 1


def cmd_finalize(args):
    """Mueve una tarea APPROVED a COMPLETED (acción de orchestrator)."""
    mm = MemoryManager()
    try:
        # VALIDACIÓN: Verificar artefactos antes de finalizar (si el hook existe)
        validator_path = REPO_ROOT / "core" / "validator.py"
        if validator_path.exists():
            validation = subprocess.run(
                ["python", str(validator_path), str(args.task_id), "finalize", args.slug],
                capture_output=True, text=True, cwd=REPO_ROOT,
            )
            if validation.returncode != 0:
                print(json.dumps({
                    "status": "error",
                    "task_id": args.task_id,
                    "error": "Validación de artefactos fallida",
                    "details": validation.stdout.strip() or validation.stderr.strip()
                }))
                return 1
        
        mm.update_task_status(args.task_id, "COMPLETED", "orchestrator")
        _print_json({"status": "completed", "task_id": args.task_id})
        return 0
    except Exception as e:
        _print_json({"error": str(e)})
        return 1


def cmd_status(args):
    mm = MemoryManager()
    if not args.slug:
        projects = mm.get_project_status()
        _print_json({
            "projects": [
                {
                    "slug": p["slug"],
                    "name": p["name"],
                    "status": p["project_status"],
                    "total_tasks": p["total_tasks"],
                    "completed": p["completed_tasks"],
                    "failed": p["failed_tasks"],
                    "in_progress": p["in_progress_tasks"],
                    "pending": p["pending_tasks"],
                    "progress_pct": p["progress_pct"],
                }
                for p in projects
            ]
        })
        return 0

    projects = mm.get_project_status(slug=args.slug)
    if not projects:
        print(json.dumps({"error": f"Project '{args.slug}' not found"}))
        return 1
    p = projects[0]
    ready = mm.get_ready_tasks(args.slug)
    _print_json({
        "project": {
            "slug": p["slug"],
            "name": p["name"],
            "status": p["project_status"],
            "total_tasks": p["total_tasks"],
            "completed": p["completed_tasks"],
            "failed": p["failed_tasks"],
            "in_progress": p["in_progress_tasks"],
            "pending": p["pending_tasks"],
            "progress_pct": p["progress_pct"],
        },
        "ready_tasks": [
            {"id": t["id"], "title": t["title"], "agent": t["assigned_agent"], "priority": t["priority"]}
            for t in ready
        ],
    })
    return 0


def cmd_health(args):
    from core.service_supervisor import ensure_supervisor_running, quick_healthcheck
    sup_state = ensure_supervisor_running()
    health = quick_healthcheck()
    _print_json({
        "supervisor": sup_state,
        "health": health,
    })
    if not health["dashboard_up"]:
        return 1
    return 0


def main():
    parser = argparse.ArgumentParser(description="AIRON-Cast Executor Bridge")
    sub = parser.add_subparsers(dest="command", required=True)

    p_disp = sub.add_parser("dispatch", help="Despachar siguiente tarea READY")
    p_disp.add_argument("slug")
    p_disp.set_defaults(func=cmd_dispatch)

    p_comp = sub.add_parser("complete", help="Marcar tarea como completada")
    p_comp.add_argument("slug")
    p_comp.add_argument("task_id", type=int)
    p_comp.add_argument("--artifacts", nargs="*", default=[])
    p_comp.add_argument("--response", default="")
    p_comp.set_defaults(func=cmd_complete)

    p_fail = sub.add_parser("fail", help="Marcar tarea como fallida")
    p_fail.add_argument("slug")
    p_fail.add_argument("task_id", type=int)
    p_fail.add_argument("--response", default="")
    p_fail.set_defaults(func=cmd_fail)

    p_app = sub.add_parser("approve", help="Mover tarea REVIEW → APPROVED (qa_auditor)")
    p_app.add_argument("slug")
    p_app.add_argument("task_id", type=int)
    p_app.add_argument("--agent", default="qa_auditor")
    p_app.set_defaults(func=cmd_approve)

    p_fin = sub.add_parser("finalize", help="Mover tarea APPROVED → COMPLETED (orchestrator)")
    p_fin.add_argument("slug")
    p_fin.add_argument("task_id", type=int)
    p_fin.set_defaults(func=cmd_finalize)

    p_stat = sub.add_parser("status", help="Ver estado del proyecto")
    p_stat.add_argument("slug", nargs="?", default=None)
    p_stat.set_defaults(func=cmd_status)

    p_boot = sub.add_parser("bootstrap", help="Crear proyecto + tareas desde BACKLOG.md (sin ejecutar)")
    p_boot.add_argument("slug")
    p_boot.set_defaults(func=cmd_bootstrap)

    p_health = sub.add_parser("health", help="Estado de servicios del ecosistema (sin despachar)")
    p_health.set_defaults(func=cmd_health)

    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
