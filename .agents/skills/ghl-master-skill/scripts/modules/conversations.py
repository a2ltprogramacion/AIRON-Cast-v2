from typing import Dict, Any

def handle_conversations(client, action: str, params: Dict[str, Any]):
    if action == "search_conversations":
        return search_conversations(client, params)
    elif action == "send_message":
        return send_message(client, params)
    elif action == "get_conversation":
        return get_conversation(client, params)
    elif action == "get_messages":
        return get_messages(client, params)
    elif action == "list_templates":
        return list_templates(client, params)
    elif action == "create_template":
        return create_template(client, params)
    elif action == "update_template":
        return update_template(client, params)
    elif action == "delete_template":
        return delete_template(client, params)
    return {"error": f"Unknown action {action} in module conversations"}

def search_conversations(client, params: Dict[str, Any]):
    location_id = params.get("locationId") or client.auth.get_location_id()
    path = f"/conversations/search?locationId={location_id}"
    if "contactId" in params:
        path += f"&contactId={params['contactId']}"
    headers = {"Version": "2021-04-15"}
    return client.request("GET", path, headers=headers)

def send_message(client, params: Dict[str, Any]):
    path = "/conversations/messages"
    headers = {"Version": "2021-04-15"}
    return client.request("POST", path, json=params, headers=headers)

def get_messages(client, params: Dict[str, Any]):
    conversation_id = params.get("conversationId")
    if not conversation_id: return {"error": "conversationId is required"}
    path = f"/conversations/{conversation_id}/messages"
    headers = {"Version": "2021-04-15"}
    return client.request("GET", path, headers=headers)

def list_templates(client, params: Dict[str, Any]):
    location_id = params.get("locationId") or client.auth.get_location_id()
    template_type = params.get("type", "").upper()
    if template_type == "EMAIL":
        path = f"/emails/builder?locationId={location_id}"
        return client.request("GET", path, headers={"Version": "2021-07-28"})
    path = f"/locations/{location_id}/templates"
    return client.request("GET", path, headers={"Version": "2021-07-28"})

def create_template(client, params: Dict[str, Any]):
    location_id = params.get("locationId") or client.auth.get_location_id()
    template_type = params.get("type", "EMAIL").upper()
    if template_type == "EMAIL":
        path = "/emails/builder"
        payload = {
            "locationId": location_id, "title": params.get("title", params.get("name")),
            "type": "html", "builderVersion": "2", "name": params.get("name"),
            "subjectLine": params.get("subject", params.get("subjectLine")), 
            "html": params.get("body", params.get("html", "")),
            "isPlainText": params.get("isPlainText", False)
        }
        if "updatedBy" in params: payload["updatedBy"] = params["updatedBy"]
        if "parentId" in params: payload["parentId"] = params["parentId"]
        return client.request("POST", path, json=payload, headers={"Version": "2021-07-28"})
    return {"error": "SMS creation not supported in v2 via PIT"}

def update_template(client, params: Dict[str, Any]):
    template_id = params.get("templateId") or params.get("id")
    if not template_id: return {"error": "templateId is required"}
    location_id = params.get("locationId") or client.auth.get_location_id()
    
    # Update Metadata (PATCH)
    patch_path = f"/emails/builder/{template_id}"
    patch_payload = {
        "locationId": location_id,
        "name": params.get("name"),
        "subjectLine": params.get("subject") or params.get("subjectLine"),
        "previewText": params.get("previewText"),
        "fromName": params.get("fromName"),
        "fromEmail": params.get("fromEmail"),
        "editorContent": params.get("body") or params.get("html"),
        "editorType": params.get("editorType", "html")
    }
    if "updatedBy" in params: patch_payload["updatedBy"] = params["updatedBy"]
    # Remove None values to avoid overwriting with nulls
    patch_payload = {k: v for k, v in patch_payload.items() if v is not None}
    client.request("PATCH", patch_path, json=patch_payload, headers={"Version": "2021-07-28"})
    
    # Update Content (POST /data)
    data_path = "/emails/builder/data"
    data_payload = {
        "locationId": location_id, "templateId": template_id,
        "html": params.get("body") or params.get("html", ""),
        "dnd": params.get("dnd", "{elements:[], attrs:{}, templateSettings:{}}"),
        "editorType": params.get("editorType", "html")
    }
    if "updatedBy" in params: data_payload["updatedBy"] = params["updatedBy"]
    return client.request("POST", data_path, json=data_payload, headers={"Version": "2021-07-28"})

def delete_template(client, params: Dict[str, Any]):
    template_id = params.get("templateId") or params.get("id")
    location_id = params.get("locationId") or client.auth.get_location_id()
    path = f"/emails/builder/{location_id}/{template_id}"
    return client.request("DELETE", path, headers={"Version": "2021-07-28"})
