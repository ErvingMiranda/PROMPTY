from services.gestor_roles import GestorRoles

gestor = GestorRoles()

print("🔐 Iniciar sesión en PROMPTY")
cif = input("Ingrese su CIF: ").strip()
clave = input("Ingrese su contraseña: ").strip()

usuario = gestor.autenticar(cif, clave)

if usuario:
    print(f"Bienvenido, {usuario.nombre}. Rol: {'Admin' if usuario.es_admin() else 'Usuario'}")
else:
    print("❌ CIF o contraseña incorrectos.")