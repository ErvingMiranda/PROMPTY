import os
import json
from prompty.models.usuario import Usuario

class GestorRoles:
    def __init__(self, ruta_archivo=None):
        if ruta_archivo is None:
            ruta_archivo = os.path.join(os.path.dirname(__file__), '..', 'data', 'usuarios.json')
        ruta_archivo = os.path.abspath(ruta_archivo)

        self.usuarios = []
        self.cargar_usuarios(ruta_archivo)

    def cargar_usuarios(self, ruta):
        try:
            with open(ruta, "r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                self.usuarios = [Usuario(**u) for u in datos["usuarios"]]
        except Exception as e:
            print(f"Error al cargar usuarios: {e}")

    def obtener_usuario_por_cif(self, cif):
        for u in self.usuarios:
            if u.cif == cif:
                return u
        return None

    def autenticar(self, cif, contrasena):
        usuario = self.obtener_usuario_por_cif(cif)
        if usuario and usuario.verificar_contrasena(contrasena):
            return usuario
        return None