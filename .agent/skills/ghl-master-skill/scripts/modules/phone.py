from core.client import GHLClient
from typing import Dict, Any, Optional

class GHLPhoneSystem:
    """Módulo base para gestionar Phone Numbers (Pilar 5 - Mensajería)."""
    def __init__(self, client: GHLClient):
        self.client = client

    def get_location_numbers(self, location_id: str, skip: int = 0, limit: int = 20) -> Dict[str, Any]:
        """
        Devuelve la lista de números de teléfono asignados a la subcuenta.
        GET /phone-system/numbers/location/{locationId}
        """
        path = f"/phone-system/numbers/location/{location_id}"
        return self.client.request("GET", path, params={"skip": skip, "limit": limit}, headers={"Version": "2021-04-15"})

def handle_phone_system(client: GHLClient, action: str, params: Dict[str, Any], location_id: str) -> Dict[str, Any]:
    """Despachador del módulo Phone System"""
    phone = GHLPhoneSystem(client)
    
    if action == "get_location_numbers":
        return phone.get_location_numbers(
            location_id,
            skip=params.get("skip", 0),
            limit=params.get("limit", 20)
        )
    else:
        raise ValueError(f"Acción no soportada en el módulo Phone: {action}")
