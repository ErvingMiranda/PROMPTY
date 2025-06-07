#Parte 1: Preparar los comandos básicos
#Implementar al menos 5 comandos funcionales que el asistente pueda ejecutar correctamente 
#1. Mostrar fecha y hora
#2. Abrir carpetas o aplicaciones
#3. Realizar búsquedas en YouTube o el navegador
#4. Proporcionar datos curiosos
#5. Ofrecer información sobre el programa y sus creadores.

from datetime import datetime
import os
from tkinter import Tk, filedialog
import webbrowser
import shutil
import random
import subprocess
import platform
from colorama import init, Fore, Style
from IngresarDatosCuriosos import administrar_datos_curiosos

# Inicializa colorama
init(autoreset=True)

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def abrir_elemento(ruta):
    try:
        if platform.system() == "Windows":
            os.startfile(ruta)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta])
        print(Fore.GREEN + f"✔ Abriendo: {ruta}")
    except Exception as e:
        print(Fore.RED + f"❌ Error al abrir {ruta}: {e}")

def mostrar_fecha_hora():
    ahora = datetime.now()
    print(Fore.CYAN + f"🕒 Fecha y hora actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")

def abrir_con_ruta():
    ruta = input(Fore.YELLOW + "\nIntroduce la ruta completa del archivo o aplicación (por ejemplo, C:/...): ")
    abrir_elemento(ruta)

def abrir_con_explorador():
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    while True:
        tipo = input(Fore.YELLOW + "\n¿Qué deseas abrir? (1. Carpeta, 2. Aplicación): ")
        if tipo == '1':
            ruta = filedialog.askdirectory(title="Selecciona una carpeta", parent=root)
            break
        elif tipo == '2':
            ruta = filedialog.askopenfilename(title="Selecciona un archivo o aplicación", parent=root)
            break
        else:
            print(Fore.RED + "❌ Opción no válida. Intenta de nuevo.")

    root.destroy()

    if ruta:
        abrir_elemento(ruta)
    else:
        print(Fore.RED + "❌ No se seleccionó ningún archivo.")

def buscar_en_navegador():
    print(Fore.YELLOW + "\n¿Dónde quieres hacer la búsqueda?")
    print("1. YouTube")
    print("2. Navegador (Google)")
    
    destino = input("Selecciona una opción (1 o 2): ").strip()
    if destino not in ('1', '2'):
        print(Fore.RED + "❌ Opción inválida. Intenta nuevamente.")
        print(Fore.YELLOW + "\n¿Dónde quieres hacer la búsqueda?")
        print("1. YouTube")
        print("2. Navegador (Google)")
        
        destino = input("Selecciona una opción (1 o 2): ").strip()

    print(Fore.YELLOW + "\n¿Tienes un término para buscar o un enlace (URL)?")
    print("1. Término de búsqueda")
    print("2. URL directa")
    
    tipo = input("Selecciona una opción (1 o 2): ").strip()
    while tipo not in ('1', '2'):
        print(Fore.RED + "❌ Opción inválida. Intenta nuevamente.")
        print(Fore.YELLOW + "\n¿Tienes un término para buscar o un enlace (URL)?")
        print("1. Término de búsqueda")
        print("2. URL directa")
        tipo = input("Selecciona una opción (1 o 2): ").strip()

    url = ""

    if destino == '1':  # YouTube
        if tipo == '1':
            termino = input("\n¿Qué deseas buscar en YouTube?: ").strip()
            while not termino:
                print(Fore.RED + "❌ El término de búsqueda no puede estar vacío.")
                termino = input("¿Qué deseas buscar en YouTube?: ").strip()
            url = f"https://www.youtube.com/results?search_query={termino.replace(' ', '+')}"
        else:
            url = input("\nIntroduce el enlace de YouTube: ").strip()
    else:  # Google
        if tipo == '1':
            termino = input("\n¿Qué deseas buscar en Google?: ").strip()
            while not termino:
                print(Fore.RED + "❌ El término de búsqueda no puede estar vacío.")
                termino = input("¿Qué deseas buscar en Google?: ").strip()
            url = f"https://www.google.com/search?q={termino.replace(' ', '+')}"
        else:
            url = input("\nIntroduce el enlace de la página web: ").strip()

    # Validar URL si es directa
    if tipo == '2':
        if not url.startswith(("http://", "https://")):
            print(Fore.RED + "❌ La URL debe comenzar con 'http://' o 'https://'.")
            return

    # Intentar abrir el navegador
    chrome_path = shutil.which("chrome") or shutil.which("google-chrome")
    try:
        if chrome_path:
            webbrowser.get(f'"{chrome_path}" %s').open(url)
        else:
            webbrowser.open(url)
        print(Fore.BLUE + f"✔ Abriendo: {url}")
    except Exception as e:
        print(Fore.RED + f"❌ Error al abrir el navegador: {e}")

