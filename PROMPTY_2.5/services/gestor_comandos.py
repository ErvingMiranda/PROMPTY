from services.comandos_basicos import ComandosBasicos

class GestorComandos:
    def __init__(self, usuario_actual=None):
        self.basicos = ComandosBasicos()
        self.usuario_actual = usuario_actual
        self._acciones = {
            "fecha": lambda a, e: self.basicos.mostrar_fecha(),
            "hora": lambda a, e: self.basicos.mostrar_hora(),
            "fecha_hora": lambda a, e: self.basicos.mostrar_fecha_hora(),
            "abrir_carpeta": lambda a, e: self.basicos.abrir_carpeta(a) if a else self.basicos.abrir_con_opcion(tipo="carpeta", entrada_manual_func=e),
            "abrir_archivo": lambda a, e: self.basicos.abrir_con_opcion(tipo="archivo", entrada_manual_func=e),
            "abrir_con_opcion": lambda a, e: self.basicos.abrir_con_opcion(entrada_manual_func=e),
            "buscar_en_youtube": lambda a, e: self.basicos.buscar_en_navegador_con_opcion(destino_predefinido="youtube", entrada_manual_func=e if not a else None),
            "buscar_en_navegador": lambda a, e: self.basicos.buscar_en_navegador_con_opcion(entrada_manual_func=e),
            "buscar_general": lambda a, e: self.basicos.buscar_en_navegador_con_opcion(entrada_manual_func=e),
            "dato_curioso": lambda a, e: self.basicos.mostrar_dato_curioso(),
            "info_programa": lambda a, e: self.basicos.info_sistema(),
        }

    def establecer_usuario(self, usuario):
        self.usuario_actual = usuario

    def ejecutar_comando(self, clave_comando, argumentos=None, entrada_manual_func=None):
        return self.ejecutar_logica(clave_comando, argumentos, entrada_manual_func)

    def ejecutar_logica(self, clave, argumentos=None, entrada_manual_func=None):
        accion = self._acciones.get(clave)
        if accion:
            return accion(argumentos, entrada_manual_func)
        return "❌ Comando no reconocido."
