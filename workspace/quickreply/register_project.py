"""Script para registrar QuickReply en el ecosistema AIRON-Cast."""
import sys, os
sys.path.insert(0, 'Y:/Proyectos/AIRON-Cast')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'quickreply.settings')

from core.memory_manager import MemoryManager
from datetime import datetime, timezone

mm = MemoryManager()

slug = "quickreply"

existing = mm.get_project(slug)
if existing:
    print(f"Proyecto '{slug}' ya existe en la DB. ID: {existing['id']}")
else:
    project_id = mm.create_project(
        slug=slug,
        name="QuickReply",
        project_type="webapp",
        active_workflow="quickreply_dev",
        client="interno",
        priority=7,
        notes="Aplicacion de despacho de mensajes para marketplace. Stack: Django + Tailwind CSS + SQLite.",
    )
    print(f"Proyecto creado. ID: {project_id}")

project_id = mm.get_project(slug)["id"]
print(f"Project ID: {project_id}")

tasks_to_create = [
    {
        "title": "Diseñar schema de modelos QuickReply",
        "assigned_agent": "backend_specialist",
        "description": "Crear models.py con Product y MessageTemplate. Campos: codigo (PK), producto, tipo, precio_usd, precio_bcv, actualizado_el para Product. Titulo, categoria, contenido para MessageTemplate.",
        "priority": 10,
        "status_override": "COMPLETED",
    },
    {
        "title": "Implementar motor de renderizado de tokens",
        "assigned_agent": "backend_specialist",
        "description": "Crear utils.py con carga_excel() y render_template(). Tokens: {CODIGO_usd} y {CODIGO_bcv}. Si codigo no existe, reemplazar por [AGOTADO / CONSULTAR].",
        "priority": 10,
        "status_override": "COMPLETED",
    },
    {
        "title": "Crear vistas y endpoints API",
        "assigned_agent": "backend_specialist",
        "description": "views.py: dashboard (GET /), upload_excel (POST /upload/), search_templates (GET /search/?q=) retornando JSON con mensajes renderizados.",
        "priority": 9,
        "status_override": "COMPLETED",
    },
    {
        "title": "Construir UI con Tailwind CSS y cards colapsables",
        "assigned_agent": "frontend_worker",
        "description": "Template index.html responsivo con barra de busqueda, cards que se expanden al clickear, boton copiar con feedback de 1s.",
        "priority": 9,
        "status_override": "COMPLETED",
    },
    {
        "title": "Cargar mensajes seed desde archivo .txt",
        "assigned_agent": "backend_specialist",
        "description": "Crear script seed/load_messages.py que cargue los 26 mensajes iniciales a la base de datos.",
        "priority": 8,
        "status_override": "COMPLETED",
    },
    {
        "title": "Implementar CRUD de plantillas desde UI",
        "assigned_agent": "frontend_worker",
        "description": "Agregar funcionalidad para crear, editar y eliminar mensajes desde la interfaz web. Modal para edicion inline.",
        "priority": 7,
    },
    {
        "title": "Decorate Django admin para QuickReply",
        "assigned_agent": "backend_specialist",
        "description": "Agregar @admin decorators y admin.py con list_display, search_fields, readonly_fields apropiados para Product y MessageTemplate.",
        "priority": 6,
    },
    {
        "title": "Escribir tests automatizados",
        "assigned_agent": "tester",
        "description": "Tests unitarios para utils.py (carga_excel, render_template) y de integracion para los endpoints. Coverage > 80%.",
        "priority": 5,
    },
    {
        "title": "Agregar historial de uso (copy count)",
        "assigned_agent": "backend_specialist",
        "description": "Agregar campo copy_count a MessageTemplate. Incrementar en cada copia desde la UI. Mostrar contador en las cards.",
        "priority": 4,
    },
]

for tdata in tasks_to_create:
    status = tdata.pop("status_override", None)

    task_id = mm.create_task(
        project_id=project_id,
        title=tdata["title"],
        assigned_agent=tdata["assigned_agent"],
        description=tdata["description"],
        priority=tdata["priority"],
    )

    if status:
        mm.update_task_status(task_id, status, "system")

    print(f"  Tarea creada: {tdata['title'][:60]}... (ID: {task_id}) [{status or 'READY'}]")

print("\nRegistro completado.")
print(f"Proyecto: {slug}")
print(f"Tareas creadas: {len(tasks_to_create)}")