import os
import re
import hashlib
import logging
import random
import string
from pathlib import Path

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

def ruta_absoluta(relativa: str) -> str:
    """Convierte una ruta relativa (desde la raíz del proyecto) a una ruta absoluta."""
    base = Path(__file__).resolve().parents[1]
    return str(base / relativa)


def hash_password(clave: str) -> str:
    """Devuelve el hash SHA-256 de la contraseña proporcionada."""
    return hashlib.sha256(clave.encode()).hexdigest()


def obtener_logger(nombre: str) -> logging.Logger:
    """Devuelve un logger configurado con un formato simple."""
    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    return logging.getLogger(nombre)

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


def generar_cif(existentes=None):
    """Genera un nuevo CIF de 8 dígitos que no esté en ``existentes``."""
    existentes = set(existentes or [])
    while True:
        cif = ''.join(random.choices(string.digits, k=8))
        if cif not in existentes:
            return cif


def generar_contrasena(longitud=8):
    """Genera una contraseña aleatoria alfanumérica."""
    caracteres = string.ascii_letters + string.digits
    return ''.join(random.choices(caracteres, k=longitud))
