from colorama import Fore, Style
from prompty.utils.helpers import leer_datos, guardar_datos, ruta_absoluta

import random

RUTA_DATOS = ruta_absoluta("data/datos_curiosos.txt")

def mostrar_curiosidad():
    datos = leer_datos(RUTA_DATOS)
    if not datos:
        return f"{Fore.RED}❌ No hay datos curiosos registrados.{Style.RESET_ALL}"
    return f"{Fore.MAGENTA}💡 Dato curioso:{Style.RESET_ALL} {random.choice(datos)}"

def agregar_dato(usuario, nuevo_dato):
    if not usuario.tiene_permiso("agregar_datos_curiosos"):
        return f"{Fore.RED}❌ No tienes permiso para agregar datos.{Style.RESET_ALL}"
    
    if not nuevo_dato.strip():
        return f"{Fore.RED}❌ No se ingresó ningún dato.{Style.RESET_ALL}"

    datos = leer_datos(RUTA_DATOS)
    datos.append(nuevo_dato.strip())
    guardar_datos(RUTA_DATOS, datos)
    return f"{Fore.GREEN}✔ Dato curioso agregado con éxito.{Style.RESET_ALL}"

def eliminar_dato(usuario, indice):
    if usuario.rol != "admin":
        return f"{Fore.RED}❌ Solo los administradores pueden eliminar datos.{Style.RESET_ALL}"

    datos = leer_datos(RUTA_DATOS)
    if not datos:
        return f"{Fore.RED}❌ No hay datos para eliminar.{Style.RESET_ALL}"

    if not (0 <= indice < len(datos)):
        return f"{Fore.RED}❌ Número fuera de rango.{Style.RESET_ALL}"

    eliminado = datos.pop(indice)
    guardar_datos(RUTA_DATOS, datos)
    return f"{Fore.GREEN}✔ Dato eliminado:{Style.RESET_ALL} {eliminado}"

def obtener_lista_datos():
    return leer_datos(RUTA_DATOS)