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
from IngresarDatosCuriosos import administrar_datos_curiosos

def limpiar_pantalla():
    os.system('cls' if os.name == 'nt' else 'clear')

def abrir_elemento(ruta):
    try:
        if platform.system() == "Windows":
            os.startfile(ruta)
        elif platform.system() == "Darwin":  # macOS
            subprocess.Popen(["open", ruta])
        else:  # Linux
            subprocess.Popen(["xdg-open", ruta])
        print(f"Abriendo: {ruta}")
    except Exception as e:
        print(f"Error al abrir {ruta}: {e}")

def mostrar_fecha_hora():
    ahora = datetime.now()
    print(f"Fecha y hora actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")

def abrir_con_ruta():
    ruta = input("\nIntroduce la ruta completa del archivo o aplicación (por ejemplo, C:/...): ")
    abrir_elemento(ruta)

def abrir_con_explorador():
    # Inicializa ventana raíz oculta para que el dialog salga al frente
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    while True:
        tipo = input("\n¿Qué deseas abrir? (1. Carpeta, 2. Aplicación): ")
        if tipo == '1':
            ruta = filedialog.askdirectory(title="Selecciona una carpeta", parent=root)
            break
        elif tipo == '2':
            ruta = filedialog.askopenfilename(title="Selecciona un archivo o aplicación", parent=root)
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

    root.destroy()  # Cierra la ventana raíz después del uso

    if ruta:
        abrir_elemento(ruta)
    else:
        print("No se seleccionó ningún archivo.")

def buscar_en_navegador():
    print("\n¿Dónde quieres hacer la búsqueda?")
    print("1. YouTube")
    print("2. Navegador (Google)")
    destino = input("Selecciona una opción (1 o 2): ")

    print("\n¿Tienes un término para buscar o un enlace (URL)?")
    print("1. Término de búsqueda")
    print("2. URL directa")
    tipo = input("Selecciona una opción (1 o 2): ")

    url = ""

    if destino == '1':  # YouTube
        if tipo == '1':
            termino = input("¿Qué deseas buscar en YouTube?: ")
            termino_formateado = termino.replace(" ", "+")
            url = f"https://www.youtube.com/results?search_query={termino_formateado}"
        elif tipo == '2':
            url = input("Introduce el enlace de YouTube: ")
    elif destino == '2':  # Google
        if tipo == '1':
            termino = input("¿Qué deseas buscar en Google?: ")
            termino_formateado = termino.replace(" ", "+")
            url = f"https://www.google.com/search?q={termino_formateado}"
        elif tipo == '2':
            url = input("Introduce el enlace de la página web: ")
    else:
        print("Opción de destino no válida.")
        return

    if tipo == '2' and not url.startswith(("http://", "https://")):
        print("La URL debe comenzar con 'http://' o 'https://'.")
        return

    chrome_path = shutil.which("chrome") or shutil.which("google-chrome")
    if chrome_path:
        webbrowser.get(f'"{chrome_path}" %s').open(url)
    else:
        webbrowser.open(url)

    print(f"Abriendo: {url}")

def datos_curiosos():
    try:
        with open("datos_curiosos.txt", "r", encoding="utf-8") as archivo:
            datos = archivo.readlines()
        if datos:
            print(f"Dato curioso: {random.choice(datos).strip()}")
        else:
            print("No hay datos curiosos disponibles.")
    except FileNotFoundError:
        # Fallback si no existe el archivo
        datos_fallback = [
            "¿Sabías que el corazón humano late más de 100,000 veces al día?",
            "Los pulpos tienen tres corazones.",
            "La miel nunca se echa a perder.",
            "La Torre Eiffel puede ser 15 cm más alta durante el verano.",
            "Los tiburones existían antes que los árboles."
        ]
        print(f"Dato curioso: {random.choice(datos_fallback)}")

