---
name: github
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Integración con GitHub MCP para gestión de issues, PRs, workflows y repositorios.
  Permite a los agentes crear issues, PRs, gestionar workflows y vincular tareas a GitHub.
  Requiere servidor MCP @modelcontextprotocol/server-github con GITHUB_TOKEN.
triggers:
  primary: ["github", "issue", "pull request", "pr", "workflow", "repo"]
  secondary: ["github issue", "crear pr", "workflow run", "github actions"]
  context: ["github integration", "issue tracking", "ci/cd", "code review"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - orchestrator
  - backend_specialist
  - frontend_worker
  - qa_auditor
  - tester
  - docs
last_used: null
scope: restricted
---

# GitHub MCP Integration — AIRON-Cast

Esta skill proporciona integración con GitHub a través del servidor MCP @modelcontextprotocol/server-github.

---

## 0. Verificación de Configuración (Pre-Flight)

### 0.1 Verificación de Disponibilidad MCP

Antes de cualquier operación, verificar que el servidor GitHub MCP esté disponible:

1. **Verificar disponibilidad:** Intentar listar herramientas MCP disponibles. Verificar que las herramientas de GitHub estén disponibles.

2. **Variables de entorno requeridas:**
   - `GITHUB_TOKEN`: Personal Access Token de GitHub con scopes apropiados

3. **Si NO disponible:**
   - Detener ejecución inmediatamente.
   - Mostrar mensaje al operador:
     ```
     [GITHUB UNAVAILABLE]: El servidor MCP GitHub no está configurado.
     Requiere GITHUB_TOKEN en variables de entorno.
     ```

---

## 1. Herramientas Disponibles (MCP GitHub)

El servidor GitHub MCP expone estas herramientas principales:

| Herramienta | Descripción |
|-------------|-------------|
| `create_issue` | Crear issue en repositorio |
| `get_issue` | Obtener detalles de issue |
| `list_issues` | Listar issues con filtros |
| `update_issue` | Actualizar issue (estado, labels, assignees) |
| `add_issue_comment` | Añadir comentario a issue |
| `create_pull_request` | Crear Pull Request |
| `get_pull_request` | Obtener detalles de PR |
| `list_pull_requests` | Listar PRs |
| `merge_pull_request` | Merge de PR |
| `create_branch` | Crear rama |
| `get_file_contents` | Leer archivo del repo |
| `create_or_update_file` | Crear/actualizar archivo |
| `search_code` | Buscar código en repo |
| `create_workflow_dispatch` | Disparar workflow |
| `list_workflow_runs` | Listar ejecuciones de workflow |
| `get_workflow_run` | Detalles de ejecución |

---

## 2. Flujo de Trabajo Obligatorio

### Paso 1: Verificar Token

```python
# El servidor MCP valida GITHUB_TOKEN automáticamente
# Si falla → HITL con mensaje: "GITHUB_TOKEN inválido o expirado"
```

### Paso 2: Operaciones Comunes

```javascript
// Crear issue desde tarea
await create_issue({
  owner: "org/repo",
  title: "Tarea 46: Crear componente ProductCard.astro",
  body: "Implementar componente reutilizable...",
  labels: ["frontend", "task-46"],
  assignees: ["frontend_worker"]
})

// Crear PR desde tarea completada
await create_pull_request({
  owner: "org/repo",
  title: "feat: ProductCard component",
  head: "feature/product-card-46",
  base: "main",
  body: "Implementa tarea 46..."
})

// Disparar workflow CI/CD
await create_workflow_dispatch({
  owner: "org/repo",
  workflow_id: "ci.yml",
  ref: "main",
  inputs: { environment: "staging" }
})
```

---

## 3. Reglas de Seguridad

1. **Token scope mínimo:** `repo`, `workflow`, `issues`, `pull_request`
2. **No hardcodear tokens:** Usar `${GITHUB_TOKEN}` desde env
3. **Rate limiting:** Respetar límites de API (5000 req/hora)
4. **Owner/repo explícitos:** Siempre especificar owner/repo

---

## 4. Protocolos por Agente

| Agente | Operaciones Típicas |
|--------|---------------------|
| `orchestrator` | Dispatch workflows, link tasks to issues |
| `backend_specialist` | Create PRs, update issues |
| `frontend_worker` | Create PRs, update issues |
| `qa_auditor` | Review PRs, approve/merge |
| `tester` | Trigger workflows, report results |
| `docs` | Update docs via PR |

---

## 5. Integración con Orquestador

El orquestador puede:
1. Crear issue automáticamente al recibir tarea nueva
2. Vincular task_id a issue_number
3. Al completar tarea → crear PR vinculado
4. QA audita → approve → merge
5. Orchestrator finaliza tarea

---

## 5. Condiciones de Parada (Stop-Loss)

- Token inválido/expirado → HITL
- Rate limit exceeded → wait + retry
- Permisos insuficientes → HITL
- Repo no accesible → HITL

---

## 6. Integración con Tareas Locales

```json
{
  "task_id": 46,
  "github_issue": 123,
  "github_pr": 456,
  "branch": "feature/product-card-46",
  "status": "PR abierto - pendiente QA"
}
```

El orquestador mantiene sincronización task_id ↔ issue/PR en `MISSION_CONTROL.md`.

---

## 7. Configuración Requerida

### Variables de entorno:
```bash
export GITHUB_TOKEN="ghp_xxxxxxxxxxxx"  # PAT con scopes: repo, workflow, issues, pr
```

### .mcp.json (ya configurado):
```json
{
  "mcp": {
    "github": {
      "type": "local",
      "command": ["npx", "-y", "@modelcontextprotocol/server-github"],
      "enabled": true,
      "environment": {
        "GITHUB_TOKEN": "${GITHUB_TOKEN}"
      }
    }
  }
}
```

---

> **Nota:** El servidor GitHub MCP (@modelcontextprotocol/server-github) está deprecado en npm pero sigue funcionando. Alternativa futura: usar gh-mcp o implementación custom.