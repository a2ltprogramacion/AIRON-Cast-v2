#!/usr/bin/env python3
"""
run_project.py — AIRON‑Cast Project Runner (Autónomo)

Único punto de entrada para ejecutar un proyecto. Crea el proyecto
si no existe, lee las tareas desde BACKLOG.md, las registra en la DB
y ejecuta el ciclo Round‑Robin del Orchestrator.

Uso:
    python tools/run_project.py --project-slug cafe-cenit
"""

import sys
import argparse
import re
from pathlib import Path

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from core.memory_manager import MemoryManager
from core.orchestrator import Orchestrator


def ensure_project(mm: MemoryManager, slug: str, name: str) -> dict:
    """Crea el proyecto en la DB si no existe, o lo devuelve si ya está."""
    project = mm.get_project(slug)
    if not project:
        pid = mm.create_project(
            slug=slug,
            name=name,
            project_type="landing",
            active_workflow=None,
            client="interno",
        )
        mm.update_project_status(slug, "ACTIVE")
        project = mm.get_project(slug)
    elif project.get("status") != "ACTIVE":
        mm.update_project_status(slug, "ACTIVE")
        project = mm.get_project(slug)
    return project


def generate_tasks_from_backlog(mm: MemoryManager, project: dict) -> list:
    """Lee BACKLOG.md y registra las tareas en la base de datos."""
    backlog_path = Path("workspace") / project["slug"] / "BACKLOG.md"
    if not backlog_path.exists():
        return _generate_default_tasks(mm, project)

    content = backlog_path.read_text(encoding="utf-8")

    task_pattern = re.compile(
        r'\|\s*(T\d+)\s*\|\s*(.+?)\s*\|\s*(\S+)\s*\|\s*(\d+)\s*\|\s*(.*?)\s*\|\s*\w+\s*\|'
    )

    created = []
    for match in task_pattern.finditer(content):
        task_id, title, agent, priority, deps = match.groups()
        title = title.strip()
        agent = agent.strip().strip("`")
        priority = int(priority.strip())

        existing = mm.get_ready_tasks(project["slug"])
        if any(t.get("title") == title for t in existing):
            continue

        task_db_id = mm.create_task(
            project_id=project["id"],
            title=title,
            assigned_agent=agent,
            priority=priority,
        )
        mm.unlock_task(task_db_id)
        created.append(task_db_id)

    return created


def _generate_default_tasks(mm: MemoryManager, project: dict) -> list:
    """Fallback: tareas por defecto si no existe BACKLOG.md."""
    tasks = [
        ("requirements_architect", "Generar REQUIREMENTS.md y BACKLOG.md", 1),
        ("ux-ui_specialist", "Definir design tokens y especificaciones visuales", 2),
        ("frontend_worker", "Implementar landing page con Astro + Tailwind", 3),
        ("qa_auditor", "Revisar artefactos y emitir veredicto", 4),
    ]
    created = []
    for agent, title, priority in tasks:
        task_id = mm.create_task(
            project_id=project["id"],
            title=title,
            assigned_agent=agent,
            priority=priority,
        )
        mm.unlock_task(task_id)
        created.append(task_id)
    return created


def main():
    parser = argparse.ArgumentParser(
        description="AIRON‑Cast — Ejecutar proyecto de forma autónoma."
    )
    parser.add_argument(
        "--project-slug",
        required=True,
        help="Slug del proyecto (ej: cafe-cenit)."
    )
    args = parser.parse_args()

    mm = MemoryManager()

    # 1. Asegurar que el proyecto existe
    project = ensure_project(
        mm,
        args.project_slug,
        args.project_slug.replace("-", " ").title()
    )

    # 2. Leer BACKLOG.md y registrar tareas
    tasks = generate_tasks_from_backlog(mm, project)
    print(f"\n[INFO] {len(tasks)} tareas registradas en la DB.")

    # 3. Ejecutar el Orchestrator
    orch = Orchestrator(project_slug=args.project_slug, memory_manager=mm)
    report = orch.run()

    # 4. Resumen final
    print(f"\n{'='*60}")
    print("REPORTE FINAL")
    print(f"  Completadas : {report.tasks_completed}")
    print(f"  Fallidas    : {report.tasks_failed}")
    print(f"  Pendientes  : {report.tasks_pending}")
    print(f"  STOP_LOSS   : {report.stop_loss_triggered}")
    print(f"  Duración    : {report.duration_seconds}s")
    print(f"  Dashboard   : http://localhost:8765")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()