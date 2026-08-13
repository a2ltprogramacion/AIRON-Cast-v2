from core.client import GHLClient
from typing import Dict, Any

def handle_custom_values(client: GHLClient, action: str, params: Dict[str, Any], location_id: str) -> Dict[str, Any]:
    if action == "list_values":
        return list_values(client, location_id)
    elif action == "create_value":
        return create_value(client, params, location_id)
    elif action == "update_value":
        return update_value(client, params, location_id)
    elif action == "delete_value":
        return delete_value(client, params, location_id)
    else:
        return {"error": f"Unknown action {action} in module custom_values"}

def list_values(client: GHLClient, location_id: str):
    path = f"/locations/{location_id}/customValues"
    headers = {"Version": "2021-07-28"}
    return client.request("GET", path, headers=headers)

def create_value(client: GHLClient, params: Dict[str, Any], location_id: str):
    path = f"/locations/{location_id}/customValues"
    headers = {"Version": "2021-07-28"}
    return client.request("POST", path, json=params, headers=headers)

def update_value(client: GHLClient, params: Dict[str, Any], location_id: str):
    value_id = params.get("id")
    if not value_id:
        return {"error": "Missing 'id' parameter"}
    path = f"/locations/{location_id}/customValues/{value_id}"
    headers = {"Version": "2021-07-28"}
    payload = {k: v for k, v in params.items() if k != "id"}
    return client.request("PUT", path, json=payload, headers=headers)

def delete_value(client: GHLClient, params: Dict[str, Any], location_id: str):
    value_id = params.get("id")
    if not value_id:
        return {"error": "Missing 'id' parameter"}
    path = f"/locations/{location_id}/customValues/{value_id}"
    headers = {"Version": "2021-07-28"}
    return client.request("DELETE", path, headers=headers)
