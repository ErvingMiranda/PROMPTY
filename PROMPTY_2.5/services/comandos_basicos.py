import datetime
import os
import platform
import subprocess
import webbrowser
import shutil
from tkinter import Tk, filedialog
from random import choice
from utils.helpers import quitar_colores
import re

class ComandosBasicos:
    def mostrar_fecha(self):
        fecha_actual = datetime.datetime.now().strftime("%d/%m/%Y")
        return f"📅 La fecha de hoy es {fecha_actual}."

    def mostrar_hora(self):
        hora_actual = datetime.datetime.now().strftime("%I:%M %p")
        return f"🕒 La hora actual es {hora_actual}."

    def mostrar_fecha_hora(self):
        ahora = datetime.datetime.now()
        return f"📆 {ahora.strftime('%d/%m/%Y')} 🕒 {ahora.strftime('%H:%M:%S')}"

    def abrir_carpeta(self, ruta):
        try:
            if platform.system() == "Windows":
                os.startfile(ruta)
            elif platform.system() == "Darwin":
                subprocess.Popen(["open", ruta])
            else:
                subprocess.Popen(["xdg-open", ruta])
            return f"📂 Abriendo: {ruta}"
        except Exception as e:
            return f"❌ Error al abrir {ruta}: {e}"

    def seleccionar_ruta(self, tipo):
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

    def abrir_con_opcion(self, tipo=None, entrada_manual_func=None):
        if tipo not in ['archivo', 'carpeta']:
            if entrada_manual_func:
                tipo = entrada_manual_func("¿Qué deseas abrir? (carpeta o archivo): ").strip().lower()
            else:
                return "❌ Tipo no válido."

        if entrada_manual_func:
            metodo = entrada_manual_func("¿Deseas escribir la ruta (1) o buscarla en el explorador (2)? ").strip()
        else:
            return "❌ No se puede continuar sin función de entrada."

        if metodo == '1':
            ruta = entrada_manual_func("Escribe la ruta completa: ").strip()
        elif metodo == '2':
            ruta = self.seleccionar_ruta(tipo)
        else:
            return "❌ Opción inválida."

        if ruta:
            return self.abrir_carpeta(ruta)
        return "❌ No se proporcionó ninguna ruta."

    def construir_url(self, busqueda, destino):
        if destino == "youtube":
            return f"https://www.youtube.com/results?search_query={busqueda.replace(' ', '+')}"
        elif destino == "navegador":
            return f"https://www.google.com/search?q={busqueda.replace(' ', '+')}"
        return None

    def abrir_url(self, url):
        if not re.match(r"^https?://", url):
            return "❌ La URL debe comenzar con 'http://' o 'https://'."

        chrome_path = shutil.which("chrome") or shutil.which("google-chrome")
        try:
            if chrome_path:
                webbrowser.get(f'"{chrome_path}" %s').open(url)
            else:
                webbrowser.open(url)
            return f"🌐 Abriendo: {url}"
        except Exception as e:
            return f"❌ Error al abrir el navegador: {e}"

    def buscar_en_navegador_con_opcion(self, destino_predefinido=None, entrada_manual_func=None):
        if not destino_predefinido:
            if entrada_manual_func:
                destino = entrada_manual_func("¿Dónde deseas buscar? (youtube o navegador): ").strip().lower()
            else:
                return "❌ Sin entrada para destino."
        else:
            destino = destino_predefinido

        if destino not in ["youtube", "navegador"]:
            return "❌ Opción inválida."

        if entrada_manual_func:
            metodo = entrada_manual_func("¿Deseas buscar un término (1) o ingresar una URL (2)? ").strip()
        else:
            return "❌ Sin entrada para método."

        if metodo == '1':
            termino = entrada_manual_func("¿Qué deseas buscar?: ").strip()
            if not termino:
                return "❌ El término no puede estar vacío."
            url = self.construir_url(termino, destino)
        elif metodo == '2':
            url = entrada_manual_func("Introduce la URL completa: ").strip()
            if not url:
                return "❌ La URL no puede estar vacía."
        else:
            return "❌ Opción inválida."

        return self.abrir_url(url)

    def mostrar_dato_curioso(self):
        """Muestra un dato curioso leyendo primero del archivo externo."""
        from services import datos_curiosos

        resultado = datos_curiosos.mostrar_curiosidad()
        if "❌" in quitar_colores(resultado):
            datos = [
                "Los pulpos tienen tres corazones.",
                "Una cucharada de miel representa el trabajo de toda la vida de 12 abejas.",
                "La Torre Eiffel puede ser 15 cm más alta en verano.",
                "El sol representa el 99.86% de la masa del sistema solar.",
                "El cerebro humano puede generar unos 20 vatios de energía, lo suficiente para encender una bombilla pequeña."
            ]
            return f"🤔 Dato curioso: {choice(datos)}"
        return resultado

    def info_sistema(self, ruta=None):
        if ruta is None:
            ruta = os.path.join(os.path.dirname(__file__), '..', 'data', 'info_programa.txt')
        ruta = os.path.abspath(ruta)

        secciones = {
            "1": "SOBRE LOS CREADORES DE PROMPTY",
            "2": "SOBRE EL PROGRAMA",
            "3": "PROCESO DE DESARROLLO",
            "4": "LICENCIA DE USO Y DERECHOS",
        }

        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
        except Exception as e:
            return f"❌ No se pudo acceder a la información del programa: {e}"

        while True:
            print("\n¿Sobre qué deseas saber?")
            print("1. Sobre los creadores")
            print("2. Sobre el programa")
            print("3. Sobre el desarrollo")
            print("4. Sobre la licencia de uso")
            opcion = input("Selecciona una opción (1-4): ").strip()
            titulo = secciones.get(opcion)
            if titulo:
                break
            print("❌ Opción inválida.")

        contenido = []
        capturar = False
        for linea in lineas:
            cabecera = linea.strip()
            if cabecera in secciones.values():
                capturar = cabecera == titulo
                continue
            if capturar:
                if cabecera in secciones.values():
                    break
                contenido.append(linea.rstrip())

        return "\n".join(contenido).strip()
