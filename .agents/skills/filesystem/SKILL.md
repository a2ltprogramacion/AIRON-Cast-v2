---
name: filesystem
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Integra el servidor MCP Filesystem para acceso controlado al workspace local.
  Permite a los agentes leer, escribir, listar y buscar archivos en el workspace
  de forma segura. Requiere servidor MCP @modelcontextprotocol/server-filesystem.
triggers:
  primary: ["filesystem", "leer archivo", "escribir archivo", "listar directorio", "buscar archivo"]
  secondary: ["read file", "write file", "list directory", "find file", "workspace access"]
  context: ["file operations", "workspace access", "file management"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - orchestrator
  - requirements_architect
  - ux-ui_specialist
  - frontend_worker
  - backend_specialist
  - tester
  - docs
  - meta_factory
last_used: null
scope: restricted
---

# Filesystem MCP Integration — AIRON-Cast

Esta skill proporciona integración con el servidor MCP Filesystem (@modelcontextprotocol/server-filesystem) para operaciones seguras de archivos en el workspace del proyecto.

---

## 0. Verificación de Configuración (Pre-Flight)

### 0.1 Verificación de Disponibilidad MCP

Antes de cualquier operación, verificar que el servidor Filesystem MCP esté disponible:

1. **Verificar disponibilidad:** Intentar listar herramientas MCP disponibles. Verificar que las herramientas `read_file`, `write_file`, `list_directory`, `search_files` estén disponibles.

2. **Si NO disponible:**
   - Detener ejecución inmediatamente.
   - Mostrar mensaje al operador:
     ```
     [FILESYSTEM UNAVAILABLE]: El servidor MCP Filesystem no está instalado o no está configurado.
     Instálalo con: npx -y @modelcontextprotocol/server-filesystem <workspace-path>
     ```

3. **Si disponible:** Proceder al flujo operativo.

---

## 1. Herramientas Disponibles

El servidor Filesystem MCP expone estas herramientas:

| Herramienta | Descripción |
|-------------|-------------|
| `read_file` | Leer contenido de un archivo (path relativo al workspace) |
| `write_file` | Escribir/crear un archivo (path relativo al workspace) |
| `list_directory` | Listar contenido de un directorio |
| `search_files` | Buscar archivos por patrón (glob) |
| `create_directory` | Crear directorio |
| `move_file` | Mover/renombrar archivo |
| `delete_file` | Eliminar archivo |
| `get_file_info` | Obtener metadata (size, modified, etc.) |

---

## 2. Flujo de Trabajo Obligatorio

### Paso 1: Verificar Acceso al Workspace

Antes de cualquier operación, confirmar que la ruta está dentro del workspace permitido:

```python
# Validación implícita - el servidor MCP rechaza rutas fuera de ALLOWED_PATHS
```

### Paso 2: Operaciones de Lectura

```javascript
// Leer archivo
await read_file({ path: "src/components/Button.astro" })

// Listar directorio
await list_directory({ path: "src/components" })

// Buscar archivos
await search_files({ pattern: "*.astro", path: "src" })
```

### Paso 3: Operaciones de Escritura

```javascript
// Escribir archivo (crea directorios intermedios si no existen)
await write_file({ 
  path: "src/components/NewComponent.astro",
  content: "// contenido del archivo"
})

// Crear directorio
await create_directory({ path: "src/components/new" })
```

---

## 3. Reglas de Seguridad

1. **Rutas relativas:** Siempre usar rutas relativas al workspace root (`workspace/<slug>/`)
2. **Validación de ruta:** El servidor MCP rechaza rutas fuera de `ALLOWED_PATHS`
3. **Encoding:** UTF-8 para archivos de texto
4. **Backup implícito:** El orquestador hace checkpoint antes de writes destructivos

---

## 4. Protocolo de Uso por Agente

| Agente | Operaciones Típicas |
|--------|---------------------|
| `frontend_worker` | read/write `.astro`, `.tsx`, `.css`, `.json` |
| `backend_specialist` | read/write `.py`, `.json`, `.sql` |
| `ux-ui_specialist` | read/write `.astro`, `.css`, `.md` |
| `backend_specialist` | read/write `.py`, `.sql`, `.json` |
| `tester` | read/write `test_*.py`, `*.spec.ts` |
| `docs` | read/write `.md`, `.rst` |
| `orchestrator` | checkpoint, checkpoint recovery |

---

## 5. Condiciones de Parada (Stop-Loss)

- Si el servidor MCP no está disponible → HITL
- Si la ruta está fuera de `ALLOWED_PATHS` → HITL
- Si hay error de permisos → HITL
- Si el archivo supera tamaño máximo (configurable) → HITL

---

## 6. Integración con Orquestador

El orquestador inyecta automáticamente el contexto del workspace en el prompt del agente:

```
=== WORKSPACE CONTEXT ===
Proyecto: cafe-cenit-v2-demo
Workspace: workspace/cafe-cenit-v2-demo/
Archivos existentes: 47 archivos en src/
```

---

> **Nota:** El servidor Filesystem MCP se ejecuta localmente via stdio. No requiere API keys externas.