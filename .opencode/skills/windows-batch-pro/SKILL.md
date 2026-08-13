---
name: windows-batch-pro
description: |
  Skill especializada en la creación, depuración y automatización de procesos mediante scripts Batch (.bat) de Windows. Actívala cuando el usuario solicite automatizar tareas CMD, crear instaladores batch, o gestionar procesos nativos de Windows. No activar para PowerShell o entornos Linux.
---

# Windows Batch Pro - Automation Master

This skill enables the generation and validation of high-performance Windows Batch scripts. It follows the A2LT standard for robust automation, including strict error handling and system state management.

## 1. Activation Trigger

- Requests for ".bat scripts", "CMD automation", "Windows Batch files".
- Keywords: `xcopy`, `robocopy`, `setlocal`, `cmd.exe`, `batch script`.

## 2. Input Contract

- `task_description`: string (Required) - Detailed description of the automation task.
- `target_directory`: path (Optional) - Contextual path where the script should operate.

## 3. Structural Standards

- **Header**: Every script must include the `setlocal enabledelayedexpansion` mandate.
- **Error Trapping**: Use `IF %ERRORLEVEL% NEQ 0` for every critical command.
- **Validation**: Pass every generated script through `scripts/batch_validator.py`.

## 4. Usage Example

Refer to the [Master Logic](references/batch_best_practices.md) for detailed implementation patterns.

## 5. CMD Reference

See [Windows CMD Reference](references/windows_cmd_reference.md) for a dense command dictionary.
