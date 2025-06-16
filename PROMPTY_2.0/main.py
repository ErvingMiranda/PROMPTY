# === main.py ===
from utilidades.helpers import limpiar_pantalla, quitar_colores
from funciones import (
    reconocimiento_voz,
    asistente_voz,
    comandos_basicos,
    datos_curiosos,
    info_programa,
    admin
)

modo_respuesta = "voz"
voz_guardada = None
modo_admin_usado = False


def elegir_modo_respuesta():
    global modo_respuesta
    print("\n🛠️ ¿Cómo quieres que PROMPTY te responda?")
    print("1. Por voz")
    print("2. Por texto")
    print("3. Ambos")

    while True:
        opcion = input("Selecciona una opción (1-3): ").strip()
        if opcion == '1':
            modo_respuesta = "voz"
            break
        elif opcion == '2':
            modo_respuesta = "texto"
            break
        elif opcion == '3':
            modo_respuesta = "ambos"
            break
        else:
            print("❌ Opción no válida. Intenta con 1, 2 o 3.")


def seleccionar_voz():
    print("\n🎤 Elige la voz de PROMPTY antes de comenzar:")
    voces = asistente_voz.listar_voces_disponibles()
    for i, nombre in voces:
        print(f"{i}. {nombre}")

    while True:
        try:
            indice = int(input("\nEscribe el número de la voz que quieres probar: "))
            asistente_voz.reproducir_muestra(indice)

            confirmacion = input("¿Te gusta esta voz? (s/n): ").strip().lower()
            if confirmacion == 's':
                asistente_voz.establecer_voz_por_indice(indice)
                print("✔ Voz seleccionada con éxito.\n")
                break
        except ValueError:
            print("❌ Entrada inválida. Ingresa un número válido.")


def mostrar_bienvenida_texto():
    from colorama import Fore, Style
    print(f"""{Fore.CYAN}
¡Hola! Soy PROMPTY 2.0, tu asistente virtual de escritorio.
{Fore.YELLOW}Estoy listo para ayudarte con tareas básicas usando tu voz o el teclado.

{Fore.GREEN}Puedes pedirme que:
{Fore.WHITE}1. Te diga la fecha y hora actual.
2. Abra un archivo o carpeta (puedes escribir la ruta o buscarla).
3. Busque algo en YouTube o en tu navegador preferido (puedes usar un término o ingresar una URL).
4. Te comparta un dato curioso.
5. Te hable sobre el programa y sus creadores.
6. Salir del programa.
7. Acceder al modo administrador (con contraseña).{Style.RESET_ALL}
""")


def bienvenida_voz():
    asistente_voz.hablar(quitar_colores(
        "Hola, soy PROMPTY 2.0. Puedes pedirme que te diga la hora, abra una carpeta, "
        "busque en el navegador, comparta datos curiosos o te hable sobre el programa. "
        "También puedes acceder al modo administrador si tienes la contraseña."
    ))


