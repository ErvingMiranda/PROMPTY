import pyttsx3
import speech_recognition as sr
import re
import time
from num2words import num2words
from data import config
from services.permisos import Permisos
from utils.helpers import limpiar_emoji, quitar_colores
from services.comandos_basicos import MESES


class ServicioVoz:
    def __init__(self, usuario, verificar_admin_callback=None):
        self.recognizer = sr.Recognizer()
        self.usuario = usuario
        self.permisos = Permisos()
        self.verificar_admin = verificar_admin_callback

        # Valores por defecto obtenidos de la configuración
        self.voz_actual = None
        self.velocidad = config.VELOCIDAD_POR_DEFECTO
        self.volumen = config.VOLUMEN_POR_DEFECTO

        self.engine = None
        self._init_engine()

        # Establecer la voz configurada si existe
        try:
            self.establecer_voz_por_indice(config.VOZ_POR_DEFECTO)
        except Exception:
            pass

    def _init_engine(self):
        """Crea un motor de voz nuevo con la configuración actual."""
        self.engine = pyttsx3.init()
        self.engine.setProperty("rate", self.velocidad)
        self.engine.setProperty("volume", self.volumen)
        if self.voz_actual:
            self.engine.setProperty("voice", self.voz_actual)

    def _ensure_engine(self):
        """Recrea el motor si no ha sido inicializado."""
        if self.engine is None:
            self._init_engine()

    def _formatear_fecha_hora(self, texto: str) -> str | None:
        """Convierte una cadena con fecha y hora numerica en una frase mas
        natural. Devuelve ``None`` si no coincide con el patron esperado."""
        m = re.search(r"(\d{2})/(\d{2})/(\d{4})\s+(\d{2}):(\d{2})(?::(\d{2}))?", texto)
        if not m:
            m = re.search(r"(\d{2})(\d{2})(\d{4})\s+(\d{2}):(\d{2})(?::(\d{2}))?", texto)
        if not m:
            return None
        dia, mes, anio, hora, minuto, _ = m.groups()
        try:
            dia = int(dia)
            mes = MESES[int(mes) - 1]
            anio_pal = num2words(int(anio), lang="es")
            h = int(hora) % 12 or 12
            h_pal = num2words(h, lang="es")
            min_val = int(minuto)
            if min_val == 0:
                minuto_pal = "en punto"
            elif min_val == 30:
                minuto_pal = "y media"
            elif min_val == 15:
                minuto_pal = "y cuarto"
            else:
                minuto_pal = f"y {num2words(min_val, lang='es')}"
        except Exception:
            return None
        return f"Hoy es {num2words(dia, lang='es')} de {mes} de {anio_pal}, son las {h_pal} {minuto_pal}"

    def _normalizar_numeros(self, texto: str) -> str:
        """Convierte cifras numéricas a palabras en español para una
        pronunciación más natural."""

        def reemplazar(match: re.Match) -> str:
            numero = match.group(0).replace(',', '.')
            try:
                if '.' in numero:
                    valor = float(numero)
                else:
                    valor = int(numero)
                return num2words(valor, lang="es")
            except Exception:
                return match.group(0)

        return re.sub(r"\d+(?:[.,]\d+)?", reemplazar, texto)

    def hablar(self, texto):
        texto_sin_colores = quitar_colores(texto)
        texto_limpio = limpiar_emoji(texto_sin_colores)
        natural = self._formatear_fecha_hora(texto_limpio)
        if natural is not None:
            texto_final = natural
        else:
            texto_final = self._normalizar_numeros(texto_limpio)
        # Garantizar que no haya otro loop de pyttsx3 activo y que el motor exista
        self.detener()
        self._ensure_engine()
        # Dar tiempo para que el motor se inicialice correctamente
        time.sleep(config.ESPERA_INICIAL_VOZ)
        try:
            self.engine.say(texto_final)
            self.engine.runAndWait()
        except RuntimeError:
            # Reiniciar y volver a intentar si el motor quedó en mal estado
            self.engine = None
            self._ensure_engine()
            self.engine.say(texto_final)
            self.engine.runAndWait()
        return texto_final

    def detener(self):
        """Detiene la reproducción actual y descarta el motor."""
        if self.engine is None:
            return
        if self.engine.isBusy():
            self.engine.stop()
        if getattr(self.engine, "_inLoop", False):
            try:
                self.engine.endLoop()
            except RuntimeError:
                pass
        # Descartar el motor para que se vuelva a crear al hablar de nuevo
        self.engine = None

    def escuchar(self, notify=None):
        """Escucha desde el micrófono y devuelve el texto reconocido.
        Si se proporciona ``notify`` se llamará con el mensaje de escucha en
        lugar de imprimirlo en la terminal. Devuelve ``None`` si no se entiende
        o ``"__error_red"`` si ocurre un problema de conexión."""
        with sr.Microphone() as source:
            if notify:
                notify("🎙️ Escuchando...")
            else:
                print("🎙️ Escuchando...")
            audio = self.recognizer.listen(source)
        try:
            texto = self.recognizer.recognize_google(audio, language="es-ES")
            return texto
        except sr.UnknownValueError:
            return None
        except sr.RequestError:
            return "__error_red"

    def listar_voces_disponibles(self):
        self._ensure_engine()
        voces = self.engine.getProperty("voices")
        return [(i, v.name) for i, v in enumerate(voces)]

    def reproducir_muestra(self, indice):
        self._ensure_engine()
        voces = self.engine.getProperty("voices")
        if 0 <= indice < len(voces):
            self.engine.setProperty("voice", voces[indice].id)
            self.engine.say("Esta es mi voz, ¿te gustaría que hablara así?")
            self.engine.runAndWait()

    def establecer_voz_por_indice(self, indice):
        self._ensure_engine()
        voces = self.engine.getProperty("voices")
        if 0 <= indice < len(voces):
            self.voz_actual = voces[indice].id
            self.engine.setProperty("voice", self.voz_actual)

    def seleccionar_voz(self):
        print("\n🎤 Elige la voz de PROMPTY:")
        voces = self.listar_voces_disponibles()
        for i, nombre in voces:
            print(f"{i}. {nombre}")

        while True:
            try:
                indice = int(input("Número de voz a probar: "))
                self.reproducir_muestra(indice)
                confirmar = input("¿Te gusta esta voz? (s/n): ").strip().lower()
                if confirmar == "s":
                    resultado = self.cambiar_voz(indice)
                    print(resultado)
                    break
            except (ValueError, IndexError):
                print("❌ Entrada inválida. Intenta con un número válido.")

    def cambiar_voz(self, indice):
        if self.tiene_permiso("editar_voz"):
            self.establecer_voz_por_indice(indice)
            return "✔ Voz cambiada con éxito."
        return self.requiere_autorizacion_admin("cambiar la voz", lambda: self.establecer_voz_por_indice(indice) or "✔ Voz cambiada como administrador.")

    def cambiar_volumen(self, valor):
        self._ensure_engine()
        if not 0.0 <= valor <= 1.0:
            return "❌ El volumen debe estar entre 0.0 y 1.0."
        if self.tiene_permiso("editar_voz"):
            self.volumen = valor
            self.engine.setProperty("volume", valor)
            return f"✔ Volumen cambiado a {int(valor * 100)}%."
        return self.requiere_autorizacion_admin("cambiar el volumen", lambda: self._forzar_cambio_volumen(valor))

    def _forzar_cambio_volumen(self, valor):
        self._ensure_engine()
        self.volumen = valor
        self.engine.setProperty("volume", valor)
        return f"✔ Volumen cambiado como administrador a {int(valor * 100)}%."

    def cambiar_velocidad(self, valor):
        self._ensure_engine()
        if not 100 <= valor <= 250:
            return "❌ La velocidad debe estar entre 100 y 250."
        if self.tiene_permiso("editar_voz"):
            self.velocidad = valor
            self.engine.setProperty("rate", valor)
            return f"✔ Velocidad cambiada a {valor}."
        return self.requiere_autorizacion_admin("cambiar la velocidad", lambda: self._forzar_cambio_velocidad(valor))

    def _forzar_cambio_velocidad(self, valor):
        self._ensure_engine()
        self.velocidad = valor
        self.engine.setProperty("rate", valor)
        return f"✔ Velocidad cambiada como administrador a {valor}."

    def tiene_permiso(self, accion):
        return self.permisos.tiene_permiso(self.usuario.rol, accion)

    def requiere_autorizacion_admin(self, descripcion, accion_si_autorizado):
        print(f"🔒 No tienes permiso para {descripcion}. Se requiere autenticación de administrador.")
        if self.verificar_admin:
            cif = input("CIF del administrador: ").strip()
            clave = input("Contraseña del administrador: ").strip()
            admin = self.verificar_admin(cif, clave)
            if admin:
                print("🔓 Acceso concedido.")
                return accion_si_autorizado()
        return "❌ Acceso denegado."
