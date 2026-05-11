from typing import Dict, Any

def handle_pipelines(client, action: str, params: Dict[str, Any]):
    if action == "list_pipelines":
        return list_pipelines(client, params)
    elif action == "get_pipeline":
        return get_pipeline(client, params)
    elif action == "search_opportunities":
        return search_opportunities(client, params)
    elif action == "create_opportunity":
        return create_opportunity(client, params)
    elif action == "update_opportunity":
        return update_opportunity(client, params)
    return {"error": f"Unknown action {action} in module pipelines"}

def list_pipelines(client, params: Dict[str, Any]):
    location_id = params.get("locationId") or client.auth.get_location_id()
    path = f"/opportunities/pipelines?locationId={location_id}"
    return client.get(path)

def get_pipeline(client, params: Dict[str, Any]):
    pipeline_id = params.get("pipelineId")
    if not pipeline_id: return {"error": "pipelineId is required"}
    location_id = params.get("locationId") or client.auth.get_location_id()
    path = f"/opportunities/pipelines/{pipeline_id}?locationId={location_id}"
    return client.get(path)

def search_opportunities(client, params: Dict[str, Any]):
    # GHL API v2 Search (GET) uses snake_case: location_id, contact_id, pipeline_id
    location_id = params.get("locationId") or params.get("location_id") or client.auth.get_location_id()
    
    query_params = {
        "location_id": location_id,
        "contact_id": params.get("contactId") or params.get("contact_id"),
        "pipeline_id": params.get("pipelineId") or params.get("pipeline_id"),
        "q": params.get("q"),
        "status": params.get("status")
    }
    # Remove None values
    query_params = {k: v for k, v in query_params.items() if v is not None}
    
    path = "/opportunities/search"
    return client.get(path, params=query_params)

def create_opportunity(client, params: Dict[str, Any]):
    # GHL API v2: POST /opportunities/
    path = "/opportunities/"
    if "locationId" not in params:
        params["locationId"] = client.auth.get_location_id()
    
    # Requirement: pipelineId, contactId, name, status
    headers = {"Version": "2021-07-28"}
    return client.request("POST", path, json=params, headers=headers)

def update_opportunity(client, params: Dict[str, Any]):
    # GHL API v2: PUT /opportunities/{opportunityId}
    opportunity_id = params.pop("opportunityId", None)
    if not opportunity_id:
        return {"error": "opportunityId is required for update_opportunity"}
        
    path = f"/opportunities/{opportunity_id}"
    headers = {"Version": "2021-07-28"}
    return client.request("PUT", path, json=params, headers=headers)
