"""Gestiona la asociación de comandos con sus funciones ejecutables."""

from services.comandos_basicos import ComandosBasicos


class GestorComandos:
    """Encapsula la lógica para ejecutar los comandos del asistente."""
    def __init__(self, usuario_actual=None):
        """Inicializa el gestor con el usuario autenticado."""
        self.basicos = ComandosBasicos()
        self.usuario_actual = usuario_actual
        self._acciones = {
            "fecha": self._accion_fecha,
            "hora": self._accion_hora,
            "fecha_hora": self._accion_fecha_hora,
            "dia_fecha": self._accion_dia_fecha,
            "abrir_carpeta": self._accion_abrir_carpeta,
            "abrir_archivo": self._accion_abrir_archivo,
            "abrir_con_opcion": self._accion_abrir_con_opcion,
            "buscar_en_youtube": self._accion_buscar_en_youtube,
            "buscar_general": self._accion_buscar_general,
            "buscar_en_navegador": self._accion_buscar_en_navegador,
            "reproducir_musica": self._accion_reproducir_musica,
            "dato_curioso": self._accion_dato_curioso,
            "info_programa": self._accion_info_programa,
            "saludo": self._accion_saludo,
        }

    def establecer_usuario(self, usuario):
        self.usuario_actual = usuario

    def ejecutar_comando(self, clave_comando, argumentos=None, entrada_manual_func=None):
        """Ejecuta el comando indicado y devuelve el mensaje de respuesta."""
        return self.ejecutar_logica(clave_comando, argumentos, entrada_manual_func)

    def ejecutar_logica(self, clave, argumentos=None, entrada_manual_func=None):
        """Devuelve el resultado de la función asociada al comando."""
        accion = self._acciones.get(clave)
        if accion:
            return accion(argumentos, entrada_manual_func)
        return (
            "❌ Comando no reconocido. "
            "Consulta la sección de ayuda para conocer las opciones disponibles."
        )

    # Funciones de acción extraídas del diccionario ------------------------
    def _accion_fecha(self, args, entrada_func):
        return self.basicos.mostrar_fecha()

    def _accion_hora(self, args, entrada_func):
        return self.basicos.mostrar_hora()

    def _accion_fecha_hora(self, args, entrada_func):
        return self.basicos.mostrar_fecha_hora()

    def _accion_dia_fecha(self, args, entrada_func):
        return self.basicos.mostrar_dia_fecha()

    def _accion_abrir_carpeta(self, args, entrada_func):
        if args:
            return self.basicos.abrir_carpeta(args)
        return self.basicos.abrir_con_opcion(tipo="carpeta", entrada_manual_func=entrada_func)

    def _accion_abrir_archivo(self, args, entrada_func):
        return self.basicos.abrir_con_opcion(tipo="archivo", entrada_manual_func=entrada_func)

    def _accion_abrir_con_opcion(self, args, entrada_func):
        return self.basicos.abrir_con_opcion(entrada_manual_func=entrada_func)

    def _accion_buscar_en_youtube(self, args, entrada_func):
        manual = entrada_func if not args else None
        return self.basicos.buscar_en_navegador_con_opcion(
            destino_predefinido="youtube", entrada_manual_func=manual
        )

    def _accion_buscar_general(self, args, entrada_func):
        return self.basicos.buscar_en_navegador_con_opcion(entrada_manual_func=entrada_func)

    def _accion_buscar_en_navegador(self, args, entrada_func):
        return self.basicos.buscar_en_navegador_con_opcion(
            destino_predefinido="navegador", entrada_manual_func=entrada_func
        )

    def _accion_reproducir_musica(self, args, entrada_func):
        return self.basicos.reproducir_musica(entrada_manual_func=entrada_func)

    def _accion_dato_curioso(self, args, entrada_func):
        return self.basicos.mostrar_dato_curioso()

    def _accion_info_programa(self, args, entrada_func):
        return self.basicos.info_sistema(entrada_manual_func=entrada_func)

    def _accion_saludo(self, args, entrada_func):
        return self.basicos.responder_saludo()
