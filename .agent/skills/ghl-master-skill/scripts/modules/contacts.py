from typing import Dict, Any

def handle_contacts(client, action: str, params: Dict[str, Any]):
    if action == "list_contacts":
        return list_contacts(client, params)
    elif action == "search_contacts":
        return search_contacts(client, params)
    elif action == "create_contact":
        return create_contact(client, params)
    elif action == "update_contact":
        return update_contact(client, params)
    return {"error": f"Unknown action {action} in module contacts"}

def list_contacts(client, params: Dict[str, Any]):
    # GHL API v2: GET /contacts/ (El motor principal de listado)
    if "locationId" not in params:
        params["locationId"] = client.auth.get_location_id()
    
    # Normalizamos el límite
    if "limit" in params and "pageLimit" not in params:
        params["pageLimit"] = params.pop("limit")
    elif "pageLimit" not in params:
        params["pageLimit"] = 20

    return client.request("GET", "/contacts/", params=params)

def search_contacts(client, params: Dict[str, Any]):
    path = "/contacts/search"
    if "locationId" not in params:
        params["locationId"] = client.auth.get_location_id()
    
    # API v2 normalization
    # 1. 'q' -> 'query'
    if "q" in params and "query" not in params:
        params["query"] = params.pop("q")
    
    # 2. 'limit' -> 'pageLimit'
    if "limit" in params and "pageLimit" not in params:
        params["pageLimit"] = params.pop("limit")
    elif "pageLimit" not in params:
        params["pageLimit"] = 10
        
    headers = {"Version": "2021-07-28"}
    return client.request("POST", path, json=params, headers=headers)

def create_contact(client, params: Dict[str, Any]):
    # GHL API v2: POST /contacts/
    path = "/contacts/"
    if "locationId" not in params:
        params["locationId"] = client.auth.get_location_id()
    headers = {"Version": "2021-07-28"}
    return client.request("POST", path, json=params, headers=headers)

def update_contact(client, params: Dict[str, Any]):
    # GHL API v2: PUT /contacts/{contactId}
    contact_id = params.pop("contactId", None)
    if not contact_id:
        return {"error": "contactId is required for update_contact"}
        
    path = f"/contacts/{contact_id}"
    headers = {"Version": "2021-07-28"}
    return client.request("PUT", path, json=params, headers=headers)
