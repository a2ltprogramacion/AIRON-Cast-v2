import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core.memory_manager import MemoryManager

mm = MemoryManager()
mm.update_project_status("cafe-cenit", "ACTIVE")
print("Proyecto activado.")
