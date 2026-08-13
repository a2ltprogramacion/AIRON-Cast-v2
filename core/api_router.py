"""
AIRON-Cast — API Router
========================
Caché de respuestas de modelos y notificaciones de cambio de modelo.
No invoca APIs directamente; el Operador cambia el modelo manualmente.

Uso:
    from core.api_router import APIRouter
    router = APIRouter()
    cached = router.check_cache(prompt_hash, agent_profile)
    router.notify_model_change(suggested, reason)
"""

import sqlite3
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional, Tuple

DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "central_intelligence.db"


class APIRouter:
    """
    Gestor de caché de respuestas y notificaciones al Operador.
    """

    def __init__(self, db_path: Optional[Path] = None):
        self.db_path = db_path or DEFAULT_DB_PATH

    # ------------------------------------------------------------------
    # CACHÉ DE RESPUESTAS
    # ------------------------------------------------------------------

    def check_cache(self, prompt_hash: str, agent_profile: str) -> Optional[str]:
        """
        Busca en response_cache una respuesta previa para el mismo
        prompt_hash y agente. Si existe, actualiza last_used y la devuelve.
        """
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT response_text, tokens_used, model_used
                FROM response_cache
                WHERE prompt_hash = ? AND agent_profile = ?
                ORDER BY last_used DESC
                LIMIT 1
                """,
                (prompt_hash, agent_profile),
            ).fetchone()

            if row:
                conn.execute(
                    """
                    UPDATE response_cache
                    SET last_used = ?
                    WHERE prompt_hash = ? AND agent_profile = ?
                    """,
                    (datetime.now(timezone.utc).isoformat(), prompt_hash, agent_profile),
                )
                conn.commit()
                return row["response_text"]
            return None

    def store_response(
        self,
        prompt_hash: str,
        agent_profile: str,
        response_text: str,
        tokens_used: int = 0,
        model_used: str = "unknown",
    ) -> None:
        """
        Almacena una respuesta en la caché para futuras consultas.
        """
        with self._connect() as conn:
            conn.execute(
                """
                INSERT INTO response_cache
                    (prompt_hash, agent_profile, response_text, tokens_used, model_used)
                VALUES (?, ?, ?, ?, ?)
                """,
                (prompt_hash, agent_profile, response_text, tokens_used, model_used),
            )
            conn.commit()

    # ------------------------------------------------------------------
    # NOTIFICACIÓN DE CAMBIO DE MODELO
    # ------------------------------------------------------------------

    def notify_model_change(self, suggested_model: str, reason: str) -> None:
        """
        Imprime una notificación visible para el Operador recomendando
        cambiar de modelo. No detiene el proceso.
        """
        message = (
            f"\n{'='*60}\n"
            f"[ALERTA DE MOTOR]: Se recomienda cambiar a {suggested_model}.\n"
            f"Motivo: {reason}\n"
            f"Acción manual requerida por el Operador.\n"
            f"{'='*60}\n"
        )
        print(message)

    # ------------------------------------------------------------------
    # HASH DE PROMPT
    # ------------------------------------------------------------------

    @staticmethod
    def hash_prompt(prompt: str) -> str:
        """Genera un hash SHA256 del prompt para indexar en caché."""
        return hashlib.sha256(prompt.encode("utf-8")).hexdigest()

    # ------------------------------------------------------------------
    # CONEXIÓN INTERNA
    # ------------------------------------------------------------------

    def _connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn