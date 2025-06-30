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
- Ventanas independientes para ayuda, configuración de voz e información del sistema

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

# 4. Cambiar a la rama principal del proyecto
git checkout 3.0

# 5. Instalar dependencias
uv sync

# 6. Ejecutar PROMPTY
uv run .\PROMPTY_3.0\main.py
```

> ⚠️ Asegúrate de usar Python 3.10 o superior. Python 3.13 es recomendado para compatibilidad total.

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