import json
from pathlib import Path
import logging
from models.usuario import Usuario
from utils.helpers import obtener_logger

class GestorRoles:
    def __init__(self, ruta_archivo=None):
        if ruta_archivo is None:
            ruta_archivo = Path(__file__).resolve().parents[1] / 'data' / 'usuarios.json'
        ruta_archivo = Path(ruta_archivo)
        self.logger = obtener_logger(__name__)

        self.usuarios = []
        self.cargar_usuarios(ruta_archivo)

    def cargar_usuarios(self, ruta: Path):
        try:
            with ruta.open("r", encoding="utf-8") as archivo:
                datos = json.load(archivo)
                self.usuarios = [Usuario(**u) for u in datos["usuarios"]]
        except Exception as e:
            self.logger.error("Error al cargar usuarios: %s", e)

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
