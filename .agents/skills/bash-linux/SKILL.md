---
name: bash-linux
description: "Patrones y comandos esenciales de Bash/Linux. Uso crítico del terminal, tuberías (pipes), gestión de procesos, manipulación de archivos y scripts de automatización para entornos de despliegue y WSL."
allowed-tools: Read, Write, Edit, Glob, Grep, Run
---

# Bash & Linux Master Patterns

You are operating under the **bash-linux** skill. This skill dictates best practices for utilizing the terminal within the A2LT workflow (which primarily operates in WSL on Windows or native Linux servers).

## 1. Safety and Execution

- **Non-Interactive Commands:** When automating tasks via `run_command` or shell scripts, ALWAYS ensure flags like `-y`, `--force`, or `--non-interactive` are passed to prevent the terminal from hanging indefinitely waiting for user input.
- **Fail Fast:** Any bash script written must begin with `set -euo pipefail` to ensure the script aborts immediately if any command fails or an undefined variable is referenced.

## 2. Essential Chaining

| Operator | Usage                       | A2LT Example                                                  |
| -------- | --------------------------- | ------------------------------------------------------------- |
| `&&`     | Run if previous succeeded   | `python manage.py makemigrations && python manage.py migrate` |
| `\|\|`   | Run if previous failed      | `npm run build \|\| echo "Astro build failed!" > error.log`   |
| `\|`     | Pass output to next command | `cat .env \| grep "SECRET_KEY"`                               |

## 3. Text and File Processing

- `grep -r "pattern" .`: Recursively search for a string.
- `find . -name "*.py"`: Find Python files.
- `tail -f logs/debug.log`: Continuously read a log file as it updates.

## 4. Process Management

When dealing with ghost processes blocking a port (common with Django runserver or Astro dev mode):

1. Find the PID: `lsof -i :8000` or `netstat -ano | findstr :8000` (if in native Windows).
2. Kill it safely: `kill -9 <PID>` (Linux/WSL) or `taskkill /PID <PID> /F` (Windows).

## 5. Automation Template

When asked to generate a deployment or setup script (`setup.sh`), use this immutable template:

```bash
#!/bin/bash
set -euo pipefail

# ANSI Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1" >&2; }

main() {
    log_info "Initiating A2LT operation..."
    # Logic goes here
    log_info "Operation complete."
}

# Execute main function with all script arguments
main "$@"
```
