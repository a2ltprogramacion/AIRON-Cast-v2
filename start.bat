@echo off
chcp 65001 > nul
title AIRON-Cast v2.0 — Control de Ecosistema
color 0B

echo ======================================================================
echo           AIRON-Cast v2.0 — Operacion Determinista $0 Budget
echo                 A2LT Soluciones - Mission Control
echo ======================================================================
echo.

:: Cambiar al directorio del script
cd /d "%~dp0"

:: Verificar que Python este disponible
python --version > nul 2>&1
if %errorlevel% neq 0 (
    color 0C
    echo [ERROR] Python no fue encontrado en el PATH del sistema.
    echo Por favor instala Python 3.10+ y asegurate de agregarlo al PATH.
    echo.
    pause
    exit /b 1
)

echo [1/3] Verificando e inicializando base de datos central...
python tools/init_ecosystem.py > nul 2>&1

echo [2/3] Levantando Auto-Supervisor Watchdog y Dashboard Server...
python tools/airon_executor.py health

echo [3/3] Abriendo Dashboard en el navegador (http://localhost:8765)...
start http://localhost:8765

echo.
echo ======================================================================
echo  [OK] El ecosistema AIRON-Cast esta corriendo activamente.
echo.
echo  * Dashboard Web:  http://localhost:8765
echo  * Watchdog:       En segundo plano con auto-curacion activa
echo  * BD Central:     central_intelligence.db (SQLite + FTS5)
echo.
echo  Para detener el servidor: ejecuta "python tools/stop_supervisor.py"
echo ======================================================================
echo.
pause
