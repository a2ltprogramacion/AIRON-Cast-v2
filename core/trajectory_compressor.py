import json
from typing import List, Dict, Any

class TrajectoryCompressor:
    """
    Comprime el historial de logs de ejecución (trayectorias) para reducir
    el consumo de tokens, manteniendo el contexto reciente intacto y 
    resumiendo el historial más antiguo.
    Inspirado en el patrón de Hermes Agent.
    """

    def __init__(self, max_recent_logs: int = 10):
        self.max_recent_logs = max_recent_logs

    def compress_logs(self, logs: List[Dict[str, Any]]) -> str:
        """
        Toma una lista de logs (orden cronológico) y genera un bloque de texto comprimido.
        """
        if not logs:
            return "No hay historial de ejecución previo."

        total_logs = len(logs)
        
        if total_logs <= self.max_recent_logs:
            return self._format_logs(logs)

        # Separar en logs antiguos y recientes
        old_logs = logs[:-self.max_recent_logs]
        recent_logs = logs[-self.max_recent_logs:]

        # Comprimir los antiguos (aquí puede integrarse un LLM económico para resumen inteligente)
        summary = self._summarize_old_logs(old_logs)
        
        # Formatear recientes
        recent_formatted = self._format_logs(recent_logs)

        return f"=== HISTORIAL COMPRIMIDO ===\n{summary}\n\n=== EVENTOS RECIENTES ({self.max_recent_logs}) ===\n{recent_formatted}"

    def _summarize_old_logs(self, old_logs: List[Dict[str, Any]]) -> str:
        """
        Estrategia de resumen heurística básica.
        """
        success_count = sum(1 for log in old_logs if log.get("outcome") == "SUCCESS")
        failure_count = sum(1 for log in old_logs if log.get("outcome") == "FAILURE")
        
        agents_involved = list(set(log.get("agent_name", "unknown") for log in old_logs))
        
        summary = (
            f"- Eventos anteriores omitidos por compresión: {len(old_logs)}\n"
            f"- Tareas exitosas en ese periodo: {success_count}\n"
            f"- Fallos/Reintentos en ese periodo: {failure_count}\n"
            f"- Agentes involucrados: {', '.join(agents_involved)}\n"
        )
        return summary

    def _format_logs(self, logs: List[Dict[str, Any]]) -> str:
        formatted = []
        for log in logs:
            ts = log.get("created_at", "")
            agent = log.get("agent_name", "")
            action = log.get("action_type", "")
            detail = log.get("action_detail", "")
            outcome = log.get("outcome", "")
            formatted.append(f"[{ts}] {agent} | {action} -> {outcome}: {detail}")
        return "\n".join(formatted)
