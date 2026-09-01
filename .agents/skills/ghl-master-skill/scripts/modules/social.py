import os
def handle_social(client, action, params, location_id):
    """
    Dispatcher para acciones de Social Planner usando GHLClient (httpx).
    Bypasea el SDK oficial para evitar bugs de headers y versionado.
    """
    
    try:
        if action == "list_accounts":
            return client.request("GET", f"/social-media-posting/{location_id}/accounts")
        
        elif action == "get_account":
            account_id = params.get("account_id")
            if not account_id: return {"error": "Missing account_id"}
            return client.request("GET", f"/social-media-posting/{location_id}/accounts/{account_id}")

        elif action == "delete_account":
            account_id = params.get("account_id")
            if not account_id: return {"error": "Missing account_id"}
            return client.request("DELETE", f"/social-media-posting/{location_id}/accounts/{account_id}")
        
        elif action == "list_posts":
            # Requiere POST en v2 para listado con filtros
            return client.request("POST", f"/social-media-posting/{location_id}/posts/list", json=params)
        
        elif action == "get_post":
            post_id = params.get("post_id")
            if not post_id: return {"error": "Missing post_id"}
            return client.request("GET", f"/social-media-posting/{location_id}/posts/{post_id}")
        
        elif action == "create_post":
            return client.request("POST", f"/social-media-posting/{location_id}/posts", json=params)
        
        elif action == "delete_post":
            post_id = params.get("post_id")
            if not post_id: return {"error": "Missing post_id"}
            return client.request("DELETE", f"/social-media-posting/{location_id}/posts/{post_id}")
        
        elif action == "list_categories":
            return client.request("GET", f"/social-media-posting/{location_id}/categories")
        
        elif action == "list_tags":
            return client.request("GET", f"/social-media-posting/{location_id}/tags")
            
        else:
            return {"error": f"Acción '{action}' no implementada o desconocida en el módulo social (Raw)"}
            
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }
