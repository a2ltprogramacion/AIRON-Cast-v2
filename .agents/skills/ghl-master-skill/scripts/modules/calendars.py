from typing import Dict, Any

def handle_calendars(client, action: str, params: Dict[str, Any]):
    if action == "list_calendars":
        return list_calendars(client, params)
    elif action == "create_appointment":
        return create_appointment(client, params)
    elif action == "list_appointments":
        return list_appointments(client, params)
    elif action == "update_appointment":
        return update_appointment(client, params)
    elif action == "delete_appointment":
        return delete_appointment(client, params)
    elif action == "get_free_slots":
        return get_free_slots(client, params)
    elif action == "get_resources":
        return get_resources(client, params)
    return {"error": f"Unknown action {action} in module calendars"}

def list_calendars(client, params: Dict[str, Any]):
    location_id = params.get("locationId") or client.auth.get_location_id()
    path = f"/calendars/?locationId={location_id}"
    return client.get(path)

def create_appointment(client, params: Dict[str, Any]):
    path = "/calendars/events/appointments"
    if "locationId" not in params:
        params["locationId"] = client.auth.get_location_id()
    headers = {"Version": "2021-04-15"}
    return client.request("POST", path, json=params, headers=headers)

def list_appointments(client, params: Dict[str, Any]):
    contact_id = params.get("contactId")
    if not contact_id:
        location_id = params.get("locationId") or client.auth.get_location_id()
        path = f"/calendars/events?locationId={location_id}"
        return client.get(path)
        
    path = f"/contacts/{contact_id}/appointments"
    headers = {"Version": "2021-04-15"}
    return client.request("GET", path, headers=headers)

def update_appointment(client, params: Dict[str, Any]):
    event_id = params.get("eventId")
    path = f"/calendars/events/appointments/{event_id}"
    headers = {"Version": "2021-04-15"}
    payload = {k: v for k, v in params.items() if k != "eventId"}
    return client.request("PUT", path, json=payload, headers=headers)

def delete_appointment(client, params: Dict[str, Any]):
    event_id = params.get("eventId")
    path = f"/calendars/events/{event_id}"
    headers = {"Version": "2021-04-15"}
    return client.request("DELETE", path, headers=headers)

def get_free_slots(client, params: Dict[str, Any]):
    calendar_id = params.get("calendarId")
    path = f"/calendars/{calendar_id}/free-slots"
    headers = {"Version": "2021-04-15"}
    filtered = {k: v for k, v in params.items() if k != "calendarId"}
    return client.request("GET", path, params=filtered, headers=headers)

def get_resources(client, params: Dict[str, Any]):
    resource_type = params.get("resourceType", "equipments") # "equipments" or "rooms"
    resource_id = params.get("id")
    location_id = params.get("locationId") or client.auth.get_location_id()
    
    path = f"/calendars/resources/{resource_type}"
    if resource_id:
        path += f"/{resource_id}"
        
    headers = {"Version": "2021-04-15"}
    return client.request("GET", path, params={"locationId": location_id}, headers=headers)
