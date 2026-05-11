from typing import Dict, Any

def handle_opportunities(client, action: str, params: Dict[str, Any], location_id: str):
    """
    Dispatcher para el Pilar 8: Opportunities (Motor Comercial).
    Unifica la gestión de Pipelines y Business Deals.
    """
    try:
        if action == "list_pipelines":
            # API v2: GET /opportunities/pipelines
            return client.request("GET", f"/opportunities/pipelines?locationId={location_id}")
            
        elif action == "search":
            # API v2: GET /opportunities/search (usa snake_case en query params)
            query_params = {
                "location_id": location_id,
                "pipeline_id": params.get("pipeline_id") or params.get("pipelineId"),
                "contact_id": params.get("contact_id") or params.get("contactId"),
                "status": params.get("status"), # open, won, lost, abandoned, all
                "q": params.get("query") or params.get("q")
            }
            # Limpiar nulos
            query_params = {k: v for k, v in query_params.items() if v is not None}
            return client.request("GET", "/opportunities/search", params=query_params)
            
        elif action == "get":
            opp_id = params.get("opportunity_id") or params.get("id")
            if not opp_id: return {"error": "Se requiere 'opportunity_id'"}
            return client.request("GET", f"/opportunities/{opp_id}")
            
        elif action == "create":
            # API v2: POST /opportunities/
            if "locationId" not in params:
                params["locationId"] = location_id
            # GHL requiere obligatoriamente: pipelineId, pipelineStageId, name, status, contactId
            return client.request("POST", "/opportunities/", json=params)
            
        elif action == "update":
            # API v2: PUT /opportunities/{opportunityId}
            opp_id = params.pop("opportunity_id", None) or params.pop("id", None)
            if not opp_id: return {"error": "Se requiere 'opportunity_id'"}
            return client.request("PUT", f"/opportunities/{opp_id}", json=params)
            
        elif action == "delete":
            # API v2: DELETE /opportunities/{opportunityId}
            opp_id = params.get("opportunity_id") or params.get("id")
            if not opp_id: return {"error": "Se requiere 'opportunity_id'"}
            return client.request("DELETE", f"/opportunities/{opp_id}")
            
        else:
            return {"error": f"Acción '{action}' no soportada en el módulo opportunities"}
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
