# PROMPTY

**PROMPTY** es un asistente por voz desarrollado en Python. Este repositorio contiene varias versiones que muestran la evolución del proyecto, siendo la versión **3.0** la más completa: incluye una interfaz gráfica adaptativa, reconocimiento de voz, gestión de usuarios y reproducción musical mediante YouTube Music.

---

## 🧠 Funcionalidades destacadas (versión 3.0)

- Interacción por texto o voz
- Interfaz gráfica adaptable con modo claro/oscuro
- Reconocimiento de voz con `speech_recognition`
- Síntesis de voz personalizable con `pyttsx3`
- Búsquedas en el navegador o en YouTube
- Reproducción de música desde YouTube Music
- Acceso a datos curiosos integrados
- Gestión de usuarios con permisos (usuario, colaborador, administrador)
- Ventanas independientes para ayuda, configuración de voz e información del usuario
- Nuevo modo "inteligente" conectado a modelos de IA gratuitos (Hugging Face Inference API)
- Servidor HTTP opcional para reutilizar PROMPTY como servicio en otras apps

---

## 🚀 Instalación rápida (versión 3.0)

### Requisitos

- [Git](https://git-scm.com/)
- [Python 3.10+](https://www.python.org/)
- [UV](https://github.com/astral-sh/uv) (gestor de entornos y dependencias)

### Pasos

```bash
# 1. Instalar Git (si aún no lo tienes)
# Comando con winget. Para otros métodos de instalación, consultar el link de arriba.
winget install --id Git.Git -e

# 2. Instalar UV
# Para macOS y Linux.
curl -LsSf https://astral.sh/uv/install.sh | sh

# Para Windows.
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# 3. Clonar el repositorio
git clone https://github.com/ErvingMiranda/PROMPTY.git
cd PROMPTY

# 4. Instalar dependencias
uv sync

# 5. Ejecutar PROMPTY
uv run .\PROMPTY_3.0\main.py
```

> ⚠️ Asegúrate de usar Python 3.10 o superior. Python 3.13 es recomendado para compatibilidad total.

---

## 🧠 Activar el modo inteligente (IA gratuita)

PROMPTY puede conectarse a cualquier modelo disponible en la [Hugging Face Inference API](https://huggingface.co/inference-api) —incluidas alternativas gratuitas como **Mistral 7B Instruct**—, lo que añade razonamiento natural cuando se ingresan comandos no soportados.
Desde la versión 3.0 usamos el endpoint OpenAI-style `https://router.huggingface.co/v1/chat/completions`, compatible con los *Inference Providers* actuales.

1. Crea un archivo `PROMPTY_3.0/config_local.json` (excluido del repositorio) con tu token y modelo:

```json
{
  "api_token": "hf_xxx",
 "model_id": "mistralai/Mistral-7B-Instruct-v0.3",
  "base_url": "https://router.huggingface.co"
}
```

> La integración de IA vive ahora en `PROMPTY_3.0/ai/` (separada de `services/`) para facilitar su mantenimiento.

2. Si prefieres variables de entorno (o como *fallback* si el archivo no existe), puedes definirlas antes de iniciar PROMPTY:

```bash
export HUGGING_FACE_API_TOKEN="hf_xxx"
# Opcional: cambia de modelo si lo deseas
export PROMPTY_IA_MODEL="mistralai/Mistral-7B-Instruct-v0.3"
```

3. Ejecuta PROMPTY normalmente (por GUI o terminal). Cuando escribas o digas algo fuera de los comandos predefinidos, la IA responderá usando el modelo remoto.

Variables extra disponibles:

| Variable | Descripción |
| --- | --- |
| `PROMPTY_IA_BASE_URL` | Endpoint personalizado (por ejemplo, si alojas tu propio modelo o llamas a Gemini vía proxy compatible). |
| `PROMPTY_IA_TIMEOUT` | Tiempo máximo de espera en segundos (por defecto 45). |
| `PROMPTY_IA_MAX_TOKENS` | Límite de tokens generados por respuesta (320 por defecto). |
| `PROMPTY_IA_TEMPERATURE` | Control de creatividad del modelo. |

---

## 🔌 Convertir a servicio/API para MyPlanU

La carpeta `PROMPTY_3.0/api` expone un servidor FastAPI listo para integrarse desde MyPlanU (C# MAUI + SQLite) u otros clientes.

```bash
# Requiere haber ejecutado `uv sync` previamente
uv run uvicorn PROMPTY_3_0.api.server:app --reload --port 8000
```

Endpoints principales:

| Método | Ruta | Descripción |
| --- | --- | --- |
| `GET /health` | Verifica que el servicio esté activo. |
| `POST /api/chat` | Envía un mensaje y recibe la respuesta de la IA. |

Ejemplo de consumo desde cualquier cliente HTTP:

```bash
curl -X POST http://localhost:8000/api/chat \
     -H "Content-Type: application/json" \
     -d '{
            "mensaje": "Genera un resumen del plan semanal",
            "historial": [
                {"rol": "usuario", "contenido": "Necesito organizar tareas"}
            ]
        }'
```

La respuesta JSON contiene `respuesta` (texto generado) y `exito` (bandera booleana). Desde MyPlanU basta con realizar esta petición HTTP para reutilizar las capacidades de PROMPTY como microservicio.

---

## 📁 Estructura del repositorio

```bash
PROMPTY/
├── Prompty1.0/        # Scripts iniciales
├── PROMPTY_2.0/       # Primera versión modularizada
├── PROMPTY_2.5/       # Organización por capas: models, services, views
├── PROMPTY_3.0/       # Versión actual con GUI y todas las funciones
├── tests/             # Pruebas unitarias y funcionales
├── .gitignore         # Ignorar archivos y carpetas en Git
├── LICENSE            # Licencia del proyecto
├── README.md          # Este archivo
├── pyproject.toml     # Configuración de dependencias y formato
└── uv.lock            # Bloqueo de dependencias
```

> Solo la carpeta `PROMPTY_3.0` contiene todas las funciones y es la versión recomendada.

---

## 🎨 Interfaz gráfica

Desde la versión 3.0, PROMPTY incluye una GUI que se adapta a la pantalla.  
Además, si decís comandos como **"estructura"**, **"tree"** o **"árbol"**, se abrirá una ventana que muestra visualmente el árbol del proyecto.

---

## 📜 Licencia

Este proyecto está bajo la licencia **Creative Commons BY-NC 4.0**  
No se permite el uso comercial. Consulta [LICENSE](LICENSE) para más detalles.

---

## 🚧 Estado del proyecto

PROMPTY 3.0 se encuentra en fase de desarrollo activo.  
Futuras versiones incluirán mejoras en la interfaz, integración con APIs externas y nuevas funciones inteligentes.

---
