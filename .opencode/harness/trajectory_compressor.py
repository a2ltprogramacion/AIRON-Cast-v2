#!/usr/bin/env python3
"""
Trajectory Compressor — OpenCode ⊕ AIRON-Cast Fusion
Compresión agente-dirigida de historial de ejecución (no LLM separado).
Basado en Engram agent-driven compression: per-action + session summary.
"""
import json
import os
from pathlib import Path
from typing import List, Dict, Any
from datetime import datetime

MAX_HISTORY_TOKENS = 8000
MAX_SESSION_TOKENS = 12000


class TrajectoryCompressor:
    """
    Comprime trayectoria de ejecución manteniendo señal alta.
    Dos niveles:
    1. Per-action summary (mem_save tras trabajo significativo)
    2. Session summary (mem_session_summary al cerrar)
    """
    
    def __init__(self, max_tokens: int = MAX_HISTORY_TOKENS):
        self.max_tokens = max_tokens
    
    def compress_execution_logs(self, logs: List[Dict], 
                                current_task: Dict) -> str:
        """
        Comprime execution_logs relevantes para la tarea actual.
        Estrategia: últimos N logs + logs de tareas relacionadas + resumen denso.
        """
        if not logs:
            return "Sin historial previo."
        
        # Filtrar logs relevantes: misma tarea, mismo agente, errores
        task_id = current_task.get("id")
        agent = current_task.get("assigned_agent")
        
        relevant = []
        for log in logs:
            if log.get("task_id") == task_id:
                relevant.append(log)
            elif log.get("agent_name") == agent and log.get("outcome") == "failure":
                relevant.append(log)  # errores del mismo agente siempre relevantes
        
        # Ordenar por timestamp descendente, tomar últimos
        relevant.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        relevant = relevant[:20]
        
        # Formato compacto
        lines = []
        for log in relevant:
            ts = log.get("created_at", "")[:19]
            action = log.get("action_type", "?")
            outcome = log.get("outcome", "?")
            detail = log.get("action_detail", "")[:80]
            lines.append(f"[{ts}] {log['agent_name']}: {action} ({outcome}) - {detail}")
        
        return "\n".join(lines)
    
    def compress_checkpoints(self, checkpoints: List[Dict]) -> str:
        """Comprime checkpoints a resumen denso."""
        if not checkpoints:
            return "Sin checkpoints."
        
        lines = []
        for cp in checkpoints[-10:]:  # últimos 10
            ts = cp.get("created_at", "")[:19]
            agent = cp.get("agent_name", "?")
            step = cp.get("step_description", "")[:60]
            lines.append(f"[{ts}] {agent}: {step}")
        
        return "\n".join(lines)
    
    def build_context_package(self, 
                              history: List[Dict],
                              adrs: List[Dict],
                              feedback: List[Dict],
                              current_task: Dict) -> str:
        """
        Construye paquete de contexto completo (<= 8000 tokens aprox).
        """
        parts = []
        
        # 1. Historial comprimido
        if history:
            parts.append("=== HISTORIAL COMPRIMIDO ===")
            parts.append(self.compress_execution_logs(history, current_task))
        
        # 2. ADRs relevantes
        if adrs:
            parts.append("\n=== ADRs RELEVANTES ===")
            for adr in adrs[:5]:
                parts.append(f"- {adr.get('decision_id', '?')}: {adr.get('title', '?')} [{adr.get('status', '?')}]")
        
        # 3. Feedback aplicable
        if feedback:
            parts.append("\n=== FEEDBACK APLICABLE ===")
            for fb in feedback[:5]:
                parts.append(f"- [{fb.get('error_type', '?')}] {fb.get('correction', '?')[:80]}")
        
        # 4. Tarea actual
        parts.append(f"\n=== TAREA ACTUAL ===")
        parts.append(f"ID: {current_task.get('id')}")
        parts.append(f"Título: {current_task.get('title')}")
        parts.append(f"Agente: {current_task.get('assigned_agent')}")
        parts.append(f"Prioridad: {current_task.get('priority')}")
        parts.append(f"Descripción: {current_task.get('description', '')[:500]}")
        
        return "\n".join(parts)


def estimate_tokens(text: str) -> int:
    """Estima tokens (aprox 1 token = 4 chars en español)."""
    return len(text) // 4


def truncate_to_budget(text: str, max_tokens: int) -> str:
    """Trunca texto al budget de tokens preservando estructura."""
    if estimate_tokens(text) <= max_tokens:
        return text
    
    # Truncar preservando secciones prioritarias
    lines = text.split("\n")
    # Mantener cabecera y última parte
    keep = int(max_tokens * 4 / len(lines) * len(lines)) if lines else 0
    return "\n".join(lines[:keep]) + "\n... [truncado]"


if __name__ == "__main__":
    tc = TrajectoryCompressor()
    # Test
    sample_logs = [
        {"created_at": "2026-06-12 10:00:00", "agent_name": "backend_specialist", 
         "action_type": "write", "outcome": "success", "action_detail": "Created models.py"},
        {"created_at": "2026-06-12 10:05:00", "agent_name": "backend_specialist", 
         "action_type": "write", "outcome": "success", "action_detail": "Created serializers.py"},
    ]
    task = {"id": 42, "assigned_agent": "backend_specialist", "title": "API endpoints"}
    
    result = tc.compress_execution_logs(sample_logs, task)
    print(result)