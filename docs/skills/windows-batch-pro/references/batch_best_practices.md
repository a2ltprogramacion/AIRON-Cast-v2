# Batch Scripting Best Practices (A2LT Standards)

To ensure the highest level of reliability in Windows Batch automation, follow these strict guidelines.

## 1. Environment Isolation

Always start your scripts with:

```batch
@echo off
setlocal enabledelayedexpansion
```

This prevents environment variable leakage and ensures dynamic variable evaluation inside loops.

## 2. Error Handling (The %ERRORLEVEL% Rule)

Check the success or failure of every destructive or external command.

```batch
XCOPY source destination /Y
IF %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Copy failed with code %ERRORLEVEL%
    exit /b %ERRORLEVEL%
)
```

## 3. Quoting Paths

In Windows, paths with spaces are common. ALWAYS quote variable expansions.

- **Correct**: `IF EXIST "%MY_PATH%" ...`
- **Incorrect**: `IF EXIST %MY_PATH% ...`

## 4. Subroutines and GOTO

Use subroutines for repeatable logic and always end with `exit /b` to return to the caller.

```batch
call :MySubroutine
exit /b 0

:MySubroutine
echo Performing task...
exit /b 0
```
