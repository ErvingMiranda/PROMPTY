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

    def responder_saludo(self):
        saludos = [
            "¡Hola! ¿En qué puedo ayudarte?",
            "Hola, ¿qué tal?",
            "¡Hola! Estoy listo para asistirte."
        ]
        return choice(saludos)

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
        entrada = entrada_manual_func or input

        if tipo not in ['archivo', 'carpeta']:
            tipo = entrada("¿Qué deseas abrir? (carpeta o archivo): ").strip().lower()

        if tipo not in ['archivo', 'carpeta']:
            return "❌ Tipo no válido."

        metodo = entrada("¿Deseas escribir la ruta (1) o buscarla en el explorador (2)? ").strip()

        if metodo == '1':
            ruta = entrada("Escribe la ruta completa: ").strip()
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
        elif destino == "musica":
            return f"https://music.youtube.com/search?q={busqueda.replace(' ', '+')}"
        return None

    def abrir_url(self, url, mensaje=None):
        """Abre la URL indicada y devuelve un mensaje apropiado."""
        if not re.match(r"^https?://", url):
            return "❌ La URL debe comenzar con 'http://' o 'https://'."

        chrome_path = shutil.which("chrome") or shutil.which("google-chrome")
        try:
            if chrome_path:
                webbrowser.get(f'"{chrome_path}" %s').open(url)
            else:
                webbrowser.open(url)
            return f"🌐 {mensaje or f'Abriendo: {url}'}"
        except Exception as e:
            return f"❌ Error al abrir el navegador: {e}"

    def reproducir_musica(self, entrada_manual_func=None):
        """Abre una búsqueda o URL en YouTube Music."""
        entrada = entrada_manual_func or input

        opcion = entrada(
            "¿Deseas buscar un término (1) o ingresar una URL (2)? "
        ).strip()
        if opcion == "1":
            termino = entrada("¿Qué deseas escuchar?: ").strip()
            if not termino:
                return "❌ El término no puede estar vacío."
            url = self.construir_url(termino, "musica")
            mensaje = f"Buscando: {termino}"

        elif opcion == "2":
            url = entrada("Introduce la URL completa: ").strip()
            if not url:
                return "❌ La URL no puede estar vacía."
            mensaje = None
        else:
            return "❌ Opción inválida."

        return self.abrir_url(url, mensaje)

    def buscar_en_navegador_con_opcion(self, destino_predefinido=None, entrada_manual_func=None):
        entrada = entrada_manual_func or input

        if not destino_predefinido:
            destino = entrada(
                "¿Dónde deseas buscar? (youtube, navegador o musica): "
            ).strip().lower()
        else:
            destino = destino_predefinido

        if destino not in ["youtube", "navegador", "musica"]:
            return "❌ Opción inválida."

        metodo = entrada("¿Deseas buscar un término (1) o ingresar una URL (2)? ").strip()

        if metodo == '1':
            termino = entrada("¿Qué deseas buscar?: ").strip()
            if not termino:
                return "❌ El término no puede estar vacío."
            url = self.construir_url(termino, destino)
            mensaje = f"Buscando: {termino}"
        elif metodo == '2':
            url = entrada("Introduce la URL completa: ").strip()
            if not url:
                return "❌ La URL no puede estar vacía."
            mensaje = None
        else:
            return "❌ Opción inválida."

        return self.abrir_url(url, mensaje)

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

    def info_sistema(self, ruta=None, entrada_manual_func=None):
        if ruta is None:
            ruta = os.path.join(os.path.dirname(__file__), '..', 'data', 'info_programa.txt')
        ruta = os.path.abspath(ruta)

        entrada = entrada_manual_func or input

        secciones = {
            "1": "SOBRE LOS CREADORES DE PROMPTY",
            "2": "SOBRE EL PROGRAMA",
            "3": "PROCESO DE DESARROLLO",
            "4": "LICENCIA DE USO Y DERECHOS",
        }

        while True:
            mensaje = (
                "\n¿Sobre qué deseas saber?\n"
                "1. Sobre los creadores\n"
                "2. Sobre el programa\n"
                "3. Sobre el desarrollo\n"
                "4. Sobre la licencia de uso"
            )
            if entrada_manual_func:
                opcion = entrada_manual_func(f"{mensaje}\nSelecciona una opción (1-4): ").strip()
            else:
                print(mensaje)
                opcion = entrada("Selecciona una opción (1-4): ").strip()
            titulo = secciones.get(opcion)
            if titulo:
                break
            if not entrada_manual_func:
                print("❌ Opción inválida.")

        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                lineas = archivo.readlines()
        except Exception as e:
            return f"❌ No se pudo acceder a la información del programa: {e}"

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
