import os
import webbrowser
import random
from datetime import datetime
from tkinter import Tk, filedialog

def mostrar_fecha_hora():
    ahora = datetime.now()
    print(f"Fecha y hora actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")

def abrir_con_ruta():
    ruta = input("Introduce la ruta completa del archivo o aplicación (por ejemplo, C:/...): ")
    try:
        os.startfile(ruta)
        print(f"Abriendo: {ruta}")
    except Exception as e:
        print(f"Error al abrir {ruta}: {e}")

def abrir_con_explorador():
    root = Tk()
    root.withdraw()
    ruta = filedialog.askopenfilename(title="Selecciona un archivo o aplicación")

    if ruta:
        try:
            os.startfile(ruta)
            print(f"Abriendo: {ruta}")
        except Exception as e:
            print(f"Error al abrir: {e}")
    else:
        print("No se seleccionó ningún archivo.")

def buscar_en_youtube(termino):
    url = f"https://www.youtube.com/results?search_query={termino}"
    webbrowser.open(url)
    print(f"Buscando en YouTube: {termino}")

def datos_curiosos():
    datos = [
        "¿Sabías que el corazón humano late más de 100,000 veces al día?",
        "Los pulpos tienen tres corazones.",
        "La miel nunca se echa a perder.",
        "La Torre Eiffel puede ser 15 cm más alta en verano.",
        "Los tiburones existían antes que los árboles."
    ]
    print(f"Dato curioso: {random.choice(datos)}")

def informacion_programa():
    info = (
        "PROMPTY 1.0 - Tu asistente virtual\n"
        "Desarrollado por estudiantes de Introducción a la Programación.\n"
        "Creado para ayudar en tareas básicas y practicar Python."
    )
    print(info)

def mostrar_menu():
    print("\nComandos disponibles:")
    print("1. Mostrar fecha y hora")
    print("2. Abrir carpeta o aplicación")
    print("3. Buscar en YouTube")
    print("4. Datos curiosos")
    print("5. Sobre nosotros")
    print("6. Salir")

# Programa principal
print("Bienvenido a PROMPTY 1.0")
print("Soy un asistente virtual y puedo ayudarte con varias tareas.")
print("Escribe 'ayuda' para ver los comandos disponibles.")

while True:
    mostrar_menu()
    comando = input("¿Qué deseas hacer?: ")

    if comando == '1':
        mostrar_fecha_hora()
    elif comando == '2':
        print("\n¿Cómo deseas abrir?")
        print("1. Con ruta escrita")
        print("2. Buscando con el explorador")
        opcion = input("Elige una opción (1 o 2): ")
        if opcion == '1':
            abrir_con_ruta()
        elif opcion == '2':
            abrir_con_explorador()
        else:
            print("Opción no válida. Regresando al menú principal.")
    elif comando == '3':
        termino = input("Dime qué buscar en YouTube: ")
        buscar_en_youtube(termino)
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
        continuar = input("¿Quieres hacer algo más? (s/n): ").lower()
        if continuar == 's':
            break
        elif continuar == 'n':
            print("Gracias por usar PROMPTY.")
            exit()
        else:
            print("Opción no válida. Responde con 's' para sí o 'n' para no.")