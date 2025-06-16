import os
import re

def limpiar_pantalla():
    """Limpia la consola según el sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')

def capitalizar_dato(texto):
    """Capitaliza el primer carácter del texto si es un string válido."""
    if isinstance(texto, str) and texto:
        return texto[0].upper() + texto[1:]
    return texto

def quitar_colores(texto):
    """Elimina códigos ANSI (colores) de un texto para pasarlo a voz o guardarlo limpio."""
    return re.sub(r'\x1b\[[0-9;]*m', '', texto or "")