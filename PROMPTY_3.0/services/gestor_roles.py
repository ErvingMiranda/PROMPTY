import json
from pathlib import Path

from models.usuario import Usuario
from utils.helpers import obtener_logger


_SIN_CAMBIO = object()


class GestorRoles:
    def __init__(self, ruta_archivo=None):
        if ruta_archivo is None:
            ruta_archivo = Path(__file__).resolve().parents[1] / 'data' / 'usuarios.json'
        ruta_archivo = Path(ruta_archivo)
        self.logger = obtener_logger(__name__)

        self.usuarios = []
        self.ruta_archivo = ruta_archivo
        self.cargar_usuarios(ruta_archivo)

    def cargar_usuarios(self, ruta: Path):
        try:
            with ruta.open("r") as archivo:
                datos = json.load(archivo)
                self.usuarios = [
                    Usuario(
                        u.get("cif"),
                        u.get("nombre"),
                        u.get("rol"),
                        u.get("contrasena"),
                        u.get("pregunta"),
                        u.get("respuesta"),
                    )
                    for u in datos["usuarios"]
                ]
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

    def guardar_usuarios(self):
        datos = {
            "usuarios": [
                {
                    "cif": u.cif,
                    "nombre": u.nombre,
                    "rol": u.rol,
                    "contrasena": u.contrasena,
                    "pregunta": u.pregunta,
                    "respuesta": u.respuesta,
                }
                for u in self.usuarios
            ]
        }
        try:
            with self.ruta_archivo.open("w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error("Error al guardar usuarios: %s", e)

    def registrar_usuario(self, nombre, rol, contrasena=None, pregunta=None, respuesta=None):
        """Registra un nuevo usuario y devuelve su CIF y contraseña."""
        from utils.helpers import generar_cif, generar_contrasena, hash_password

        existente = [u.cif for u in self.usuarios]
        cif = generar_cif(existente)
        if contrasena is None:
            contrasena_plana = generar_contrasena()
        else:
            contrasena_plana = contrasena
        hashed = hash_password(contrasena_plana)
        if respuesta is not None:
            respuesta = hash_password(respuesta)
        nuevo = Usuario(
            cif=cif,
            nombre=nombre,
            rol=rol,
            contrasena=hashed,
            pregunta=pregunta,
            respuesta=respuesta,
        )
        self.usuarios.append(nuevo)
        self.guardar_usuarios()
        return cif, contrasena_plana

    def actualizar_usuario(
        self,
        cif,
        nombre=_SIN_CAMBIO,
        contrasena=_SIN_CAMBIO,
        rol=_SIN_CAMBIO,
        pregunta=_SIN_CAMBIO,
        respuesta=_SIN_CAMBIO,
    ):
        usuario = self.obtener_usuario_por_cif(cif)
        if not usuario:
            return False
        from utils.helpers import hash_password

        if nombre is not _SIN_CAMBIO:
            usuario.nombre = nombre
        if contrasena is not _SIN_CAMBIO:
            usuario.contrasena = hash_password(contrasena)
        if pregunta is not _SIN_CAMBIO:
            usuario.pregunta = pregunta
        if respuesta is not _SIN_CAMBIO:
            usuario.respuesta = hash_password(respuesta) if respuesta is not None else None
        if rol is not _SIN_CAMBIO and rol:
            usuario.rol = rol.lower()
        self.guardar_usuarios()
        return True

    def restablecer_contrasena(self, cif, respuesta=None):
        """Genera y asigna una nueva contraseña para el usuario indicado."""
        usuario = self.obtener_usuario_por_cif(cif)
        if not usuario:
            return None
        if usuario.pregunta and not usuario.verificar_respuesta(respuesta or ""):
            return None
        from utils.helpers import generar_contrasena, hash_password

        nueva = generar_contrasena()
        usuario.contrasena = hash_password(nueva)
        self.guardar_usuarios()
        return nueva

    def listar_usuarios(self):
        return self.usuarios