def datos_curiosos():
    try:
        with open("datos_curiosos.txt", "r", encoding="utf-8") as archivo:
            datos = archivo.readlines()
        if datos:
            print(Fore.MAGENTA + f"✨ Dato curioso: {random.choice(datos).strip()}")
        else:
            print(Fore.YELLOW + "⚠ No hay datos curiosos disponibles.")
    except FileNotFoundError:
        datos_fallback = [
            "¿Sabías que el corazón humano late más de 100,000 veces al día?",
            "Los pulpos tienen tres corazones.",
            "La miel nunca se echa a perder.",
            "La Torre Eiffel puede ser 15 cm más alta durante el verano.",
            "Los tiburones existían antes que los árboles."
        ]
        print(Fore.MAGENTA + f"✨ Dato curioso: {random.choice(datos_fallback)}")

def informacion_programa():
    print(Fore.YELLOW + "\nSobre qué quieres saber más:")
    print("1. Sobre los creadores")
    print("2. Sobre el programa")
    print("3. Sobre el desarrollo")
    print("4. Licencia de uso")
    opcion = input("Selecciona una opción (1-4): ")

    if opcion == '1':
        print(Fore.CYAN + """
PROMPTY fue desarrollado por un equipo de estudiantes comprometidos con la innovación, como proyecto para la asignatura de \n"Introducción a la Programación" en la Universidad Americana (UAM):
        
Miembros del equipo:
    - Erving Miranda: Coordinador del proyecto y encargado del diseño general de funciones
    - Owen Bravo: Encargado de pruebas del sistema.
    - Liang Zúñiga: Encargado de documentación y apoyo técnico.
    - María Carrasco: Responsable de diseño creativo y contenido informativo.""")
    
    elif opcion == '2':
        print(Fore.CYAN + "🤖 SOBRE EL PROGRAMA" + Style.RESET_ALL + """
PROMPTY 1.2 es un asistente virtual de escritorio desarrollado como proyecto final del curso "Introducción a la Programación" en la Universidad Americana (UAM).
        """)

        print(Fore.CYAN + "🎯 Objetivo del programa:" + Style.RESET_ALL + """
Desarrollar un asistente virtual de escritorio en Python que permita ejecutar tareas básicas mediante comandos escritos y por voz, integrando una interfaz gráfica amigable y una voz sintética configurable que brinde respuestas auditivas.

El proyecto busca aplicar conocimientos fundamentales del lenguaje Python en un entorno práctico, interactivo y creativo, 
permitiendo a los usuarios realizar acciones cotidianas como consultar la hora, abrir archivos, buscar en internet o recibir datos curiosos, \ntodo desde una interfaz amigable.

Inspirado por asistentes como Jarvis (Iron Man) o herramientas como ChatGPT, PROMPTY combina lógica de programación con una experiencia de usuario accesible y en constante evolución.
        """)

        print(Fore.BLUE + "🛠️ Funciones principales:" + Style.RESET_ALL + """
        - Mostrar fecha y hora actual.
        - Abrir archivos y aplicaciones mediante rutas o explorador de archivos.
        - Realizar búsquedas en YouTube o Google.
        - Proporcionar datos curiosos de forma aleatoria.
        - Información sobre el programa y sus creadores.
        """)

        print(Fore.YELLOW + "🔒 Modo administrador:" + Style.RESET_ALL + """
        - Permite agregar o sobrescribir datos curiosos en el archivo de texto.
        - Requiere contraseña para acceso.
        """)


    
    elif opcion == '3':
        print(Fore.CYAN + """
🛠️ PROCESO DE DESARROLLO

PROMPTY fue desarrollado en el lenguaje **Python 3.13.3**, utilizando librerías estándar como `datetime`, `os`, `webbrowser`, `tkinter.filedialog` y `random`, así como módulos personalizados.

🔸 Versión actual: **PROMPTY 1.2**
🔸 Funciones actuales:
- Mostrar fecha y hora
- Abrir carpetas o aplicaciones
- Buscar en YouTube o Google
- Compartir datos curiosos y añadirlos (modo administrador)
- Información general del asistente y sus creadores

🧭 Próximas versiones incluirán:
- Reconocimiento de voz
- Interfaz gráfica completa con `tkinter`
- Respuestas auditivas mediante `pyttsx3`

Este proyecto se ha ido construyendo de a poco, aplicando conceptos como modularidad, condicionales, validación de entradas y manejo de archivos.""")
    
    elif opcion == '4':
        print(Fore.CYAN + """
📜 LICENCIA DE USO Y DERECHOS

© 2025 PROMPTY 1.2 | Universidad Americana (UAM)

Este software fue desarrollado exclusivamente con fines **educativos y demostrativos**. 
Todos los derechos pertenecen a los autores mencionados y a la Universidad Americana.

🔒 LICENCIA:
- Uso libre para propósitos académicos y personales.
- No se permite su distribución comercial sin autorización del equipo creador.
- Se autoriza la modificación del código siempre que se mantenga el crédito original.

Cualquier uso indebido fuera del marco académico puede violar derechos de autor o políticas institucionales.""")
    
    else:
        print(Fore.RED + "❌ Opción no válida.")

