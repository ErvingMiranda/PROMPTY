import speech_recognition as sr
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

reconocedor = sr.Recognizer()

def escuchar_microfono(tiempo_espera=1, tiempo_limite=5):
    with sr.Microphone() as fuente:
        print(f"{Fore.MAGENTA}🎙️ Escuchando...{Style.RESET_ALL}")
        reconocedor.adjust_for_ambient_noise(fuente, duration=tiempo_espera)
        try:
            audio = reconocedor.listen(fuente, timeout=tiempo_limite)
            texto = reconocedor.recognize_google(audio, language="es-NI")
            return texto.lower()
        except sr.WaitTimeoutError:
            return f"{Fore.YELLOW}⏱️ No se detectó ninguna voz a tiempo.{Style.RESET_ALL}"
        except sr.UnknownValueError:
            return f"{Fore.YELLOW}🤔 No entendí lo que dijiste.{Style.RESET_ALL}"
        except sr.RequestError:
            return f"{Fore.RED}🚫 Error al conectarse con el servicio de reconocimiento de voz.{Style.RESET_ALL}"
        except Exception as e:
            return f"{Fore.RED}⚠️ Ocurrió un error inesperado:{Style.RESET_ALL} {e}"