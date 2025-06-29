"""Funciones de autenticación compartidas entre las interfaces."""
from typing import Callable, Tuple, Optional

from services.gestor_roles import GestorRoles
from models.usuario import Usuario


class ServicioAutenticacion:
    """Centraliza la lógica para verificar credenciales de administrador."""

    def __init__(self, gestor_roles: GestorRoles | None = None):
        self.gestor_roles = gestor_roles or GestorRoles()

    def autenticar_admin(
        self,
        usuario: Usuario,
        solicitar_credenciales: Callable[[], Tuple[str | None, str | None]],
    ) -> Optional[Usuario]:
        """Devuelve un usuario administrador válido o ``None`` si falla."""
        admin = usuario
        if not usuario.es_admin():
            cif, clave = solicitar_credenciales()
            if not cif or not clave:
                return None
            admin = self.gestor_roles.autenticar(cif.strip(), clave.strip())
        if admin and admin.es_admin():
            return admin
        return None
