import json
from pathlib import Path
from models.usuario import Usuario
from utils.helpers import obtener_logger

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

    def guardar_usuarios(self):
        datos = {
            "usuarios": [
                {
                    "cif": u.cif,
                    "nombre": u.nombre,
                    "rol": u.rol,
                    "contrasena": u.contrasena,
                }
                for u in self.usuarios
            ]
        }
        try:
            with self.ruta_archivo.open("w", encoding="utf-8") as archivo:
                json.dump(datos, archivo, indent=2, ensure_ascii=False)
        except Exception as e:
            self.logger.error("Error al guardar usuarios: %s", e)

    def registrar_usuario(self, nombre, rol):
        """Registra un nuevo usuario y devuelve su CIF y contraseña inicial."""
        from utils.helpers import generar_cif, generar_contrasena, hash_password

        existente = [u.cif for u in self.usuarios]
        cif = generar_cif(existente)
        contrasena_plana = generar_contrasena()
        hashed = hash_password(contrasena_plana)
        nuevo = Usuario(cif=cif, nombre=nombre, rol=rol, contrasena=hashed)
        self.usuarios.append(nuevo)
        self.guardar_usuarios()
        return cif, contrasena_plana

    def actualizar_usuario(self, cif, nombre=None, contrasena=None, rol=None):
        usuario = self.obtener_usuario_por_cif(cif)
        if not usuario:
            return False
        from utils.helpers import hash_password

        if nombre:
            usuario.nombre = nombre
        if contrasena:
            usuario.contrasena = hash_password(contrasena)
        if rol:
            usuario.rol = rol.lower()
        self.guardar_usuarios()
        return True

    def restablecer_contrasena(self, cif):
        """Genera y asigna una nueva contraseña para el usuario indicado."""
        usuario = self.obtener_usuario_por_cif(cif)
        if not usuario:
            return None
        from utils.helpers import generar_contrasena, hash_password

        nueva = generar_contrasena()
        usuario.contrasena = hash_password(nueva)
        self.guardar_usuarios()
        return nueva

    def listar_usuarios(self):
        return self.usuarios
