from services.gestor_roles import GestorRoles
from views.terminal import VistaTerminal
from utils.helpers import limpiar_pantalla
from colorama import Fore, Style


class VistaLogin:
    """Gestiona el proceso de autenticación de usuarios."""

    def __init__(self, gestor_roles=None):
        self.gestor_roles = gestor_roles or GestorRoles()

    def verificar_credenciales(self, cif, clave):
        """Devuelve el usuario si las credenciales son válidas, None en caso contrario."""
        return self.gestor_roles.autenticar(cif, clave)

    def iniciar(self):
        while True:
            limpiar_pantalla()
            print(f"{Fore.CYAN}🔐 Iniciar sesión en PROMPTY{Style.RESET_ALL}")
            print("1. Iniciar sesión")
            print("2. Olvidé mi contraseña")
            print("3. Salir")
            opcion = input("Selecciona una opción: ").strip()

            if opcion == "1":
                cif = input(f"{Fore.YELLOW}CIF:{Style.RESET_ALL} ").strip()
                clave = input(f"{Fore.YELLOW}Contraseña:{Style.RESET_ALL} ").strip()
                usuario = self.verificar_credenciales(cif, clave)

                if usuario:
                    vista = VistaTerminal(usuario)
                    resultado = vista.iniciar()
                    if resultado == "logout":
                        limpiar_pantalla()
                        continue
                    break
                else:
                    print(f"{Fore.RED}❌ CIF o contraseña incorrectos.{Style.RESET_ALL}")
                    input("Presiona Enter para continuar...")
            elif opcion == "2":
                self.restablecer_contrasena()
            elif opcion == "3":
                break
            else:
                print("Opción no válida")
                input("Presiona Enter para continuar...")

    def restablecer_contrasena(self):
        limpiar_pantalla()
        print("🔑 Recuperar contraseña")
        cif = input("CIF: ").strip()
        nueva = self.gestor_roles.restablecer_contrasena(cif)
        if nueva:
            print(f"Tu nueva contraseña temporal es: {nueva}")
        else:
            print("❌ CIF no encontrado.")
        input("Presiona Enter para continuar...")

