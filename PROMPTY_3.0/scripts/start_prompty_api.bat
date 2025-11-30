@echo off
setlocal
rem Cambia a la carpeta raíz del proyecto (PROMPTY_3.0)
cd /d "%~dp0.."

rem Activa el entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

rem Inicia el servidor HTTP de PROMPTY Lite
python -m uvicorn api.server:app --host 0.0.0.0 --port 8000
