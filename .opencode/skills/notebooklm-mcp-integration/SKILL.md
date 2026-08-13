---
name: notebooklm-mcp-integration
version: 1.0.0
type: utility
subtype: skill
tier: all
description: |
  Integración avanzada de Google NotebookLM vía MCP y CLI para AIRON‑Cast.
  Permite consultar cuadernos, generar audio, añadir fuentes y razonar
  entre múltiples cuadernos. Incluye protocolo de instalación asistida.
  Activar cuando el Operador o un agente necesiten interactuar con
  NotebookLM o instalar/configurar el servidor MCP.
  Trigger phrases: "notebooklm", "consulta mis cuadernos", "genera audio
  de notebook", "añade fuente a notebook", "instalar notebooklm mcp", "notebooklm",
  "consulta cuadernos", "notebook mcp", "genera audio notebook", "añade fuente",
  "instalar notebooklm".
triggers:
  primary: ["notebooklm", "consulta cuadernos", "notebook mcp"]
  secondary: ["genera audio notebook", "añade fuente", "instalar notebooklm"]
  context: ["MCP integration", "knowledge base external", "Google NotebookLM"]
dependencies: []
framework_version: ">=1.0.0"
assigned_agents:
  - orchestrator
  - requirements_architect
  - backend_specialist
  - meta_factory
  - writer
last_used: 2026-06-05
scope: elevated
---

# NotebookLM MCP Integration — AIRON‑Cast

Autonomous interaction with Google NotebookLM using the
`notebooklm-mcp-cli` package. Prioritize MCP tools for all hot operations
within the IDE. The CLI (`nlm`) is reserved for initial setup,
troubleshooting, or heavy batch automation.

---

## 0. Critical Behavior Rules

1. **MCP Priority:** Before invoking a CLI command, check if the equivalent
   MCP tool is available.
2. **Active Profile:** Never assume a static profile name. The system reads
   the user's active Chrome browser session via local credential persistence.
3. **Context Persistence:** When using text mode queries (`nlm_chat`), maintain
   thematic coherence and read notebook notes before responding if the prompt
   requires specific data.
4. **Full Feature Set:** Use all available functions: audio/podcasts, videos,
   structured documents, and advanced Studio flows.

---

## 1. Installation Protocol (Assisted)

Use this flow when an operator requests help installing, repairing, or
configuring the NotebookLM MCP ecosystem on their local machine.

### Step 1 — Pre-flight Check

Ask the user to run this diagnostic in their terminal:

```bash
python3 --version && echo "uv: $(which uv || echo 'not-found')"
```

**Decision tree:**
- **Python < 3.11:** Stop. The package requires `Python >= 3.11`.
- **`uv` found:** Proceed with **Route A (Recommended)**.
- **No `uv` but valid Python:** Proceed with **Route B (pip/pipx)**.

### Step 2 — Isolated Installation

**Route A: With `uv` (Priority)**

```bash
uv tool install --force notebooklm-mcp-cli
```

The `--force` flag overwrites any corrupted symlinks from previous collisions.

**Route B: With `pipx` or `pip`**

```bash
pipx install notebooklm-mcp-cli
# or, if using manual venv:
pip install notebooklm-mcp-cli
```

### Step 3 — Verify Binaries

```bash
which nlm && which notebooklm-mcp
```

Both commands must return their local installation paths.

### Step 4 — Sync Active Chrome Profile

```bash
nlm setup --browser chrome
```

Then generate the JSON configuration block for the IDE:

```bash
nlm setup add json
```

The output must be added to the IDE's MCP configuration file:

```json
{
  "mcpServers": {
    "notebooklm-mcp": {
      "command": "notebooklm-mcp",
      "args": []
    }
  }
}
```

### Step 5 — Health Check

```bash
nlm doctor
```

If the command returns a healthy status, the installation is complete and
fully functional. The agent can now consume MCP tools immediately.

---

## 2. MCP Tools Reference (High Priority)

Use these functions directly from the MCP ecosystem:

