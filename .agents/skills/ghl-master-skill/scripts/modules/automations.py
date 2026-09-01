from typing import Dict, Any

def handle_automations(client, action: str, params: Dict[str, Any]):
    if action == "list_workflows":
        return list_workflows(client, params)
    return {"error": f"Unknown action {action} in module automations"}

def list_workflows(client, params: Dict[str, Any]):
    # GHL API v2: GET /workflows/
    location_id = params.get("locationId") or client.auth.get_location_id()
    path = f"/workflows/?locationId={location_id}"
    
    headers = {"Version": "2021-04-15"}
    response = client.request("GET", path, headers=headers)
    return response