def informacion_programa():
    print("\nSobre que quieres saber más:")
    print("1. Sobre los creadores")
    print("2. Sobre el programa")
    print("3. Sobre el desarrollo")
    print("4. Licencia de uso")

    opcion = input("Selecciona una opción (1-4): ")
    if opcion == '1':
        print("""
PROMPTY fue desarrollado por un equipo de estudiantes comprometidos con la innovación, como proyecto para la asignatura de \n"Introducción a la Programación" en la Universidad Americana (UAM):
        
Miembros del equipo:
    - Erving Miranda: Coordinador del proyecto y encargado del diseño general de funciones
    - Owen Bravo: Encargado de pruebas del sistema.
    - Liang Zúñiga: Encargado de documentación y apoyo técnico.
    - María Carrasco: Responsable de diseño creativo y contenido informativo.""")
    
    elif opcion == '2':
        print("""
🤖 SOBRE EL PROGRAMA

PROMPTY 1.0 es un asistente virtual de escritorio desarrollado como proyecto final del curso "Introducción a la Programación" en la Universidad Americana (UAM).

🎯 Objetivo del programa:
Desarrollar un asistente virtual de escritorio en Python que permita ejecutar tareas básicas mediante comandos escritos y por voz, integrando una interfaz gráfica amigable y una voz sintética configurable que brinde respuestas auditivas.

El proyecto busca aplicar conocimientos fundamentales del lenguaje Python en un entorno práctico, interactivo y creativo, permitiendo a los usuarios realizar acciones cotidianas como consultar la hora, abrir archivos, buscar en internet o recibir datos curiosos, todo desde una interfaz amigable.

Inspirado por asistentes como Jarvis (Iron Man) o herramientas como ChatGPT, PROMPTY combina lógica programática con una experiencia de usuario accesible y en constante evolución.

🛠️ Funciones principales:
- Mostrar fecha y hora actual.
- Abrir archivos y aplicaciones mediante rutas o explorador de archivos.
- Realizar búsquedas en YouTube o Google.
- Proporcionar datos curiosos de forma aleatoria.
- Información sobre el programa y sus creadores.

🔒 Modo administrador:
- Permite agregar o sobrescribir datos curiosos en el archivo de texto.
- Requiere contraseña para acceso.
""")
        
    elif opcion == '3':
        print("""
🛠️ PROCESO DE DESARROLLO

PROMPTY fue desarrollado en el lenguaje **Python 3.13.3**, utilizando librerías estándar como `datetime`, `os`, `webbrowser`, `tkinter.filedialog` y `random`, así como módulos personalizados.

🔸 Versión actual: **PROMPTY 1.1**
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

El proyecto fue construido paso a paso, aplicando conceptos como modularidad, condicionales, validación de entradas y manejo de archivos.
""")
        
    elif opcion == '4':
        print("""
📜 LICENCIA DE USO Y DERECHOS

© 2025 PROMPTY 1.1 | Universidad Americana (UAM)

Este software fue desarrollado exclusivamente con fines **educativos y demostrativos**. 
Todos los derechos pertenecen a los autores mencionados y a la Universidad Americana.

🔒 LICENCIA:
- Uso libre para propósitos académicos y personales.
- No se permite su distribución comercial sin autorización del equipo creador.
- Se autoriza la modificación del código siempre que se mantenga el crédito original.

Cualquier uso indebido fuera del marco académico puede violar derechos de autor o políticas institucionales.
""")
    else:
        print("Opción no válida.")

def mostrar_menu():
    print("\nComandos disponibles:")
    print("1. Mostrar fecha y hora")
    print("2. Abrir carpeta o aplicación")
    print("3. Buscar en YouTube")
    print("4. Datos curiosos")
    print("5. Sobre nosotros")
    print("6. Añadir dato curioso (admin)")
    print("7. Salir (o 'salir' para cerrar el programa)")

# Programa principal
while True:
    limpiar_pantalla()
    print("\nBienvenido a PROMPTY 1.1")
    print("Soy un asistente virtual y puedo ayudarte con varias tareas.")
    mostrar_menu()
    comando = input("\n¿Qué deseas hacer?: ")
    if comando.lower() == 'salir' or comando == '7':
        print("Saliendo del programa. ¡Hasta luego!")
        break
    elif comando == '1':
        mostrar_fecha_hora()
    elif comando == '2':
        while True:
            print("\n¿Cómo deseas abrir?")
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
                print("Opción no válida. Intenta de nuevo.")
    elif comando == '3':
        buscar_en_navegador()
    elif comando == '4':
        datos_curiosos()
    elif comando == '5':
        informacion_programa()
    elif comando == '6':
        clave = input("Introduce la contraseña de administrador: ")
        if clave == "admin123":
            administrar_datos_curiosos()
        else:
            print("❌ Contraseña incorrecta. Acceso denegado.")     
    else:
        print("Comando no reconocido. Por favor, intenta de nuevo.")
    
    while True:
        continuar = input("\n¿Quieres hacer algo más? (s/n): ").lower()
        if continuar == 's':
            break
        elif continuar == 'n':
            print("Gracias por probar PROMPTY, ¡nos vemos luego!.")
            exit()
        else:
            print("Opción no válida. Responde con 's' para sí o 'n' para no.")