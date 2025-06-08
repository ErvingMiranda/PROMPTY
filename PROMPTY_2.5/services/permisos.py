class Permisos:
    def __init__(self):
        # Permisos por rol
        self.permisos_por_rol = {
            "admin": [
                "ver_comandos",
                "editar_voz",
                "agregar_comando",
                "eliminar_comando",
                "registrar_usuario",
                "asignar_rol",
                "agregar_datos_curiosos"
            ],
            "colaborador": [
                "ver_comandos",
                "editar_voz",  # Tiene acceso a cambiar voz/volumen/velocidad
                "agregar_comando",
                "agregar_datos_curiosos"
            ],
            "usuario": [
                "ver_comandos"
            ]
        }

    def tiene_permiso(self, rol, accion):
        rol = rol.lower()
        acciones = self.permisos_por_rol.get(rol, [])
        return accion in acciones

    def listar_permisos(self, rol):
        return self.permisos_por_rol.get(rol.lower(), [])