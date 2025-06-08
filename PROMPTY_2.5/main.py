from services.gestor_roles import GestorRoles
from views.terminal import VistaTerminal

def main():
    gestor_roles = GestorRoles()

    print("🔐 Iniciar sesión en PROMPTY")
    cif = input("CIF: ").strip()
    clave = input("Contraseña: ").strip()

    usuario = gestor_roles.autenticar(cif, clave)

    if usuario:
        vista = VistaTerminal(usuario)
        vista.iniciar()
    else:
        print("❌ CIF o contraseña incorrectos.")

if __name__ == "__main__":
    main()