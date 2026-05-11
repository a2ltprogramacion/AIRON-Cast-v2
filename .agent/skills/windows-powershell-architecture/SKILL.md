---
name: windows-powershell-architecture
description: "Ingeniería de Operaciones para Windows Desktop. Obliga al uso de sintaxis estricta de PowerShell (paréntesis en condicionales, codificación ASCII pura) y prevención catastrófica de parseo JSON."
allowed-tools: Read, Write, Edit, Glob, Grep, Powershell
---

# OS Architecture: Windows PowerShell (A2LT Standard)

This discrete skill enforces hard rules to prevent catastrophic syntax errors when writing PowerShell automation for the user's Desktop environment. PowerShell operates on Objects, not pure raw strings like Bash.

---

## 1. Operator Syntax (The Parentheses Mandate)

PowerShell's evaluation engine is incredibly rigid.

- **CRITICAL RULE:** Each cmdlet call inside an `if` block MUST be wrapped in its own parentheses.
  - ❌ `if (Test-Path "a" -or Test-Path "b")` -> Fatal parse error.
  - ✅ `if ((Test-Path "a") -or (Test-Path "b"))`

## 2. Character Encoding Restrictions

- **No Emojis / Unicode:** Using `✅` or `❌` in PowerShell output scripts breaks the execution stream and throws "Unexpected token" errors. Use ASCII brackets exclusively: `[OK]`, `[ERROR]`, `[WARN]`.

## 3. The JSON Depth Trap

When converting objects to JSON for API payloads or config files:

- ❌ `ConvertTo-Json` (Defaults to shallow depth, silently truncating nested objects payload directly destroying complex data structures).
- ✅ `ConvertTo-Json -Depth 10` (Mandatory flag on every single invocation).

## 4. Null Checking & Variable States

Variables in PowerShell can silently evaluate if not guarded.

- **Always Check Truthiness:** Make sure the object exists before measuring it. `if ($array -and $array.Count -gt 0)`.
- **Cross-Platform Path Safety:** Never hardcode `C:\`. Always use `$env:USERPROFILE` and `Join-Path` to dynamically construct directory addresses.

## 5. Standard Error Handling

Implement global fail-safes in production Windows scripts:

```powershell
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop" # Fail fast mentality

try {
    # Risky Execution
} catch {
    Write-Warning "[ERROR] Failed: $_"
    exit 1
}
```
