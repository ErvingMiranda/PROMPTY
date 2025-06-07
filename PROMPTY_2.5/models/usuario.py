class Usuario:
    def __init__(self, cif, nombre, rol, contrasena):
        self.cif = cif
        self.nombre = nombre
        self.rol = rol.lower()
        self.contrasena = contrasena

    def es_admin(self):
        return self.rol == "admin"

    def es_colaborador(self):
        return self.rol == "colaborador"

    def es_usuario(self):
        return self.rol == "usuario"

    def verificar_contrasena(self, clave_ingresada):
        return self.contrasena == clave_ingresada

    def __str__(self):
        rol_formateado = {
            "admin": "Administrador",
            "colaborador": "Colaborador",
            "usuario": "Usuario"
        }.get(self.rol, "Desconocido")
        return f"{self.nombre} ({rol_formateado})"