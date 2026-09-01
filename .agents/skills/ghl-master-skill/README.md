# GHL Master Skill (API 2.0) — Guía Maestra de Capacidades

Esta skill modular es el núcleo de orquestación de **AIRON-Cast** para la integración con **GoHighLevel API 2.0**. Está diseñada para ser operada tanto por humanos como por agentes de IA, siguiendo estándares de código limpio y síncrono.

## 🚀 Arquitectura y Autenticación
- **Ruta Base de Scripts**: `.agent/skills/ghl-master-skill/scripts/`
- **Cliente**: `GHLClient` (Basado en `httpx`, síncrono).
- **Seguridad**: Soporte nativo para OAuth2 y Headers de Versión (`2021-07-28`).

## 🛠️ Diccionario de Módulos y Acciones

### 1. Sistema (`system`)
- `health_check`: Verifica la conectividad y validez del API Key/Token.

### 2. CRM y Contactos (`contacts`)
- `search_contacts`: Búsqueda avanzada por email, teléfono o nombre.
- `create_contact`: Registro de nuevos leads.
- `update_contact`: Actualización de perfiles existentes.

### 3. Calendarios y Citas (`calendars`)
- `list_groups`: Listar grupos de calendarios.
- `list_calendars`: Listar calendarios individuales.
- `get_slots`: Consultar disponibilidad de fechas.
- `list_appointments`: Ver citas programadas.
- `create_appointment`: Agendar nuevas citas.

### 4. Motor Comercial (`opportunities`) — [PILAR 8]
- `list_pipelines`: Listar todos los embudos de venta.
- `search`: Búsqueda de negocios (filtros por pipeline, estado, contacto).
- `create`: Crear una nueva oportunidad de negocio.
- `update`: Mover de etapa, cambiar valor o estado (won/lost).
- `get`: Detalles técnicos de un negocio.

### 5. Social Planner (`social`) — [PILAR 3]
*Nota: Implementación robusta vía Raw Requests para evitar bugs de SDK.*
- `list_accounts`: Ver cuentas de RRSS conectadas (FB, IG, LinkedIn, etc.).
- `list_posts`: Listar publicaciones programadas o enviadas.
- `create_post`: Publicar o programar contenido con soporte multimedia.
- `delete_post`: Eliminar publicaciones programadas.

### 6. Formularios y Captación (`forms`) — [PILAR 7]
- `list_forms`: Listar formularios disponibles en la ubicación.
- `get_submissions`: Recuperar envíos y datos de leads prospectados.

### 7. Webhooks (`webhooks`) — [PILAR 7]
- `list_subscriptions`: Ver suscripciones activas a eventos.
- `create_subscription`: Suscribir a eventos (ej. `contact.create`, `opportunity.change`).
- `delete_subscription`: Eliminar integración de webhook.

### 8. Datos Personalizados (`custom_values` / `custom_objects`)
- Gestión completa de campos personalizados y objetos de negocio a medida.

## 📂 Ejemplo de Ejecución (CLI)

Todo se orquesta mediante `main.py`:

```bash
# Ejemplo: Listar Oportunidades en un Pipeline específico
python main.py --module opportunities --action search --params '{"pipeline_id": "ID_DEL_PIPELINE"}'

# Ejemplo: Publicar en Redes Sociales
python main.py --module social --action create_post --params '{"account_id": "ID_CUENTA", "text": "Hola Mundo #A2LT"}'
```

---
**Desarrollado por:** A2LT Soluciones | **Project:** AIRON-Cast
