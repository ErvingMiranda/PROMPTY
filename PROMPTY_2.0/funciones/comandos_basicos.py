from datetime import datetime
import os
import platform
import subprocess
import webbrowser
import shutil
from tkinter import Tk, filedialog
from colorama import init, Fore, Style

# Inicializar colorama
init(autoreset=True)

def mostrar_fecha_hora():
    ahora = datetime.now()
    return f"{Fore.CYAN}🕒 Fecha y hora actual:{Style.RESET_ALL} {ahora.strftime('%d/%m/%Y %H:%M:%S')}"

def abrir_elemento(ruta):
    try:
        if platform.system() == "Windows":
            os.startfile(ruta)
        elif platform.system() == "Darwin":
            subprocess.Popen(["open", ruta])
        else:
            subprocess.Popen(["xdg-open", ruta])
        return f"{Fore.GREEN}✔ Abriendo:{Style.RESET_ALL} {ruta}"
    except Exception as e:
        return f"{Fore.RED}❌ Error al abrir {ruta}:{Style.RESET_ALL} {e}"

def seleccionar_ruta(tipo):
    """Abre una ventana para seleccionar archivo o carpeta según el tipo indicado."""
    root = Tk()
    root.withdraw()
    root.attributes("-topmost", True)

    try:
        if tipo == 'carpeta':
            return filedialog.askdirectory(title="Selecciona una carpeta", parent=root)
        elif tipo == 'archivo':
            return filedialog.askopenfilename(title="Selecciona un archivo o aplicación", parent=root)
    finally:
        root.destroy()

def abrir_con_opcion(tipo=None):
    """Abre un archivo o carpeta, permitiendo al usuario elegir la forma de selección."""
    if tipo not in ['archivo', 'carpeta']:
        tipo = input(f"{Fore.CYAN}¿Qué deseas abrir? (carpeta o archivo):{Style.RESET_ALL} ").strip().lower()
        if tipo not in ["carpeta", "archivo"]:
            return f"{Fore.RED}❌ Tipo no válido.{Style.RESET_ALL}"

    metodo = input(f"{Fore.CYAN}¿Deseas escribir la ruta (1) o buscarla en el explorador (2)?{Style.RESET_ALL} ").strip()
    if metodo == '1':
        ruta = input("Escribe la ruta completa: ").strip()
    elif metodo == '2':
        ruta = seleccionar_ruta(tipo)
    else:
        return f"{Fore.RED}❌ Opción inválida.{Style.RESET_ALL}"

    if ruta:
        return abrir_elemento(ruta)
    return f"{Fore.RED}❌ No se proporcionó ninguna ruta.{Style.RESET_ALL}"

def construir_url(busqueda, destino):
    if destino == "youtube":
        return f"https://www.youtube.com/results?search_query={busqueda.replace(' ', '+')}"
    elif destino == "navegador":
        return f"https://www.google.com/search?q={busqueda.replace(' ', '+')}"
    return None

def abrir_url(url):
    if not url.startswith(("http://", "https://", "https://www.", "http://www.")):
        return f"{Fore.RED}❌ La URL debe comenzar con 'http://' o 'https://'.{Style.RESET_ALL}"

    chrome_path = shutil.which("chrome") or shutil.which("google-chrome")
    try:
        if chrome_path:
            webbrowser.get(f'"{chrome_path}" %s').open(url)
        else:
            webbrowser.open(url)
        return f"{Fore.GREEN}✔ Abriendo:{Style.RESET_ALL} {url}"
    except Exception as e:
        return f"{Fore.RED}❌ Error al abrir el navegador:{Style.RESET_ALL} {e}"

def buscar_en_navegador_con_opcion(destino_predefinido=None):
    if destino_predefinido not in ["youtube", "navegador"]:
        destino = input(f"{Fore.CYAN}¿Dónde deseas buscar? (youtube o navegador):{Style.RESET_ALL} ").strip().lower()
    else:
        destino = destino_predefinido

    if destino not in ["youtube", "navegador"]:
        return f"{Fore.RED}❌ Opción inválida.{Style.RESET_ALL}"

    metodo = input(f"{Fore.CYAN}¿Deseas buscar un término (1) o ingresar una URL (2)?{Style.RESET_ALL} ").strip()
    if metodo == '1':
        termino = input("¿Qué deseas buscar?: ").strip()
        if not termino:
            return f"{Fore.RED}❌ El término no puede estar vacío.{Style.RESET_ALL}"
        url = construir_url(termino, destino)
    elif metodo == '2':
        url = input("Introduce la URL completa: ").strip()
        if not url:
            return f"{Fore.RED}❌ La URL no puede estar vacía.{Style.RESET_ALL}"
    else:
        return f"{Fore.RED}❌ Opción inválida.{Style.RESET_ALL}"

    return abrir_url(url)