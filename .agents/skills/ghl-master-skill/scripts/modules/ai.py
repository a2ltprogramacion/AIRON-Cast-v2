from typing import Dict, Any

def handle_ai(client, action: str, params: Dict[str, Any]):
    if action == "list_conversation_ai_agents":
        return list_conversation_ai_agents(client, params)
    elif action == "list_voice_ai_agents":
        return list_voice_ai_agents(client, params)
    elif action == "list_agent_studio_agents":
        return list_agent_studio_agents(client, params)
    return {"error": f"Unknown action {action} in module ai"}

def list_conversation_ai_agents(client, params: Dict[str, Any]):
    # GHL API v2: GET /conversation-ai/agents/search
    # Note: locationId is inferred from token, but we can pass it as a safety param if needed
    path = "/conversation-ai/agents/search"
    response = client.get(path)
    
    # Normalize response
    agents_raw = response.get("agents", response.get("data", []))
    if isinstance(agents_raw, dict) and "id" in agents_raw:
        agents_raw = [agents_raw]
        
    normalized = []
    for agent in agents_raw:
        normalized.append({
            "id": agent.get("id", "unknown"),
            "name": agent.get("name", "(unnamed)"),
            "mode": agent.get("mode", "unknown"),
            "channels": agent.get("channels", []),
            "sleepEnabled": agent.get("sleepEnabled", False)
        })
    return {"agents": normalized, "count": len(normalized)}

def list_voice_ai_agents(client, params: Dict[str, Any]):
    # Placeholder for Voice AI API (To be expanded via NotebookLM specs)
    return {"error": "Voice AI agents listing not yet implemented in API 2.0 module"}

def list_agent_studio_agents(client, params: Dict[str, Any]):
    # Placeholder for Agent Studio API
    return {"error": "Agent Studio listing not yet implemented in API 2.0 module"}
