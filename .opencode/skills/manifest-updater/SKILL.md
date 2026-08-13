---
name: manifest-updater
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Manages AIRON‑Cast's manifest.json — the single source of truth for all
  registered agents and skills. Handles add, update, deprecate, and full
  integrity validation operations. Activate after deploying a new component
  or when the operator needs to register, update, or audit a component.
  Trigger phrases: "actualiza el manifiesto", "registra el componente",
  "depreca la skill", "valida el manifiesto", "update manifest".
  Do NOT activate for reading the manifest — inspect the file directly.
triggers:
  primary: ["actualiza manifiesto", "registra componente", "update manifest"]
  secondary: ["depreca", "valida manifiesto", "manifest integrity"]
  context: ["post-deployment", "cierre de tarea"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - meta_factory
  - orchestrator
last_used: 2026-06-03
scope: restricted
---

# Manifest Updater — Gestión de Manifiesto de AIRON‑Cast

You are acting as a **Registry Keeper** for AIRON‑Cast (A2LT Soluciones).
The manifest is the source of truth for the entire ecosystem. Health checks,
dependency resolution, and deployment all depend on it being accurate.

**One mistake here cascades silently.** Read this document completely before
touching the manifest.

---

## 0. Reglas Absolutas

- **Backup obligatorio antes de cualquier escritura.** The script creates a
  `.bak` copy automatically before writing.
- **Nunca editar el manifiesto a mano.** Only use `manifest_updater.py`.
- **`status: active` es el único estado que el ecosistema consume.**
  `deprecated` and `draft` components are ignored by health checks.
- **El `path` debe ser relativo a la raíz del proyecto**, not absolute.
- **`dependencies` es obligatorio**, even when empty.

---

## 1. Estructura del Manifiesto

AIRON‑Cast uses a single `manifest.json` at the project root:

```json
{
  "ecosystem": "AIRON-Cast",
  "version": "1.0.0",
  "last_updated": "YYYY-MM-DDTHH:MM:SSZ",
  "agents": [],
  "skills": []
}
```

### Entrada de agente

```json
{
  "name": "agent-name",
  "version": "1.0.0",
  "kind": "agent",
  "status": "active",
  "path": "./.agents/profiles/agent-name.md",
  "role": "orchestrator",
  "circle": 2,
  "scope": "elevated",
  "dependencies": {"internal": [], "external": []},
  "description": "What this agent does."
}
```

### Entrada de skill

```json
{
  "name": "skill-name",
  "version": "1.0.0",
  "kind": "skill",
  "status": "active",
  "path": "./.agents/skills/skill-name/",
  "type": "utility",
  "scope": "restricted",
  "dependencies": {"internal": [], "external": []},
  "description": "What this skill does."
}
```

---

## 2. Operaciones

### 2.1 `add` — Registrar componente nuevo

```
1. Verify component path exists on disk
2. Read frontmatter to extract metadata
3. Check name does not already exist in manifest
   → If exists: use update instead
4. Run: manifest_updater.py --operation add --kind agent|skill --component '<json>'
```

### 2.2 `update` — Actualizar versión o estado

```
1. Verify component exists in manifest by name
2. Identify changed fields
3. Run: manifest_updater.py --operation update --kind agent|skill --component '<json>'
```

### 2.3 `deprecate` — Marcar como obsoleto

```
1. Verify component exists with status: active
2. Check for active dependents
   → If dependents exist: STOP — emit [ALTO]
3. Run: manifest_updater.py --operation deprecate --kind agent|skill --name <name>
```

### 2.4 `validate` — Auditoría de integridad

Checks all entries for:

| Check | Severity |
|-------|----------|
| Schema compliance — all required fields present | Fatal |
| Name uniqueness — no duplicates | Fatal |
| Path existence — directory or file exists on disk | Fatal |
| SKILL.md or profile .md present at path | Fatal |
| Version follows SemVer X.Y.Z | Warning |
| Dependencies resolve to existing components | Warning |
| Circular dependencies | Fatal |
| Orphan directories not in manifest | Warning |

```bash
python scripts/manifest_updater.py --operation validate
```

If any fatal errors: emit `[ALTO]`. Do not proceed with deployment.

---

## 3. Inicialización (Primera vez)

If `manifest.json` does not exist at the project root:

```bash
python scripts/manifest_updater.py --operation init
```

This creates the manifest with the correct schema and empty `agents` + `skills` arrays.

---

## 4. Script de Soporte

### `manifest_updater.py`

Located in `scripts/` within this skill directory.

```bash
# Init
python scripts/manifest_updater.py --operation init

# Add
python scripts/manifest_updater.py --operation add \
  --kind agent|skill --component '<json>'

# Update
python scripts/manifest_updater.py --operation update \
  --kind agent|skill --component '<json>'

# Deprecate
python scripts/manifest_updater.py --operation deprecate \
  --kind agent|skill --name <name>

# Validate
python scripts/manifest_updater.py --operation validate

# Dry run (preview without writing)
python scripts/manifest_updater.py --operation add --kind skill \
  --component '<json>' --dry-run

# Exit codes:
# 0 — Success
# 1 — Component not found
# 2 — Duplicate name
# 3 — Schema validation failed
# 4 — Path does not exist on disk
# 5 — Active dependents block deprecation
# 6 — Circular dependency detected
```

---

## 🔗 AIRON‑Cast Integration

Consumed by:
- `meta_factory` — to register newly created agents and skills.
- `orchestrator` — to validate manifest integrity before starting a task loop.

Generated validation reports can be stored in `workspace/<slug>/reports/`
for project-level audits.