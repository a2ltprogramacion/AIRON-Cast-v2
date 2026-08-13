---
name: debian-kde-architecture
description: "Ingeniería de Operaciones para Linux Debian y KDE Plasma. Define la ejecución impecable de Bash, gestión de procesos de sistema (Systemd), y atajos específicos para entornos de escritorio KDE."
allowed-tools: Read, Write, Edit, Glob, Grep, Bash
---

# OS Architecture: Debian Linux & KDE Plasma (A2LT Standard)

This discrete skill dictates how background scripts and user-facing terminal commands must be executed on the user's primary Linux laptop (Debian running KDE Plasma).

---

## 1. The Bash Standard Strictness

When generating `.sh` files or executing chains of commands, enforce safe failure logic.

- **Fail Fast:** Every shell script must start with `set -euo pipefail`.
- **Chaining:** Use `&&` for explicit dependency execution (`npm run build && pm2 restart app`). Never use `;` unless ignoring failures is explicitly intended.

## 2. Process & Port Management (Debian/Ubuntu Core)

- **Killing Ports:** Instead of generic guesses, use precise termination: `kill -9 $(lsof -t -i :3000)`.
- **Service Management:** Use `systemctl` for daemon management over raw background passing (`&`). Example: `sudo systemctl restart gunicorn`.
- **Environment Targeting:** Be aware that environment variables in script execution (`$VAR`) differ from system-wide environments. Export explicitly.

## 3. KDE Plasma Context

Since the user operates KDE Plasma:

- **Clipboard:** Use `xclip` or `wl-copy` (if Wayland is enforced) instead of `pbcopy` (macOS).
- **GUI Interactions:** Terminal scripts that require user notifications can leverage `notify-send "Task Complete"`.
- **File Manager:** Operations opening GUI folders should target `dolphin` instead of `explorer.exe` or `open`.

## 4. Text Processing Elite Tools

Before proposing complex Python scripts for simple text parsing, prioritize native Unix binaries:

- `grep -rn "PATTERN"` for global code searching.
- `awk '{print $1}'` for log column extraction.
- `sed -i 's/OLD/NEW/g'` for rapid string replacement in config files.
