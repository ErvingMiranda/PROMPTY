import random
import os
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

# Acceso a la raíz del proyecto
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ruta = os.path.join(BASE_DIR, "datos", "datos_curiosos.txt")

FALLBACK_DATOS = [
    "¿Sabías que el corazón humano late más de 100,000 veces al día?",
    "Los pulpos tienen tres corazones.",
    "La miel nunca se echa a perder.",
    "La Torre Eiffel puede ser 15 cm más alta durante el verano.",
    "Los tiburones existían antes que los árboles."
]

def mostrar_curiosidad():
    try:
        with open(ruta, "r", encoding="utf-8") as archivo:
            curiosidades = [linea.strip() for linea in archivo if linea.strip()]
            if curiosidades:
                return f"{Fore.CYAN}🤔 Dato curioso:{Style.RESET_ALL} {random.choice(curiosidades)}"
            else:
                mensaje = f"{Fore.YELLOW}⚠ No hay datos en el archivo.{Style.RESET_ALL}"
    except FileNotFoundError:
        mensaje = f"{Fore.RED}📁 Archivo no encontrado.{Style.RESET_ALL}"
    except Exception:
        mensaje = f"{Fore.RED}❌ Hubo un problema al leer el archivo.{Style.RESET_ALL}"

    respaldo = f"{Fore.GREEN}🤖 Aquí tienes un dato de respaldo:{Style.RESET_ALL} {random.choice(FALLBACK_DATOS)}"
    return f"{mensaje}\n{respaldo}"