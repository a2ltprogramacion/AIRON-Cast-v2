import argparse
import sys
import json
import os
import asyncio

# Add current directory to path to allow absolute imports of core/modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from core.auth import GHLAuth
from core.client import GHLClient

from modules.contacts import handle_contacts
from modules.calendars import handle_calendars
from modules.ai import handle_ai
from modules.automations import handle_automations
from modules.pipelines import handle_pipelines
from modules.conversations import handle_conversations
from modules.phone import handle_phone_system
from modules.custom_values import handle_custom_values
from modules.custom_objects import handle_custom_objects
from modules.social import handle_social
from modules.forms import handle_forms
from modules.webhooks import handle_webhooks
from modules.opportunities import handle_opportunities

def handle_system(client, action, params):
    if action == "health_check":
        try:
            # Verify auth by listing calendars (minimal cost call)
            location_id = client.auth.get_location_id()
            client.get(f"/calendars/?locationId={location_id}")
            return {"status": "connected", "location_id": location_id}
        except Exception as e:
            return {"status": "failed", "error": str(e)}
    return {"error": f"Unknown action {action} in module system"}

def main():
    parser = argparse.ArgumentParser(description="GHL Master Skill v2.0 Dispatcher")
    parser.add_argument("--module", required=True, help="Module: contacts, calendars, pipelines, automations, ai, system, social")
    parser.add_argument("--action", required=True, help="Action to perform")
    parser.add_argument("--params", type=str, default='{}', help="JSON string of parameters")
    
    args = parser.parse_args()
    
    try:
        if args.params.startswith("'") and args.params.endswith("'"):
            args.params = args.params[1:-1]
        params = json.loads(args.params)
    except json.JSONDecodeError:
        print(f"Error: --params must be a valid JSON string. Received: {args.params}")
        sys.exit(1)

    try:
        auth = GHLAuth()
        client = GHLClient(auth)

        result = None
        if args.module == "system":
            result = handle_system(client, args.action, params)
        elif args.module == "contacts":
            result = handle_contacts(client, args.action, params)
        elif args.module == "calendars":
            result = handle_calendars(client, args.action, params)
        elif args.module == "ai":
            result = handle_ai(client, args.action, params)
        elif args.module == "automations":
            result = handle_automations(client, args.action, params)
        elif args.module == "pipelines":
            result = handle_pipelines(client, args.action, params)
        elif args.module == "conversations":
            result = handle_conversations(client, args.action, params)
        elif args.module == "phone":
            result = handle_phone_system(client, args.action, params, auth.get_location_id())
        elif args.module == "custom_values":
            result = handle_custom_values(client, args.action, params, auth.get_location_id())
        elif args.module == "custom_objects":
            result = handle_custom_objects(client, args.action, params, auth.get_location_id())
        elif args.module == "social":
            result = handle_social(client, args.action, params, auth.get_location_id())
        elif args.module == "forms":
            result = handle_forms(client, args.action, params, auth.get_location_id())
        elif args.module == "webhooks":
            result = handle_webhooks(client, args.action, params, auth.get_location_id())
        elif args.module == "opportunities":
            result = handle_opportunities(client, args.action, params, auth.get_location_id())
        else:
            result = {"error": f"Module '{args.module}' not implemented."}

        print(json.dumps(result, indent=2))
        
    except Exception as e:
        print(json.dumps({"status": "error", "message": str(e)}, indent=2))
        sys.exit(1)

if __name__ == "__main__":
    main()
