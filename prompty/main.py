from prompty.services.gestor_roles import GestorRoles
from prompty.views.terminal import VistaTerminal
from prompty.views.gui import VistaGUI

def main():
    gestor_roles = GestorRoles()

    print("🔐 Iniciar sesión en PROMPTY")
    cif = input("CIF: ").strip()
    clave = input("Contraseña: ").strip()

    usuario = gestor_roles.autenticar(cif, clave)

    if usuario:
        usar_gui = input("¿Usar la interfaz gráfica? (s/n): ").strip().lower() == "s"
        vista = VistaGUI(usuario) if usar_gui else VistaTerminal(usuario)
        vista.iniciar()
    else:
        print("❌ CIF o contraseña incorrectos.")

if __name__ == "__main__":
    main()
