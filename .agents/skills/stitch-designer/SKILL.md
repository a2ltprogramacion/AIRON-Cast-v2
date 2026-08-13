---
name: stitch-designer
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Orchestrates and designs user interfaces using the StitchMCP server tools.
  Activate when the operator requests UI generation, mockup creation, or
  screen design via Stitch. Trigger phrases: "diseña pantalla", "usa stitch",
  "genera ui", "crea proyecto ux", "edita pantalla interactiva".
  Do NOT activate if StitchMCP is not configured or accessible.
triggers:
  primary: ["diseña pantalla", "usa stitch", "genera ui", "crea proyecto ux"]
  secondary: ["edita pantalla interactiva", "StitchMCP"]
  context: ["ui design", "mockup generation"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - ux-ui_specialist
  - frontend_worker
last_used: 2026-06-05
scope: restricted
---

# Stitch Designer — AIRON‑Cast

This skill provides instructions on how to efficiently operate the **StitchMCP**
server for the creation and management of user interfaces and UI projects.

---

## 0. Prerrequisitos

### 0.1 Verificación de Configuración MCP

Before any operation, verify that StitchMCP is configured in the operator's IDE.
If the MCP tool is not listed or connected, stop execution and ask the operator
to configure it using one of the following templates:

**Google Antigravity IDE:**
```json
{
  "mcpServers": {
    "stitch": {
      "serverUrl": "https://stitch.googleapis.com/mcp",
      "headers": {
        "X-Goog-Api-Key": "[API-KEY]"
      }
    }
  }
}
```

**OpenCode:**
```json
{
  "$schema": "https://opencode.ai/config.json",
  "mcp": {
    "stitch": {
      "type": "remote",
      "url": "https://stitch.googleapis.com/mcp",
      "enabled": true,
      "headers": {
        "X-Goog-Api-Key": "[API-KEY]"
      }
    }
  }
}
```

The `[API-KEY]` placeholder must be replaced with a valid Google API key
with StitchMCP access enabled.

---

## 1. Flujo de Trabajo Completo

### Paso 1: Verificar Proyectos Existentes

Start by calling `mcp_StitchMCP_list_projects` to see if the operator already
has projects. If a project name is mentioned, use it. If not, create a new one.

### Paso 2: Generar una Pantalla

Use `mcp_StitchMCP_generate_screen_from_text` with:
- `projectId`: project identifier
- `prompt`: detailed UI description (see §2 for examples)
- `deviceType`: MOBILE, DESKTOP, or TABLET (optional)

### Paso 3: Verificar la Generación

The generation process can be asynchronous. If a temporary connection failure
occurs, **DO NOT RETRY**. The server will complete the generation in the
background. Use `mcp_StitchMCP_list_screens` with the `projectId` to confirm
which screens have been generated.

### Paso 4: Iterar el Diseño

- **Selective editing:** `mcp_StitchMCP_edit_screens`
  (requires `projectId`, `selectedScreenIds` and `prompt`).
- **Alternative generation:** `mcp_StitchMCP_generate_variants`
  specifying the corresponding `variantOptions`.

### Paso 5: Exportar

When the design is approved, extract assets, design tokens, and specifications
to hand off to `frontend_worker` or `ux-ui_specialist`.

---

## 2. Reglas de Diseño de Prompts

When the operator requests a UI, assist by defining a deep architectural prompt:

- **Rich Aesthetics:** Avoid basic colors. Recommend color palettes
  (HSL, HEX), Dark Modes or nuanced shades.
- **Typography and Layout:** Specify modern typography (Inter, Roboto,
  Outfit) and visual frameworks.
- **Animation:** If applicable, describe hover states or micro-animations.
- **States:** Cover empty, loading, error, hover, focus, and active states.
- **Responsive:** Specify behavior on mobile, tablet, and desktop.

### Ejemplo 1: Landing Page Hero

```
Generate a modern hero section for a SaaS landing page:
- Full viewport height with gradient background (#1a1a2e to #16213e)
- Centered headline "Build Faster with AIRON" in Inter Bold 56px
- Subheadline "AI-powered development orchestration" in Inter Regular 20px, 70% opacity
- Two CTA buttons: primary "Get Started" (filled, #e94560), secondary "Watch Demo" (outlined, white)
- Floating 3D illustration on the right side (placeholder)
- Subtle particles animation in background
- Mobile: stack vertically, buttons full width
```

### Ejemplo 2: Dashboard Card

```
Design a dashboard statistics card:
- White background with 8px border radius, subtle shadow
- Icon on the left (blue circle, white icon)
- Title "Total Projects" in Inter Medium 14px, gray
- Value "24" in Inter Bold 32px, dark
- Green badge "+12% this month" next to value
- Hover state: shadow increases, slight scale up
- Empty state: "No projects yet" with ghost CTA
```

---

## 3. Condiciones de Parada (Stop-Loss)

- If the MCP tool is not listed or connected, stop execution and ask the
  operator to configure it using the templates in §0.1.
- Never assume raw IDs (for projects or screens) without previously listing
  them or asking the operator.
- If the operator already has a design at stitch.withgoogle.com, use
  `mcp_StitchMCP_list_projects` and `mcp_StitchMCP_list_screens` to access
  it — no need to regenerate from scratch.