def procesar_comando(comando):
    global modo_admin_usado

    if comando in ['1', 'uno']:
        return comandos_basicos.mostrar_fecha_hora()

    elif comando in ['2', 'dos']:
        return comandos_basicos.abrir_con_opcion()

    elif comando in ['3', 'tres']:
        return comandos_basicos.buscar_en_navegador_con_opcion()

    elif comando in ['4', 'cuatro']:
        return datos_curiosos.mostrar_curiosidad()

    elif comando in ['5', 'cinco']:
        print("Opciones: 1. Creadores | 2. Sobre el programa | 3. Desarrollo | 4. Licencia")
        opcion = input("Elige una opción (1-4): ").strip()
        if opcion in ['1', '2', '3', '4']:
            return info_programa.obtener_informacion(opcion)
        else:
            return "❌ Opción inválida."

    elif comando in ['6', 'salir', 'cerrar']:
        if modo_admin_usado:
            return "🔐 Modo administrador cerrado. Cambios guardados. Hasta pronto."
        return "👋 Hasta pronto. Fue un placer ayudarte."

    elif comando in ['7', 'siete'] or "administrador" in comando:
        clave = input("🔒 Ingresa la contraseña de administrador: ").strip()
        if clave == "admin123":
            modo_admin_usado = True
            return admin.modo_admin()
        else:
            return "❌ Contraseña incorrecta. Acceso denegado."

    elif "hora" in comando or "fecha" in comando:
        return comandos_basicos.mostrar_fecha_hora()

    elif "youtube" in comando and "navegador" not in comando:
        return comandos_basicos.buscar_en_navegador_con_opcion("youtube")

    elif "navegador" in comando and "youtube" not in comando:
        return comandos_basicos.buscar_en_navegador_con_opcion("navegador")

    elif ("youtube" in comando and "navegador" in comando) or "buscar" in comando:
        return comandos_basicos.buscar_en_navegador_con_opcion()

    elif "archivo" in comando and "carpeta" not in comando:
        return comandos_basicos.abrir_con_opcion("archivo")

    elif "carpeta" in comando and "archivo" not in comando:
        return comandos_basicos.abrir_con_opcion("carpeta")

    elif ("archivo" in comando and "carpeta" in comando) or "abrir" in comando:
        return comandos_basicos.abrir_con_opcion()


    elif "curioso" in comando or "dato" in comando:
        return datos_curiosos.mostrar_curiosidad()

    elif "información" in comando or "programa" in comando:
        print("Opciones: 1. Creadores | 2. Sobre el programa | 3. Desarrollo | 4. Licencia")
        opcion = input("Elige una opción (1-4): ").strip()
        if opcion in ['1', '2', '3', '4']:
            return info_programa.obtener_informacion(opcion)
        else:
            return "❌ Opción inválida."

    elif "salir" in comando or "cerrar" in comando:
        if modo_admin_usado:
            return "🔐 Modo administrador cerrado. Cambios guardados. Hasta pronto."
        return "👋 Hasta pronto. Fue un placer ayudarte."

    else:
        if modo_respuesta == "texto":
            return "❌ Opción no válida. Ingresa un número del 1 al 7."
        return "Lo siento, no entendí ese comando."


# === Inicio del programa ===
elegir_modo_respuesta()

if modo_respuesta in ["voz", "ambos"]:
    seleccionar_voz()

limpiar_pantalla()
mostrar_bienvenida_texto()
if modo_respuesta in ["voz", "ambos"]:
    bienvenida_voz()

# Bucle principal
while True:
    limpiar_pantalla()
    mostrar_bienvenida_texto()

    if modo_respuesta == "texto":
        instruccion = input("\n⌨️ Escribe tu comando: ").lower()
    elif modo_respuesta == "voz":
        asistente_voz.hablar("Estoy escuchando...")
        instruccion = reconocimiento_voz.escuchar_microfono()
        print(f"🗣️ Entendí: {instruccion}")
    elif modo_respuesta == "ambos":
        while True:
            tipo = input("\n¿Quieres escribir (t) o hablar (v)? ").strip().lower()
            if tipo == "t":
                instruccion = input("⌨️ Escribe tu comando: ").lower()
                break
            elif tipo == "v":
                asistente_voz.hablar("Estoy escuchando...")
                instruccion = reconocimiento_voz.escuchar_microfono()
                print(f"🗣️ Entendí: {instruccion}")
                break
            else:
                print("❌ Opción no válida. Intenta de nuevo.")

    respuesta = procesar_comando(instruccion)

    if modo_respuesta in ["texto"]:
        print(respuesta)

    if modo_respuesta in ["voz", "ambos"]:
        print(respuesta)
        asistente_voz.hablar(quitar_colores(respuesta))

    if "hasta pronto" in respuesta.lower():
        break

    input("\nPresiona Enter para continuar...")