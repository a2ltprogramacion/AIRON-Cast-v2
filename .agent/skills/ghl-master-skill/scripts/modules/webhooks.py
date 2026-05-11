from typing import Dict, Any

def handle_webhooks(client, action: str, params: Dict[str, Any], location_id: str):
    """
    Dispatcher para acciones de Webhooks en GHL API 2.0.
    """
    try:
        if action == "list_subscriptions":
            return client.request("GET", f"/webhooks/subscriptions?locationId={location_id}")
            
        elif action == "create_subscription":
            # Aseguramos que el locationId esté en el body si no viene en params
            if "locationId" not in params:
                params["locationId"] = location_id
            return client.request("POST", "/webhooks/subscriptions", json=params)
            
        elif action == "delete_subscription":
            sub_id = params.get("subscription_id")
            if not sub_id:
                return {"error": "Se requiere 'subscription_id' para eliminar la suscripción"}
            return client.request("DELETE", f"/webhooks/subscriptions/{sub_id}?locationId={location_id}")
            
        else:
            return {"error": f"Acción '{action}' no implementada en el módulo webhooks"}
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
