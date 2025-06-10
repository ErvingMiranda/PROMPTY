from services.gestor_roles import GestorRoles
from views.terminal import VistaTerminal
from utils.helpers import limpiar_pantalla


class VistaLogin:
    """Gestiona el proceso de autenticación de usuarios."""

    def __init__(self, gestor_roles=None):
        self.gestor_roles = gestor_roles or GestorRoles()

    def iniciar(self):
        while True:
            print("🔐 Iniciar sesión en PROMPTY")
            cif = input("CIF: ").strip()
            clave = input("Contraseña: ").strip()

            usuario = self.gestor_roles.autenticar(cif, clave)

            if usuario:
                vista = VistaTerminal(usuario)
                resultado = vista.iniciar()
                if resultado == "logout":
                    limpiar_pantalla()
                    continue
                break
            else:
                print("❌ CIF o contraseña incorrectos.")

