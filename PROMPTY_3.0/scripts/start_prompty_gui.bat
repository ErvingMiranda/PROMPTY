@echo off
setlocal
rem Cambia a la carpeta raíz del proyecto (PROMPTY_3.0)
cd /d "%~dp0.."

rem Activa el entorno virtual si existe
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
)

rem Lanza PROMPTY en modo interfaz gráfica sin pedir confirmación
(echo s) | python main.py
