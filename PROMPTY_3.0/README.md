# PROMPTY 3.0

Este proyecto incluye dos scripts pensados para facilitar la integración con MyPlanU en Windows. Ambos viven en la carpeta `scripts/` y funcionan con doble clic.

## Requisitos previos
- Contar con Python instalado en Windows.
- (Opcional) Crear un entorno virtual en `PROMPTY_3.0\venv` e instalar las dependencias. Los scripts lo activarán automáticamente si existe.

## Levantar la API (PROMPTY Lite)
1. Navega a `PROMPTY_3.0\scripts` y haz doble clic en `start_prompty_api.bat`.
2. El script cambia a la raíz del proyecto, activa `venv` si está disponible y lanza el servidor FastAPI con uvicorn (`api.server:app`) en el puerto 8000.
3. Accede a la API en `http://localhost:8000`. El endpoint `/health` devuelve `{ "status": "ok" }`.

## Arrancar la interfaz gráfica (PROMPTY completo)
1. Desde `PROMPTY_3.0\scripts`, ejecuta `start_prompty_gui.bat` (doble clic).
2. El script activa `venv` (si existe) y ejecuta `main.py`, enviando automáticamente `s` para arrancar la interfaz gráfica sin interacción manual.
3. La aplicación se mantiene abierta mientras uses la interfaz gráfica de PROMPTY 3.0.

## Notas
- Si necesitas cambiar el puerto de la API, modifica la línea de uvicorn en `scripts/start_prompty_api.bat`.
- Los scripts asumen que se ejecutan desde Windows; en otros sistemas operativos puedes lanzar los mismos comandos manualmente desde la terminal.
