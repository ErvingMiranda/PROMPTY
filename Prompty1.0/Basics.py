#Parte 1: Preparar los comandos básicos
#Implementar al menos 5 comandos funcionales que el asistente pueda ejecutar correctamente 
#1. Mostrar fecha y hora
#2. Abrir carpetas o aplicaciones
#3. Realizar búsquedas en YouTube
#4. Proporcionar datos curiosos
#5. Ofrecer información sobre el programa y sus creadores.

from datetime import datetime
import os
import webbrowser
import random

def mostrar_fecha_hora():
    ahora = datetime.now()
    print(f"Fecha y hora actual: {ahora.strftime('%d/%m/%Y %H:%M:%S')}")

def abrir_carpeta_o_aplicacion(ruta):
    try:
        os.startfile(ruta)
        print(f"Abriendo: {ruta}")
    except Exception as e:
        print(f"Error al abrir {ruta}: {e}")

def buscar_en_youtube(termino):
    url = f"https://www.youtube.com/results?search_query={termino}"
    webbrowser.open(url)
    print(f"Buscando en YouTube: {termino}")

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
        ruta = input("Introduce la ruta de la carpeta o aplicación: ")
        abrir_carpeta_o_aplicacion(ruta)
    elif comando == '3':
        termino = input("Dime que buscar en YouTube: ")
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
        continuar = input("\n¿Quieres hacer algo más? (s/n): ").lower()
        if continuar == 's':
            break
        elif continuar == 'n':
            print("Gracias por probar PROMPTY, ¡nos vemos luego!.")
            exit()
        else:
            print("Opción no válida. Responde con 's' para sí o 'n' para no.")