def mostrar_menu():
    print(Fore.YELLOW + "\nComandos disponibles:")
    print(Fore.GREEN + "1." + Style.RESET_ALL + " Mostrar fecha y hora")
    print(Fore.GREEN + "2." + Style.RESET_ALL + " Abrir carpeta o aplicación")
    print(Fore.GREEN + "3." + Style.RESET_ALL + " Buscar en YouTube o Google")
    print(Fore.GREEN + "4." + Style.RESET_ALL + " Datos curiosos")
    print(Fore.GREEN + "5." + Style.RESET_ALL + " Sobre nosotros")
    print(Fore.GREEN + "6." + Style.RESET_ALL + " Añadir dato curioso (admin)")
    print(Fore.GREEN + "7." + Style.RESET_ALL + " Salir (o 'salir' para cerrar el programa)")

# === Programa principal ===
while True:
    limpiar_pantalla()
    print(Fore.CYAN + Style.BRIGHT + "\nBienvenido a PROMPTY 1.2")
    print(Style.RESET_ALL + "Soy un asistente virtual y puedo ayudarte con varias tareas.")
    mostrar_menu()
    comando = input(Fore.YELLOW + "\n¿Qué deseas hacer?: ")

    if comando.lower() == 'salir' or comando == '7':
        print(Fore.CYAN + "👋 Saliendo del programa. ¡Hasta luego!")
        break
    elif comando == '1':
        mostrar_fecha_hora()
    elif comando == '2':
        while True:
            print(Fore.YELLOW + "\n¿Cómo deseas abrir?")
            print("1. Con ruta escrita")
            print("2. Buscando con el explorador")
            opcion = input("Elige una opción (1 o 2): ")
            if opcion == '1':
                abrir_con_ruta()
                break
            elif opcion == '2':
                abrir_con_explorador()
                break
            else:
                print(Fore.RED + "❌ Opción no válida. Intenta de nuevo.")
    elif comando == '3':
        buscar_en_navegador()
    elif comando == '4':
        datos_curiosos()
    elif comando == '5':
        informacion_programa()
    elif comando == '6':
        clave = input("Introduce la contraseña de administrador: ")
        if clave == "admin123":
            limpiar_pantalla()
            print(Fore.GREEN + "🔑 Acceso concedido al modo administrador.")
            administrar_datos_curiosos()
        else:
            print(Fore.RED + "❌ Contraseña incorrecta. Acceso denegado.")
    else:
        print(Fore.RED + "❌ Comando no reconocido. Por favor, intenta de nuevo.")
        input(Fore.YELLOW + "Presiona Enter para continuar...")
        continue

    while True:
        continuar = input(Fore.YELLOW + "\n¿Quieres hacer algo más? (s/n): ").lower()
        if continuar == 's':
            break
        elif continuar == 'n':
            print(Fore.GREEN + "👋 Gracias por probar PROMPTY, ¡nos vemos luego!")
            exit()
        else:
            print(Fore.RED + "❌ Opción no válida. Responde con 's' para sí o 'n' para no.")