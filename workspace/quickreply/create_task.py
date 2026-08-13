import sys, os
sys.path.insert(0, 'Y:/Proyectos/AIRON-Cast')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickreply.settings')
import django
django.setup()
from core.memory_manager import MemoryManager
mm = MemoryManager()
project = mm.get_project("quickreply")
task_id = mm.create_task(
    project_id=project["id"],
    title="Disenar interfaz de importacion de mensajes",
    assigned_agent="frontend_worker",
    description="UI para cargar mensajes de forma individual (formulario) y masiva (JSON/Markdown). Seccion en index.html con tabs Individual/Masivo.",
    priority=8,
)
print("Tarea creada: ID " + str(task_id))