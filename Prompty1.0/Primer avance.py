#Parte 1: Preparar los comandos básicos
#Implementar al menos 5 comandos funcionales que el asistente pueda ejecutar correctamente 
#1. Mostrar fecha y hora
#2. Abrir carpetas o aplicaciones
#3. Realizar búsquedas en YouTube o el navegador
#4. Proporcionar datos curiosos
#5. Ofrecer información sobre el programa y sus creadores.

from datetime import datetime
import os
from tkinter import filedialog
import webbrowser
import shutil
import random

def mostrar_fecha_hora():
    ahora = datetime.now()
    print(f"Fecha y hora actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")

def abrir_con_ruta():
    ruta = input("\nIntroduce la ruta completa del archivo o aplicación (por ejemplo, C:/...): ")
    try:
        os.startfile(ruta)
        print(f"Abriendo: {ruta}")
    except Exception as e:
        print(f"Error al abrir {ruta}: {e}")

def abrir_con_explorador():
    while True:
        tipo = input("\n¿Qué deseas abrir? (1. Carpeta, 2. Aplicación): ")
        if tipo == '1':
            ruta = filedialog.askdirectory(title="Selecciona una carpeta")
            break
        elif tipo == '2':
            ruta = filedialog.askopenfilename(title="Selecciona un archivo o aplicación")
            break
        else:
            print("Opción no válida. Intenta de nuevo.")

    if ruta:
        try:
            os.startfile(ruta)
            print(f"Abriendo: {ruta}")
        except Exception as e:
            print(f"Error al abrir: {e}")
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
    elif destino == '2':  # Navegador (Google)
        if tipo == '1':
            termino = input("¿Qué deseas buscar en Google?: ")
            termino_formateado = termino.replace(" ", "+")
            url = f"https://www.google.com/search?q={termino_formateado}"
        elif tipo == '2':
            url = input("Introduce el enlace de la página web: ")
    else:
        print("Opción de destino no válida.")
        return

    # Validar URL si es directa
    if tipo == '2' and not url.startswith(("http://", "https://")):
        print("La URL debe comenzar con 'http://' o 'https://'.")
        return

    # Intentar abrir con Google Chrome si está disponible
    chrome_path = shutil.which("chrome") or shutil.which("google-chrome")
    if chrome_path:
        webbrowser.get(f'"{chrome_path}" %s').open(url)
    else:
        webbrowser.open(url)

    print(f"Abriendo: {url}")

def datos_curiosos():
    datos = [
        "¿Sabías que el corazón humano late más de 100,000 veces al día?",
        "Los pulpos tienen tres corazones.",
        "La miel nunca se echa a perder.",
        "La Torre Eiffel puede ser 15 cm más alta durante el verano.",
        "Los tiburones existían antes que los árboles."
    ]
    print(f"Dato curioso: {random.choice(datos)}")

def informacion_programa():
    info = (
        "\nPROMPTY 1.0 - Tu asistente virtual\n"
        "Desarrollado por estudiantes de UAM, para la asignatura de Introducción a la Programación.\n"
        "Creado para ayudar en tareas básicas y practicar Python.\n"
        "Creadores: Erving Miranda, Owen Bravo, Liang Zúñiga y María Carrasco"
    )
    print(info)

def mostrar_menu():
    print("\nComandos disponibles:")
    print("1. Mostrar fecha y hora")
    print("2. Abrir carpeta o aplicación")
    print("3. Buscar en YouTube")
    print("4. Datos curiosos")
    print("5. Sobre nosotros")
    print("6. Salir (o 'salir' para cerrar el programa)")

#Programa principal
while True:
    print("\nBienvenido a PROMPTY 1.0")
    print("Soy un asistente virtual y puedo ayudarte con varias tareas.")
    mostrar_menu()
    comando = input("\n¿Qué deseas hacer?: ")
    if comando.lower() == 'salir':
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
        print("Saliendo del programa. ¡Hasta luego!")
        break
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