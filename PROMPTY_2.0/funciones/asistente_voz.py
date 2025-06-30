import re
import pyttsx3
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

engine = pyttsx3.init()
engine.setProperty('rate', 175)
engine.setProperty('volume', 1.0)

def listar_voces_disponibles():
    """Devuelve una lista de voces con sus nombres e índices."""
    voces = engine.getProperty('voices')
    return [(i, voz.name) for i, voz in enumerate(voces)]

def reproducir_muestra(indice):
    """Reproduce una muestra de voz según el índice."""
    voces = engine.getProperty('voices')
    if 0 <= indice < len(voces):
        engine.setProperty('voice', voces[indice].id)
        engine.say("Esta es mi voz. ¿Te gustaría que hablara así?")
        engine.runAndWait()
    else:
        print(f"{Fore.RED}❌ Índice fuera de rango.{Style.RESET_ALL}")

def establecer_voz_por_indice(indice):
    """Establece la voz del asistente usando un índice."""
    voces = engine.getProperty('voices')
    if 0 <= indice < len(voces):
        engine.setProperty('voice', voces[indice].id)
    else:
        print(f"{Fore.YELLOW}⚠ Índice inválido. Se mantendrá la voz por defecto.{Style.RESET_ALL}")

def limpiar_emoji(texto):
    """Elimina cualquier carácter que no sea letra, número, espacio o puntuación básica."""
    return re.sub(r'[^\w\s.,;:!?()\'\"-]', '', texto)

def hablar(texto):
    """Reproduce el texto con la voz del asistente, limpiando emojis si es necesario."""
    texto_limpio = limpiar_emoji(texto)
    engine.say(texto_limpio)
    engine.runAndWait()