@echo off
setlocal enabledelayedexpansion
title QuickReply - Inicializacion

:: ============================================================================
:: QuickReply - Script de inicio
:: Crea el entorno virtual, instala dependencias, corre migraciones y
:: levanta el servidor de desarrollo.
:: ============================================================================

set "PROJECT_ROOT=%~dp0"
cd /d "%PROJECT_ROOT%"

echo.
echo +==============================================================+
echo ^|                    QuickReply                               ^|
echo ^|               Inicializacion del proyecto                  ^|
echo +==============================================================+
echo.

:: 1. Verificar Python
echo [1/5] Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python no encontrado. Instalalo desde https://python.org
    pause
    exit /b 1
)
for /f "tokens=2 delims= " %%v in ('python --version') do echo         Python %%v encontrado.
echo.

:: 2. Entorno virtual
echo [2/5] Configurando entorno virtual...
if not exist "src\.venv\Scripts\python.exe" (
    echo         Creando entorno virtual en src\.venv...
    python -m venv src\.venv
    if errorlevel 1 (
        echo [ERROR] No se pudo crear el entorno virtual.
        pause
        exit /b 1
    )
    echo         Entorno virtual creado.
) else (
    echo         Entorno virtual existente.
)
echo.

:: Definir rutas fijas
set "VENV_PY=src\.venv\Scripts\python.exe"
set "VENV_PIP=src\.venv\Scripts\pip.exe"

:: 3. Instalar dependencias
echo [3/5] Instalando dependencias...
if not exist "src\requirements.txt" (
    echo [ERROR] No se encontro src\requirements.txt
    pause
    exit /b 1
)
%VENV_PIP% install -r src\requirements.txt --quiet
if errorlevel 1 (
    echo [ERROR] Fallo al instalar dependencias.
    pause
    exit /b 1
)
echo         Dependencias instaladas.
echo.

:: 4. Migraciones
echo [4/5] Aplicando migraciones...
%VENV_PY% src\manage.py migrate --run-syncdb
if errorlevel 1 (
    echo [ERROR] Fallo al aplicar migraciones.
    pause
    exit /b 1
)
echo.

:: 5. Seeds
echo [5/5] Seeds...
if not exist "src\db.sqlite3" (
    echo         Base de datos nueva. Cargando mensajes iniciales...
    %VENV_PY% -m seed.load_messages
) else (
    echo         Base de datos existente. Omite seeds.
    echo         Para recargar: %VENV_PY% -m seed.load_messages
)
echo.

echo ===============================================================
echo   QuickReply inicializado correctamente.
echo ===============================================================
echo.
echo   Opciones:
echo     [1] Levantar servidor (localhost:8123)
echo     [2] Abrir admin Django (localhost:8123/admin)
echo     [3] Recargar seeds
echo     [4] Salir
echo.

:menu
set "choice="
set /p "choice=Selecciona una opcion (1/2/3/4): "
if "%choice%"=="" goto menu
if "%choice%"=="1" goto option_server
if "%choice%"=="2" goto option_admin
if "%choice%"=="3" goto option_seeds
if "%choice%"=="4" goto option_exit
echo Opcion invalida. Intenta de nuevo.
goto menu

:option_server
echo.
echo Levantando servidor en http://127.0.0.1:8123 ...
%VENV_PY% src\manage.py runserver 127.0.0.1:8123
goto end_script

:option_admin
echo.
echo Levantando servidor en http://127.0.0.1:8123 ...
start http://127.0.0.1:8123/admin
%VENV_PY% src\manage.py runserver 127.0.0.1:8123
goto end_script

:option_seeds
echo.
%VENV_PY% -m seed.load_messages
pause
goto end_script

:option_exit
echo.
echo Saliendo.
goto end_script

:end_script
endlocal