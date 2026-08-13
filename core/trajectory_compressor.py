"""
AIRON-Cast — Trajectory Compressor
===================================
Comprime el historial de logs de ejecución (trayectorias) para reducir
el consumo de tokens, manteniendo el contexto reciente intacto y
resumiendo el historial más antiguo.

Integrado con memory_manager.build_context_for().
"""

from typing import List, Dict, Any


class TrajectoryCompressor:
    """
    Comprime una lista cronológica de execution_logs en un bloque de texto
    optimizado para ventanas de contexto de agentes.
    """

    def __init__(self, max_recent_logs: int = 10):
        self.max_recent_logs = max_recent_logs

    def compress_logs(self, logs: List[Dict[str, Any]]) -> str:
        """
        Toma una lista de logs (orden cronológico) y genera un bloque
        de texto comprimido listo para inyectar en el contexto del agente.
        """
        if not logs:
            return "[AIRON-Cast] Sin historial de ejecución previo."

        total_logs = len(logs)

        if total_logs <= self.max_recent_logs:
            return "=== HISTORIAL DE EJECUCIÓN ===\n" + self._format_logs(logs)

        old_logs = logs[:-self.max_recent_logs]
        recent_logs = logs[-self.max_recent_logs:]

        summary = self._summarize_old_logs(old_logs)
        recent_formatted = self._format_logs(recent_logs)

        return (
            f"=== HISTORIAL COMPRIMIDO ===\n"
            f"{summary}\n\n"
            f"=== EVENTOS RECIENTES ({self.max_recent_logs}) ===\n"
            f"{recent_formatted}"
        )

    def _summarize_old_logs(self, old_logs: List[Dict[str, Any]]) -> str:
        """
        Genera un resumen heurístico de los eventos comprimidos.
        """
        success_count = sum(1 for log in old_logs if log.get("outcome") == "success")
        failure_count = sum(1 for log in old_logs if log.get("outcome") == "failure")
        pending_count = sum(1 for log in old_logs if log.get("outcome") == "pending")

        agents_involved = list(set(
            log.get("agent_name", "system") for log in old_logs
        ))

        total_tokens = sum(
            log.get("tokens_used", 0) or 0 for log in old_logs
        )

        summary = (
            f"- Eventos comprimidos: {len(old_logs)}\n"
            f"- Tareas exitosas: {success_count}\n"
            f"- Fallos/Reintentos: {failure_count}\n"
            f"- Pendientes/Transiciones: {pending_count}\n"
            f"- Agentes activos: {', '.join(agents_involved)}\n"
        )
        if total_tokens > 0:
            summary += f"- Tokens consumidos (periodo): {total_tokens}\n"

        return summary

    def _format_logs(self, logs: List[Dict[str, Any]]) -> str:
        """
        Formatea los logs recientes en líneas legibles.
        """
        formatted = []
        for log in logs:
            ts = log.get("created_at", "")[:19]  # YYYY-MM-DD HH:MM:SS
            agent = log.get("agent_name", "system")
            task_id = log.get("task_id", "-")
            action = log.get("action_type", "")
            detail = log.get("action_detail", "")
            outcome = log.get("outcome", "")

            line = f"[{ts}] [{agent}] T{task_id} | {action} → {outcome}"
            if detail:
                line += f": {detail[:120]}"
            formatted.append(line)

        return "\n".join(formatted)