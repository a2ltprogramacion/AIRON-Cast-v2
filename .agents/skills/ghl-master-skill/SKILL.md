---
name: ghl-master-skill
version: 2.2.0
type: execution
subtype: skill
tier: enterprise
description: |
  Master Skill definitiva para GoHighLevel API 2.0. Reúne CRM, Oportunidades, 
  Calendarios, Automatizaciones, IA y Conversaciones en un único componente modular robusto.
  Sustituye a todas las skills individuales ghl-list-*.

triggers:
  primary: ["ghl", "gohighlevel", "crm", "api 2.0"]
  secondary: ["pipelines", "oportunidades", "calendario", "workflow", "ai agent", "conversations", "messages"]

inputs:
  - name: module
    type: string
    required: true
    description: "Módulo: contacts, calendars, pipelines, automations, ai, conversations, system"
  - name: action
    type: string
    required: true
    description: "Acción a ejecutar"
  - name: params
    type: object
    required: false
    description: "Parámetros JSON de la acción"

outputs:
  - name: result
    type: object
    description: "Respuesta de la API GHL"

dependencies:
  - name: httpx
    version: ">=0.24.0"
  - name: python-dotenv
    version: ">=1.0.0"

entrypoint: scripts/main.py
---

# GHL Master Skill v2.2

Motor unificado de orquestación para el ecosistema GoHighLevel.

## Módulos Disponibles

### 1. CRM (Contacts & Pipelines)
- **Module**: `contacts`
  - `search_contacts`: Búsqueda avanzada de contactos.
  - `create_contact`: Crea un prospecto.
  - `update_contact`: Actualiza datos de un lead.
- **Module**: `pipelines`
  - `list_pipelines`: Lista todos los embudos de la subcuenta.
  - `search_opportunities`: Filtra oportunidades.
  - `create_opportunity`: Crea una oportunidad vinculada.
  - `update_opportunity`: Cambia etapa o estado.

### 2. Agendamiento (Calendars)
- **Module**: `calendars`
  - `list_calendars`: Lista calendarios activos.
  - `list_appointments`: Citas por contacto o ubicación.
  - `create_appointment`: Agenda una cita (v2).

### 3. Conversaciones (Conversations) [NEW]
- **Module**: `conversations`
  - `search_conversations`: Listado de hilos por ubicación.
  - `send_message`: Envío omnicanal (SMS, Email, WA).
  - `get_messages`: Historial de mensajes de un hilo.
  - `list_templates`: Listado de plantillas SMS/Email.

### 4. Automatización (Automations)
- **Module**: `automations`
  - `list_workflows`: Lista los flujos de trabajo instalados.

### 5. Inteligencia Artificial (AI)
- **Module**: `ai`
  - `list_conversation_ai_agents`: Catálogo de agentes de chat.

## Uso Técnico

```bash
python scripts/main.py --module <modulo> --action <accion> --params '{"key": "value"}'
```

## Autenticación
Maneja automáticamente las credenciales en `.env` (PIT + OAuth2).
