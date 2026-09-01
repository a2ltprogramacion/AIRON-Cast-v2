from core.client import GHLClient
from typing import Dict, Any

def handle_custom_objects(client: GHLClient, action: str, params: Dict[str, Any], location_id: str) -> Dict[str, Any]:
    if action == "list_schemas":
        return list_schemas(client, location_id)
    elif action == "create_schema":
        return create_schema(client, params, location_id)
    elif action == "search_records":
        return search_records(client, params, location_id)
    elif action == "get_record":
        return get_record(client, params, location_id)
    elif action == "create_record":
        return create_record(client, params, location_id)
    elif action == "update_record":
        return update_record(client, params, location_id)
    elif action == "delete_record":
        return delete_record(client, params, location_id)
    else:
        return {"error": f"Unknown action {action} in module custom_objects"}

def list_schemas(client: GHLClient, location_id: str):
    path = f"/objects/?locationId={location_id}"
    headers = {"Version": "2021-07-28"} # Assuming standard v2 version wrapper
    return client.request("GET", path, headers=headers)

def create_schema(client: GHLClient, params: Dict[str, Any], location_id: str):
    path = "/objects/"
    headers = {"Version": "2021-07-28"}
    
    # Inject locationId if not passed in params
    payload = params.copy()
    if "locationId" not in payload:
        payload["locationId"] = location_id
        
    return client.request("POST", path, json=payload, headers=headers)

def search_records(client: GHLClient, params: Dict[str, Any], location_id: str):
    schema_key = params.get("schemaKey")
    if not schema_key:
        return {"error": "Missing 'schemaKey' parameter"}
    
    path = f"/objects/{schema_key}/records/search"
    headers = {"Version": "2021-07-28"}
    
    payload = {k: v for k, v in params.items() if k != "schemaKey"}
    payload["locationId"] = location_id
    
    return client.request("POST", path, json=payload, headers=headers)

def get_record(client: GHLClient, params: Dict[str, Any], location_id: str):
    schema_key = params.get("schemaKey")
    record_id = params.get("id") or params.get("recordId")
    if not schema_key or not record_id:
        return {"error": "Missing 'schemaKey' or 'id' parameter"}
        
    path = f"/objects/{schema_key}/records/{record_id}"
    headers = {"Version": "2021-07-28"}
    return client.request("GET", path, headers=headers)

def create_record(client: GHLClient, params: Dict[str, Any], location_id: str):
    schema_key = params.get("schemaKey")
    if not schema_key:
        return {"error": "Missing 'schemaKey' parameter"}
        
    path = f"/objects/{schema_key}/records"
    headers = {"Version": "2021-07-28"}
    payload = {k: v for k, v in params.items() if k != "schemaKey"}
    
    # Needs locationId according to some docs, though snippet shows nothing. Assumed in JSON body.
    payload["locationId"] = location_id
    
    return client.request("POST", path, json=payload, headers=headers)

def update_record(client: GHLClient, params: Dict[str, Any], location_id: str):
    schema_key = params.get("schemaKey")
    record_id = params.get("id") or params.get("recordId")
    if not schema_key or not record_id:
        return {"error": "Missing 'schemaKey' or 'id' parameter"}
        
    # Snippet states ?locationId= is needed for PUT
    path = f"/objects/{schema_key}/records/{record_id}?locationId={location_id}"
    headers = {"Version": "2021-07-28"}
    
    payload = {k: v for k, v in params.items() if k not in ["schemaKey", "id", "recordId"]}
    
    return client.request("PUT", path, json=payload, headers=headers)

def delete_record(client: GHLClient, params: Dict[str, Any], location_id: str):
    schema_key = params.get("schemaKey")
    record_id = params.get("id") or params.get("recordId")
    if not schema_key or not record_id:
        return {"error": "Missing 'schemaKey' or 'id' parameter"}
        
    path = f"/objects/{schema_key}/records/{record_id}"
    headers = {"Version": "2021-07-28"}
    return client.request("DELETE", path, headers=headers)

