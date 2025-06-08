import os
import re

def quitar_colores(texto):
    """
    Elimina los códigos de escape ANSI usados por colorama para que no sean leídos por voz.
    """
    ansi_escape = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
    return ansi_escape.sub('', texto)

def limpiar_pantalla():
    """
    Limpia la consola según el sistema operativo.
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def ruta_absoluta(relativa):
    """Convierte una ruta relativa (desde la raíz del proyecto) a una ruta absoluta."""
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base, relativa)

def leer_datos(ruta):
    """Lee un archivo de texto y devuelve una lista de líneas sin saltos."""
    try:
        with open(ruta, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        return []

def guardar_datos(ruta, lista):
    """Guarda una lista de textos en un archivo, uno por línea."""
    with open(ruta, "w", encoding="utf-8") as f:
        for linea in lista:
            f.write(f"{linea}\n")

def limpiar_emoji(texto):
    """Elimina emojis u otros caracteres no alfanuméricos para reproducir por voz."""
    return re.sub(r'[^\w\s.,;:!?()\'\"-]', '', texto or "")
