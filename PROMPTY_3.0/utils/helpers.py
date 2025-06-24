import os
import re
import hashlib
import logging
import random
import string
from pathlib import Path
from pathspec import PathSpec

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


def preguntar_modo_interfaz():
    """Pregunta al usuario si desea iniciar la interfaz gráfica."""
    respuesta = input("¿Usar interfaz gráfica? [S/N]: ").strip().lower()
    return respuesta in {"s", "y", "si", "sí"}


def _cargar_gitignore(path: Path):
    """Carga las reglas de ``.gitignore`` buscando en ``path`` y sus padres."""
    for carpeta in [path] + list(path.parents):
        gi = carpeta / ".gitignore"
        if gi.exists():
            with gi.open("r", encoding="utf-8") as f:
                reglas = [l.strip() for l in f if l.strip() and not l.startswith("#")]
            return PathSpec.from_lines("gitwildmatch", reglas), carpeta
    return PathSpec.from_lines("gitwildmatch", []), path


def generar_arbol(directorio: Path) -> list[str]:
    """Devuelve una representación en lista del árbol de ``directorio`` respetando ``.gitignore``."""
    directorio = directorio.resolve()
    spec, raiz = _cargar_gitignore(directorio)

    lineas: list[str] = []
    for ruta, dirs, files in os.walk(directorio):
        rel_raiz = Path(ruta).resolve().relative_to(raiz)
        if rel_raiz != Path('.') and spec.match_file(str(rel_raiz) + "/"):
            dirs[:] = []
            continue

        dirs[:] = [d for d in dirs if not spec.match_file(str(rel_raiz / d) + "/")]
        archivos = [f for f in files if not spec.match_file(str(rel_raiz / f))]

        nivel = len(Path(ruta).relative_to(directorio).parts)
        indent = "    " * nivel
        lineas.append(f"{indent}{Path(ruta).name}/")
        for f in archivos:
            lineas.append(f"{indent}    {f}")
    return lineas
