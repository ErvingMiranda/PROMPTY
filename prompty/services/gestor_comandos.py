from prompty.services.comandos_basicos import ComandosBasicos

class GestorComandos:
    def __init__(self, usuario_actual=None):
        self.basicos = ComandosBasicos()
        self.usuario_actual = usuario_actual

    def establecer_usuario(self, usuario):
        self.usuario_actual = usuario

    def ejecutar_comando(self, clave_comando, argumentos=None, entrada_manual_func=None):
        return self.ejecutar_logica(clave_comando, argumentos, entrada_manual_func)

    def ejecutar_logica(self, clave, argumentos=None, entrada_manual_func=None):
        match clave:
            case "fecha":
                return self.basicos.mostrar_fecha()

            case "hora":
                return self.basicos.mostrar_hora()

            case "fecha_hora":
                return self.basicos.mostrar_fecha_hora()

            case "abrir_carpeta":
                if argumentos:
                    return self.basicos.abrir_carpeta(argumentos)
                else:
                    return self.basicos.abrir_con_opcion(tipo="carpeta", entrada_manual_func=entrada_manual_func)

            case "abrir_archivo":
                return self.basicos.abrir_con_opcion(tipo="archivo", entrada_manual_func=entrada_manual_func)

            case "abrir_con_opcion":
                return self.basicos.abrir_con_opcion(entrada_manual_func=entrada_manual_func)

            case "buscar_en_youtube":
                if argumentos:
                    return self.basicos.buscar_en_navegador_con_opcion(destino_predefinido="youtube", entrada_manual_func=None)
                else:
                    return self.basicos.buscar_en_navegador_con_opcion(destino_predefinido="youtube", entrada_manual_func=entrada_manual_func)

            case "buscar_en_navegador":
                return self.basicos.buscar_en_navegador_con_opcion(entrada_manual_func=entrada_manual_func)

            case "buscar_general":
                return self.basicos.buscar_en_navegador_con_opcion(entrada_manual_func=entrada_manual_func)

            case "dato_curioso":
                return self.basicos.mostrar_dato_curioso()

            case "info_programa":
                return self.basicos.info_sistema()

            case _:
                return "❌ Comando no reconocido."