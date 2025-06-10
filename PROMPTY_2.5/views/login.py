from services.gestor_roles import GestorRoles
from views.terminal import VistaTerminal
from utils.helpers import limpiar_pantalla
from colorama import Fore, Style


class VistaLogin:
    """Gestiona el proceso de autenticación de usuarios."""

    def __init__(self, gestor_roles=None):
        self.gestor_roles = gestor_roles or GestorRoles()

    def iniciar(self):
        while True:
            print(f"{Fore.CYAN}🔐 Iniciar sesión en PROMPTY{Style.RESET_ALL}")
            cif = input(f"{Fore.YELLOW}CIF:{Style.RESET_ALL} ").strip()
            clave = input(f"{Fore.YELLOW}Contraseña:{Style.RESET_ALL} ").strip()

            usuario = self.gestor_roles.autenticar(cif, clave)

            if usuario:
                vista = VistaTerminal(usuario)
                resultado = vista.iniciar()
                if resultado == "logout":
                    limpiar_pantalla()
                    continue
                break
            else:
                print(f"{Fore.RED}❌ CIF o contraseña incorrectos.{Style.RESET_ALL}")

