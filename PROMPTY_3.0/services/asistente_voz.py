import pyttsx3
import speech_recognition as sr
import threading
from data import config
from services.permisos import Permisos
from utils.helpers import limpiar_emoji, quitar_colores


class ServicioVoz:
    def __init__(self, usuario, verificar_admin_callback=None):
        self.engine = pyttsx3.init()
        self.recognizer = sr.Recognizer()
        self.usuario = usuario
        self.permisos = Permisos()
        self.verificar_admin = verificar_admin_callback

        # Valores por defecto obtenidos de la configuración
        self.voz_actual = None
        self.velocidad = config.VELOCIDAD_POR_DEFECTO
        self.volumen = config.VOLUMEN_POR_DEFECTO

        # Control de reproducción de voz
        self._speech_thread = None
        self._speech_lock = threading.Lock()

        self.engine.setProperty("rate", self.velocidad)
        self.engine.setProperty("volume", self.volumen)

        # Establecer la voz configurada si existe
        try:
            self.establecer_voz_por_indice(config.VOZ_POR_DEFECTO)
        except Exception:
            pass

    def hablar(self, texto):
        """Reproduce ``texto`` interrumpiendo cualquier reproducción previa."""
        texto_sin_colores = quitar_colores(texto)
        texto_limpio = limpiar_emoji(texto_sin_colores)

        def reproducir():
            self.engine.say(texto_limpio)
            self.engine.runAndWait()

        with self._speech_lock:
            if self._speech_thread and self._speech_thread.is_alive():
                self.engine.stop()
                self._speech_thread.join()
                # Al llamar a stop se pierden algunas propiedades,
                # por lo que las restablecemos.
                self.engine.setProperty("voice", self.voz_actual)
                self.engine.setProperty("rate", self.velocidad)
                self.engine.setProperty("volume", self.volumen)

            self._speech_thread = threading.Thread(target=reproducir, daemon=True)
            self._speech_thread.start()
        return texto_limpio

    def esperar_fin(self):
        """Bloquea hasta que termine la reproducción actual (si existe)."""
        hilo = None
        with self._speech_lock:
            hilo = self._speech_thread
        if hilo:
            hilo.join()

    def escuchar(self, notify=None):
        """Escucha desde el micrófono y devuelve el texto reconocido.
        Si se proporciona ``notify`` se llamará con el mensaje de escucha en
        lugar de imprimirlo en la terminal. Devuelve ``None`` si no se entiende
        o ``"__error_red"`` si ocurre un problema de conexión."""
        # Asegura que no haya reproducción en curso antes de escuchar
        self.esperar_fin()
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
        voces = self.engine.getProperty("voices")
        return [(i, v.name) for i, v in enumerate(voces)]

    def reproducir_muestra(self, indice):
        voces = self.engine.getProperty("voices")
        if 0 <= indice < len(voces):
            self.engine.setProperty("voice", voces[indice].id)
            self.engine.say("Esta es mi voz, ¿te gustaría que hablara así?")
            self.engine.runAndWait()

    def establecer_voz_por_indice(self, indice):
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
        if not 0.0 <= valor <= 1.0:
            return "❌ El volumen debe estar entre 0.0 y 1.0."
        if self.tiene_permiso("editar_voz"):
            self.volumen = valor
            self.engine.setProperty("volume", valor)
            return f"✔ Volumen cambiado a {int(valor * 100)}%."
        return self.requiere_autorizacion_admin("cambiar el volumen", lambda: self._forzar_cambio_volumen(valor))

    def _forzar_cambio_volumen(self, valor):
        self.volumen = valor
        self.engine.setProperty("volume", valor)
        return f"✔ Volumen cambiado como administrador a {int(valor * 100)}%."

    def cambiar_velocidad(self, valor):
        if not 100 <= valor <= 250:
            return "❌ La velocidad debe estar entre 100 y 250."
        if self.tiene_permiso("editar_voz"):
            self.velocidad = valor
            self.engine.setProperty("rate", valor)
            return f"✔ Velocidad cambiada a {valor}."
        return self.requiere_autorizacion_admin("cambiar la velocidad", lambda: self._forzar_cambio_velocidad(valor))

    def _forzar_cambio_velocidad(self, valor):
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
