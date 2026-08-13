#!/usr/bin/env python3
"""
HITL Gateway — OpenCode ⊕ AIRON-Cast Fusion
Notificación al operador (Modo B) cuando se detecta desviación/stop-loss.
"""
import json
import os
import subprocess
import sys
from pathlib import Path
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class HITLReason(Enum):
    STOP_LOSS = "stop_loss"
    RETRY_EXHAUSTED = "retry_exhausted"
    SCOPE_VIOLATION = "scope_violation"
    CHECKSUM_MISMATCH = "checksum_mismatch"
    ARCH_DECISION_NO_ADR = "arch_decision_no_adr"
    META_FACTORY_PATCH = "meta_factory_patch"
    AGENT_DEVIATION = "agent_deviation"

class HITLGateway:
    def __init__(self, mode: str = "B"):
        """
        Modo A: Bloqueo total (requiere confirmación para continuar)
        Modo B: Notificación (continúa ejecutando, solo avisa)
        """
        self.mode = mode.upper()
        self.notifications_log = Path.home() / ".opencode" / "hitl_notifications.jsonl"
        self.notifications_log.parent.mkdir(parents=True, exist_ok=True)
    
    def notify(self, reason: HITLReason, details: Dict[str, Any]) -> None:
        """Envía notificación al operador según modo."""
        notification = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason.value,
            "details": details,
            "mode": self.mode,
            "project": os.environ.get("OPENCODE_PROJECT_SLUG", "unknown"),
            "agent": os.environ.get("OPENCODE_AGENT", "unknown"),
        }
        
        # Log persistente
        with open(self.notifications_log, "a", encoding="utf-8") as f:
            f.write(json.dumps(notification, ensure_ascii=False) + "\n")
        
        # Notificación según modo
        if self.mode == "A":
            self._blocking_notify(notification)
        else:
            self._non_blocking_notify(notification)
    
    def _blocking_notify(self, notification: Dict) -> None:
        """Modo A: Bloquea y espera confirmación."""
        print("\n" + "="*60, file=sys.stderr)
        print("🛑 HITL BLOQUEANTE - REQUIERE CONFIRMACIÓN", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print(f"Razón: {notification['reason']}", file=sys.stderr)
        print(f"Proyecto: {notification['project']}", file=sys.stderr)
        print(f"Agente: {notification['agent']}", file=sys.stderr)
        print(f"Detalles: {json.dumps(notification['details'], indent=2, ensure_ascii=False)}", file=sys.stderr)
        print("="*60, file=sys.stderr)
        print("Presiona ENTER para continuar o Ctrl+C para abortar...", file=sys.stderr)
        sys.stderr.flush()
        input()
    
    def _non_blocking_notify(self, notification: Dict) -> None:
        """Modo B: Notifica sin bloquear (Windows toast / terminal bell)."""
        # Windows: usa toast notification si disponible
        if sys.platform == "win32":
            try:
                import win10toast
                toaster = win10toast.ToastNotifier()
                toaster.show_toast(
                    f"⚠️ AIRON-Cast HITL: {notification['reason']}",
                    f"Proyecto: {notification['project']} | Agente: {notification['agent']}",
                    duration=10
                )
            except ImportError:
                pass  # fallback a terminal
        
        # Terminal bell + mensaje
        print(f"\a⚠️ HITL NOTIFICACIÓN: {notification['reason']} | "
              f"Proyecto: {notification['project']} | Agente: {notification['agent']}", 
              file=sys.stderr)
        
        # Log para revisión posterior
        self._log_for_review(notification)
    
    def _log_for_review(self, notification: Dict) -> None:
        """Registra para revisión en próxima interacción."""
        review_file = Path.home() / ".opencode" / "hitl_review.json"
        review_file.parent.mkdir(parents=True, exist_ok=True)
        
        reviews = []
        if review_file.exists():
            try:
                with open(review_file, "r") as f:
                    reviews = json.load(f)
            except:
                reviews = []
        
        reviews.append(notification)
        # Mantener últimos 50
        reviews = reviews[-50:]
        
        with open(review_file, "w") as f:
            json.dump(reviews, f, indent=2, ensure_ascii=False)
    
    def get_pending_reviews(self) -> list:
        """Obtiene notificaciones pendientes de revisión."""
        review_file = Path.home() / ".opencode" / "hitl_review.json"
        if review_file.exists():
            try:
                with open(review_file, "r") as f:
                    return json.load(f)
            except:
                pass
        return []
    
    def clear_reviews(self) -> None:
        """Limpia revisiones pendientes."""
        review_file = Path.home() / ".opencode" / "hitl_review.json"
        if review_file.exists():
            review_file.unlink()


# Instancia global (Modo B por defecto)
_gateway = HITLGateway(mode="B")

def get_hitl_gateway() -> HITLGateway:
    return _gateway

def notify_hitl(reason: str, details: Dict) -> None:
    """Helper rápido para notificar."""
    try:
        hitl_reason = HITLReason(reason)
    except ValueError:
        hitl_reason = HITLReason.AGENT_DEVIATION
    _gateway.notify(hitl_reason, details)


if __name__ == "__main__":
    gw = HITLGateway(mode="B")
    gw.notify(HITLReason.STOP_LOSS, {"task_id": 42, "retry_count": 3, "error": "Max retries exceeded"})
    print("Test notificación enviado")