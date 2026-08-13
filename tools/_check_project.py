import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.memory_manager import MemoryManager

mm = MemoryManager()
p = mm.get_project("cafe-cenit")
if p:
    print(f'Proyecto: {p["name"]} (slug: {p["slug"]})')
    tasks = mm.get_ready_tasks("cafe-cenit")
    print(f"Tareas READY: {len(tasks)}")
    for t in tasks:
        print(f'  - {t["title"]} [{t["assigned_agent"]}] prioridad {t["priority"]}')
else:
    print("No existe. Creando...")
    mm.create_project(
        slug="cafe-cenit",
        name="Cafe Cenit",
        project_type="landing",
        active_workflow=None,
        client="interno",
    )
    print("Creado.")
