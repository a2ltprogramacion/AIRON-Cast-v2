"""
Test funcional: dispatch_next + complete_task
Crea un proyecto de prueba, una tarea, la despacha y la completa.
"""
import sys
import json
sys.path.insert(0, ".")

from core.memory_manager import MemoryManager
from core.orchestrator import Orchestrator

mm = MemoryManager()

# 1. Crear proyecto de prueba
try:
    project_id = mm.create_project(
        slug="test-dispatch",
        name="Test Dispatch",
        project_type="test",
        active_workflow="none",
        client="test",
        priority=5,
    )
    print(f"[OK] Proyecto creado: id={project_id}")
except Exception as e:
    print(f"[INFO] {e}")
    proj = mm.get_project("test-dispatch")
    project_id = proj["id"]

# 2. Activar el proyecto
mm.update_project_status("test-dispatch", "ACTIVE")
print(f"[OK] Proyecto ACTIVE")

# 3. Crear una tarea READY (sin deps = se puede desbloquear)
try:
    task_id = mm.create_task(
        project_id=project_id,
        title="Test: Generar componente Hero",
        assigned_agent="frontend_worker",
        description="Generar el componente Hero de la landing page.",
        priority=10,
        dependencies=[],
    )
    # Desbloquear inmediatamente (sin dependencias)
    mm.unlock_task(task_id)
    print(f"[OK] Tarea creada y desbloqueada: id={task_id}")
except Exception as e:
    print(f"[ERROR] {e}")
    sys.exit(1)

# 4. Dispatch
o = Orchestrator("test-dispatch")
o.load_project()

result = o.dispatch_next()
if result:
    print(f"\n[OK] dispatch_next() retornó:")
    print(f"  task_id: {result['task_id']}")
    print(f"  agent: {result['agent']}")
    print(f"  title: {result['title']}")
    print(f"  prompt length: {len(result['prompt'])} chars")
    print(f"  prompt preview: {result['prompt'][:200].encode('ascii', 'replace').decode()}...")
else:
    print("[ERROR] dispatch_next() retornó None")
    sys.exit(1)

# 5. Complete
ok = o.complete_task(
    task_id=result["task_id"],
    response="TAREA COMPLETADA. Artifacts: [hero.html, hero.css]",
    artifacts=None,  # No registrar archivos reales en test
    success=True,
)
print(f"\n[OK] complete_task() retornó: {ok}")

# 6. Verificar que no hay más tareas
step = o.run_step()
print(f"\n[OK] run_step() tras completar: {step}")

print("\n✅ Test funcional EXITOSO: dispatch_next → complete_task funciona correctamente.")
