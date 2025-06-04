from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

def obtener_informacion(opcion):
    if opcion == '1':
        return info_creadores()
    elif opcion == '2':
        return info_sobre_programa()
    elif opcion == '3':
        return info_desarrollo()
    elif opcion == '4':
        return info_licencia()
    else:
        return f"{Fore.RED}❌ Opción no válida.{Style.RESET_ALL}"

def info_creadores():
    return f"""
{Fore.BLUE}SOBRE LOS CREADORES DE PROMPTY{Style.RESET_ALL}
PROMPTY fue desarrollado por un equipo de estudiantes comprometidos con la innovación, como proyecto para la asignatura de 
"Introducción a la Programación" en la Universidad Americana (UAM):

{Fore.CYAN}Miembros del equipo:{Style.RESET_ALL}
- Erving Miranda: Coordinador del proyecto y encargado del diseño general de funciones.
- Owen Bravo: Encargado de pruebas del sistema.
- Liang Zúñiga: Encargado de documentación y apoyo técnico.
- María Carrasco: Responsable de diseño creativo y contenido informativo.
"""

def info_sobre_programa():
    return f"""
{Fore.BLUE}SOBRE EL PROGRAMA{Style.RESET_ALL}
PROMPTY 2.0 es un asistente virtual de escritorio desarrollado como proyecto final del curso "Introducción a la Programación" en la Universidad Americana (UAM).

{Fore.CYAN}Objetivo del programa:{Style.RESET_ALL}
Desarrollar un asistente virtual en Python capaz de ejecutar tareas básicas mediante comandos por texto o voz, integrando una voz sintética natural y una estructura modular profesional. 

El proyecto busca aplicar conocimientos fundamentales del lenguaje Python en un entorno práctico, interactivo y creativo, permitiendo a los usuarios realizar acciones cotidianas como consultar la hora, abrir archivos, buscar en internet o recibir datos curiosos, todo con comandos personalizados y una experiencia cercana a asistentes modernos como ChatGPT o inspirados en personajes como Jarvis.

{Fore.CYAN}Funciones actuales:{Style.RESET_ALL}
- Mostrar fecha y hora actual.
- Abrir archivos o aplicaciones por ruta o explorador.
- Realizar búsquedas en YouTube o Google.
- Compartir datos curiosos desde archivo o con respaldo interno.
- Proporcionar información sobre el proyecto y sus desarrolladores.
- Recibir comandos por voz y responder con voz sintética.
"""

def info_desarrollo():
    return f"""
{Fore.BLUE}PROCESO DE DESARROLLO{Style.RESET_ALL}
PROMPTY está siendo desarrollado en Python 3.13.3 utilizando librerías estándar como `datetime`, `os`, `webbrowser`, `tkinter.filedialog` y `random`, así como módulos como `speech_recognition` y `pyttsx3` para integrar entrada y salida por voz. Además, el código está organizado de forma modular para facilitar su mantenimiento y expansión.

{Fore.CYAN}Versión actual:{Style.RESET_ALL} PROMPTY 2.0

{Fore.CYAN}Funciones implementadas:{Style.RESET_ALL}
- Comandos básicos (fecha/hora, abrir archivos, búsquedas, curiosidades).
- Reconocimiento de voz para interpretar instrucciones.
- Respuesta auditiva mediante voz sintética (`pyttsx3`).
- Organización profesional en módulos independientes.

{Fore.CYAN}Próxima versión: PROMPTY 3.0{Style.RESET_ALL}
- Se planea implementar una interfaz gráfica completa (Tkinter o Qt).
- Se evaluarán mejoras en precisión de comandos de voz.
"""

def info_licencia():
    return f"""
{Fore.BLUE}LICENCIA DE USO Y DERECHOS{Style.RESET_ALL}
© 2025 PROMPTY 2.0 | Universidad Americana (UAM)

Este software fue desarrollado exclusivamente con fines educativos y demostrativos. 
Todos los derechos pertenecen a los autores mencionados y a la Universidad Americana.

{Fore.CYAN}LICENCIA:{Style.RESET_ALL}
- Uso libre para propósitos académicos y personales.
- No se permite su distribución comercial sin autorización del equipo creador.
- Se autoriza la modificación del código siempre que se mantenga el crédito original.

Cualquier uso indebido fuera del marco académico puede violar derechos de autor o políticas institucionales.
"""