| Tool | Input / Arguments | Description |
|------|-------------------|-------------|
| `nlm_list_notebooks` | None | Returns the complete list of available notebooks with unique IDs. |
| `nlm_create_notebook` | `title` (str) | Creates a new blank notebook in the active account. |
| `nlm_delete_notebook` | `notebook_id` (str) | Permanently deletes a specific notebook. |
| `nlm_list_sources` | `notebook_id` (str) | Lists all documents, links, or videos indexed in the notebook. |
| `nlm_add_source` | `notebook_id` (str), `source_type` (str), `payload` (str) | Adds text, PDFs, YouTube URLs, or web links to the notebook. |
| `nlm_remove_source` | `notebook_id` (str), `source_id` (str) | Removes a specific source from the notebook. |
| `nlm_create_note` | `notebook_id` (str), `title` (str), `content` (str) | Creates a text note autonomously within the notebook. |
| `nlm_get_note` | `notebook_id` (str), `note_id` (str) | Reads the full text content of a specific note. |
| `nlm_chat` | `notebook_id` (str), `query` (str) | Executes a direct query on the notebook's context (Main Text Mode). |
| `nlm_cross_notebook_chat` | `notebook_ids` (list), `query` (str) | Performs complex queries crossing multiple notebooks in parallel. |
| `nlm_studio_prompt` | `notebook_id` (str), `prompt` (str), `output_type` (str) | Generates study guides, data tables, advanced summaries, or Studio briefings. |
| `nlm_generate_audio` | `notebook_id` (str), `config` (dict) | Initiates the audio generation pipeline (NotebookLM Podcast). |

---

## 3. CLI Usage (Specific Cases)

Invoke the CLI via terminal commands only for batch flows or structured
maintenance:

### Source and Notebook Management

```bash
nlm notebook create --title "Critical Infrastructure 2026"
nlm source add --notebook-id "NOTEBOOK_ID" --file "./docs/network_perimeters.pdf"
```

### Interactive REPL Mode

```bash
nlm chat repl --notebook-id "NOTEBOOK_ID"
```

### Advanced Studio Exploitation

```bash
nlm studio prompt --notebook-id "NOTEBOOK_ID" \
  --instruction "Generate a comparative table of analyzed failure modes" \
  --format data_table
```

---

## 4. Recommended Agent Workflows

### Flow A: Deep Context Query

1. Call `nlm_list_notebooks` to locate the ID associated with the active
   project.
2. If it does not exist, create it with `nlm_create_notebook` and add local
   technical documentation using `nlm_add_source`.
3. Execute `nlm_chat` to extract hidden variables or critical dependencies
   from the provided specifications.

### Flow B: Automatic Cookie Sync

If an MCP call returns a session error (`401` or `CookieExpired`), launch
the embedded repair script (see §5).

---

## 5. Session Repair Automation Script

This script validates and refreshes the communication bridge with active
Google Chrome cookies without requiring manual operator intervention:

```python
import sys
import subprocess
import json
from notebooklm_tools.core.auth import get_active_profile_cookies

def check_and_repair_session():
    print("[Skill] Initiating active Chrome session validation...")
    try:
        result = subprocess.run(
            ["nlm", "doctor"],
            capture_output=True, text=True, check=False
        )
        if result.returncode == 0:
            print("[Skill] NotebookLM connection healthy. MCP Operational.")
            return True
        else:
            print("[Skill] Alert: Session expired or invalid. "
                  "Forcing re-sync with active browser...")
            subprocess.run(
                ["nlm", "setup", "--browser", "chrome"],
                capture_output=True, text=True, check=True
            )
            print("[Skill] Re-sync completed successfully.")
            return True
    except Exception as e:
        print(f"[Skill] Critical error during session auto-repair: {e}",
              file=sys.stderr)
        return False

if __name__ == "__main__":
    success = check_and_repair_session()
    sys.exit(0 if success else 1)
```

---

## 6. Permissions in `manifest.json`

Each agent that needs to consult NotebookLM must include `"notebooklm"` in
its `can_call_mcps` array:

```json
"requirements_architect": {
  "can_call_mcps": ["context7", "notebooklm"]
}
```

The Orchestrator coordinates handoffs involving this query but does not
consult NotebookLM directly.