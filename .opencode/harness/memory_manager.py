#!/usr/bin/env python3
"""
Memory Manager — OpenCode ⊕ AIRON-Cast Fusion
Wrapper Engram para patrones AIRON-Cast: contexto, checkpoints, artefactos, ADRs, feedback.
"""
import json
import os
import sqlite3
import subprocess
import hashlib
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Any

class MemoryManager:
    def __init__(self, project_slug: str):
        self.project_slug = project_slug
        self.engram_db = Path.home() / ".engram" / f"airon_{project_slug}.db"
        self.engram_db.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()
    
    def _init_db(self):
        """Inicializa tablas AIRON-Cast en la DB Engram si no existen."""
        # Engram ya tiene su schema; añadimos tablas AIRON-Cast
        pass
    
    def mem_context(self, agent: str, task_description: str, limit: int = 10000) -> Dict[str, Any]:
        """
        Pipeline de contexto Engram (3-layer progressive disclosure).
        Returns: compressed_history, adrs, feedback, task_context
        """
        # Layer 1: Session index (~100 tokens)
        sessions = self._run_engram("mem_context", {"limit": 5})
        
        # Layer 2: Timeline relevante
        timeline = self._run_engram("mem_timeline", {"limit": 10})
        
        # Layer 3: Full observations bajo demanda (no aquí)
        
        # ADRs relevantes via FTS5
        adrs = self._run_engram("mem_search", {
            "query": task_description,
            "type": "adr",
            "project": self.project_slug,
            "limit": 5
        })
        
        # Feedback aplicable
        feedback = self._run_engram("mem_search", {
            "query": task_description,
            "type": "feedback",
            "affected_agent": agent,
            "limit": 5
        })
        
        return {
            "sessions": sessions,
            "timeline": timeline,
            "adrs": adrs,
            "feedback": feedback,
            "task": task_description
        }
    
    def mem_save(self, title: str, type: str, content: str, 
                 project: str = None, tags: List[str] = None) -> str:
        """
        Guarda observación en Engram (agent-driven compression).
        type: 'decision'|'bugfix'|'pattern'|'adr'|'feedback'|'checkpoint'
        """
        project = project or self.project_slug
        cmd = [
            "engram", "save",
            "--title", title,
            "--type", type,
            "--content", content,
            "--project", project
        ]
        if tags:
            cmd.extend(["--tags", ",".join(tags)])
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError(f"mem_save failed: {result.stderr}")
        
        # Extraer observation ID del output
        return result.stdout.strip()
    
    def mem_session_summary(self, summary: str, metrics: Dict[str, Any]) -> None:
        """Summary obligatorio al cerrar sesión."""
        self.mem_save(
            title=f"Session Summary - {datetime.now().isoformat()}",
            type="session_summary",
            content=json.dumps({"summary": summary, "metrics": metrics}, ensure_ascii=False),
            tags=["session", "summary"]
        )
    
    def write_checkpoint(self, agent: str, task_id: str, state: Dict[str, Any]) -> str:
        """Checkpoint antes de acción irreversible."""
        return self.mem_save(
            title=f"Checkpoint - {task_id} by {agent}",
            type="checkpoint",
            content=json.dumps(state, ensure_ascii=False),
            tags=["checkpoint", agent, task_id]
        )
    
    def register_artifact(self, filepath: str, agent: str, 
                          file_type: str = "source") -> Dict[str, str]:
        """Registra artefacto con checksum SHA256."""
        checksum = self._calculate_sha256(filepath)
        size = os.path.getsize(filepath)
        
        content = json.dumps({
            "filepath": filepath,
            "checksum": checksum,
            "size": size,
            "agent": agent,
            "file_type": file_type
        }, ensure_ascii=False)
        
        obs_id = self.mem_save(
            title=f"Artifact: {Path(filepath).name}",
            type="artifact",
            content=content,
            tags=["artifact", file_type, agent]
        )
        
        return {"id": obs_id, "checksum": checksum}
    
    def verify_checksum(self, filepath: str) -> bool:
        """Verifica integridad de artefacto."""
        # Buscar en memoria y comparar
        return True  # Placeholder
    
    def _calculate_sha256(self, filepath: str) -> str:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    
    def _run_engram(self, subcommand: str, args: Dict) -> Any:
        """Ejecuta subcomando Engram y parsea JSON output."""
        cmd = ["engram", subcommand]
        for k, v in args.items():
            cmd.extend([f"--{k}", str(v)])
        cmd.append("--format")
        cmd.append("json")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0:
            return []
        try:
            return json.loads(result.stdout)
        except:
            return []


# Singleton por proyecto
_memory_managers = {}

def get_memory_manager(project_slug: str) -> MemoryManager:
    if project_slug not in _memory_managers:
        _memory_managers[project_slug] = MemoryManager(project_slug)
    return _memory_managers[project_slug]


if __name__ == "__main__":
    # Test rápido
    mm = get_memory_manager("test-project")
    print("MemoryManager inicializado")