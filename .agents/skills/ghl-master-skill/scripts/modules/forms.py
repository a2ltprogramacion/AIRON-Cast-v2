from typing import Dict, Any

def handle_forms(client, action: str, params: Dict[str, Any], location_id: str):
    """
    Dispatcher para acciones de Formularios en GHL API 2.0.
    """
    try:
        if action == "list_forms":
            return client.request("GET", f"/forms/?locationId={location_id}")
            
        elif action == "get_submissions":
            form_id = params.get("form_id")
            path = f"/forms/submissions?locationId={location_id}"
            if form_id:
                path += f"&formId={form_id}"
            return client.request("GET", path)
            
        else:
            return {"error": f"Acción '{action}' no implementada en el módulo forms"}
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
