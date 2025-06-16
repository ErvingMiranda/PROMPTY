from services.gestor_comandos import GestorComandos
from services.asistente_voz import ServicioVoz
from services.gestor_roles import GestorRoles
from services.interpretador import interpretar
from utils.helpers import quitar_colores, limpiar_pantalla
from colorama import Fore, Style

class VistaTerminal:
    def __init__(self, usuario):
        self.usuario = usuario
        self.gestor_roles = GestorRoles()
        self.asistente_voz = ServicioVoz(usuario, verificar_admin_callback=self.gestor_roles.autenticar)
        self.gestor_comandos = GestorComandos(usuario)
        self.modo_respuesta = "texto"

    def iniciar(self):
        self.elegir_modo_respuesta()
        limpiar_pantalla()
        print(f"\n✅ Bienvenido {self.usuario.nombre} ({self.usuario.rol})")
        self.mostrar_bienvenida()

        if self.modo_respuesta in ["voz", "ambos"]:
            self.asistente_voz.hablar(quitar_colores("Hola. Estoy listo para ayudarte."))

        while True:
            comando, argumentos = self.obtener_instruccion()

            if comando == "modo_admin":
                self.menu_admin()
                continue

            if comando == "editar_usuario":
                self.menu_editar_usuario()
                continue


            if comando == "cerrar_sesion":
                mensaje = "🔒 Sesión cerrada."
                print(mensaje)
                if self.modo_respuesta in ["voz", "ambos"]:
                    self.asistente_voz.hablar(quitar_colores(mensaje))
                limpiar_pantalla()
                return "logout"

            if comando == "salir":
                return self.salir_programa()

            if comando == "ayuda":
                self.mostrar_bienvenida()
                continue

            if comando == "comando_no_reconocido":
                mensaje = "❌ Comando no reconocido. Intenta de nuevo."
                print(mensaje)
                if self.modo_respuesta in ["voz", "ambos"]:
                    self.asistente_voz.hablar(quitar_colores(mensaje))
                continue

            # Comandos que requieren entrada
            comandos_interactivos = ["abrir_carpeta", "abrir_con_opcion", "buscar_en_navegador", "buscar_en_youtube"]
            if comando in comandos_interactivos:
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos, entrada_manual_func=input)
            else:
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos)

            if self.modo_respuesta in ["texto", "ambos"]:
                print(respuesta)
            if self.modo_respuesta in ["voz", "ambos"]:
                self.asistente_voz.hablar(quitar_colores(respuesta))

            input("\nPresiona Enter para continuar...")
            limpiar_pantalla()
            self.mostrar_bienvenida()

    def elegir_modo_respuesta(self):
        print("\n🛠️ ¿Cómo quieres que PROMPTY te responda?")
        print("1. Por voz")
        print("2. Por texto")
        print("3. Ambos")

        while True:
            opcion = input("Selecciona una opción (1-3): ").strip()
            if opcion == '1':
                self.modo_respuesta = "voz"
                break
            elif opcion == '2':
                self.modo_respuesta = "texto"
                break
            elif opcion == '3':
                self.modo_respuesta = "ambos"
                break
            else:
                print("❌ Opción no válida. Intenta con 1, 2 o 3.")

        if self.modo_respuesta in ["voz", "ambos"] and self.asistente_voz.voz_actual is None:
            self.asistente_voz.seleccionar_voz()

    def obtener_instruccion(self):
        if self.modo_respuesta == "texto":
            entrada = input("⌨️ Escribe tu comando: ").lower()
        elif self.modo_respuesta == "voz":
            self.asistente_voz.hablar("Estoy escuchando...")
            entrada = self.asistente_voz.escuchar()
            print(f"🗣️ Entendí: {entrada}")
        elif self.modo_respuesta == "ambos":
            while True:
                tipo = input("¿Quieres escribir (t) o hablar (v)?: ").strip().lower()
                if tipo == "t":
                    entrada = input("⌨️ Escribe tu comando: ").lower()
                    break
                elif tipo == "v":
                    self.asistente_voz.hablar("Estoy escuchando...")
                    entrada = self.asistente_voz.escuchar()
                    print(f"🗣️ Entendí: {entrada}")
                    break
                else:
                    print("❌ Opción no válida. Intenta de nuevo.")
        else:
            entrada = ""

        return interpretar(entrada)

    def salir_programa(self):
        mensaje = "👋 Hasta luego. Fue un placer ayudarte."
        print(mensaje)
        if self.modo_respuesta in ["voz", "ambos"]:
            self.asistente_voz.hablar(quitar_colores(mensaje))
        return "exit"

    def mostrar_bienvenida(self):
        print(f"{Fore.CYAN}¡Hola! Soy PROMPTY 3.0, tu asistente virtual de escritorio.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Estoy listo para ayudarte con tareas básicas usando tu voz o el teclado.{Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}Puedes pedirme que:{Style.RESET_ALL}")
        print("1. Te diga la fecha y hora actual.")
        print("2. Abra un archivo o carpeta (puedes escribir la ruta o buscarla).")
        print("3. Busque algo en YouTube o en tu navegador preferido (puedes usar un término o ingresar una URL).")
        print("4. Te comparta un dato curioso.")
        print("5. Te hable sobre el programa y sus creadores.")
        if self.usuario.es_admin():
            print("6. Acceder al modo administrador.")
        else:
            print("6. Acceder a funciones admin (requerirá credenciales de un administrador).")
        print("7. Modificar tus datos de usuario.")
        print("8. Cerrar sesión para iniciar con otro usuario.")
        print("9. Salir del programa.")

    def menu_configuracion_voz(self):
        while True:
            print("\n🎚️ CONFIGURACIÓN DE VOZ")
            print("1. Cambiar voz")
            print("2. Cambiar volumen")
            print("3. Cambiar velocidad")
            print("4. Volver al menú principal")

            opcion = input("Selecciona una opción (1-4): ").strip()

            if opcion == "1":
                self.asistente_voz.seleccionar_voz()
            elif opcion == "2":
                try:
                    valor = float(input("Nuevo volumen (0.0 a 1.0): "))
                    resultado = self.asistente_voz.cambiar_volumen(valor)
                    print(resultado)
                except ValueError:
                    print("❌ Entrada inválida.")
            elif opcion == "3":
                try:
                    valor = int(input("Nueva velocidad (100 a 250): "))
                    resultado = self.asistente_voz.cambiar_velocidad(valor)
                    print(resultado)
                except ValueError:
                    print("❌ Entrada inválida.")
            elif opcion == "4":
                break
            else:
                print("❌ Opción no válida.")

    def menu_admin(self):
        print("\n🔐 MODO ADMINISTRADOR")
        admin = self.usuario
        if not self.usuario.es_admin():
            cif = input("CIF del administrador: ").strip()
            clave = input("Contraseña: ").strip()
            admin = self.gestor_roles.autenticar(cif, clave)
            if not admin or not admin.es_admin():
                print("❌ Credenciales incorrectas.")
                return
        print("🔓 Acceso concedido.")
        while True:
            print("\n⚙️ OPCIONES DE ADMINISTRADOR")
            print("1. Configurar voz")
            print("2. Gestionar usuarios")
            print("3. Volver al menú principal")

            opcion = input("Selecciona una opción (1-3): ").strip()

            if opcion == "1":
                self.menu_configuracion_voz()
            elif opcion == "2":
                self.menu_gestion_usuarios()
            elif opcion == "3":
                break
            else:
                print("❌ Opción no válida.")

    def menu_gestion_usuarios(self):
        while True:
            print("\n👥 GESTIÓN DE USUARIOS")
            print("1. Crear nuevo usuario")
            print("2. Modificar un usuario existente")
            print("3. Listar usuarios")
            print("4. Volver")


            opcion = input("Selecciona una opción (1-4): ").strip()

            if opcion == "1":
                nombre = input("Nombre del nuevo usuario: ").strip()
                rol = input("Rol (usuario/colaborador/admin): ").strip().lower()
                cif, clave = self.gestor_roles.registrar_usuario(nombre, rol)
                print(f"✔ Usuario creado. CIF: {cif} Contraseña: {clave}")
            elif opcion == "2":
                cif = input("CIF del usuario a modificar: ").strip()
                usuario = self.gestor_roles.obtener_usuario_por_cif(cif)
                if not usuario:
                    print("❌ Usuario no encontrado.")
                    continue
                nuevo_nombre = input(f"Nuevo nombre [{usuario.nombre}]: ").strip()
                nueva_clave = input("Nueva contraseña (dejar vacío para no cambiar): ").strip()
                nuevo_rol = input(f"Nuevo rol [{usuario.rol}] (usuario/colaborador/admin): ").strip().lower()
                self.gestor_roles.actualizar_usuario(
                    cif,
                    nombre=nuevo_nombre or None,
                    contrasena=nueva_clave or None,
                    rol=nuevo_rol or None,
                )
                print("✔ Usuario actualizado.")
            elif opcion == "3":
                self.mostrar_tabla_usuarios()

            elif opcion == "4":
                break
            else:
                print("❌ Opción no válida.")

    def mostrar_tabla_usuarios(self):
        usuarios = self.gestor_roles.listar_usuarios()
        encabezado = f"{'CIF':<10} {'Nombre':<20} {'Contraseña':<64} Permisos"
        print(encabezado)
        print("-" * len(encabezado))
        for u in usuarios:
            permisos = ", ".join(u._permisos.listar_permisos(u.rol))
            print(f"{u.cif:<10} {u.nombre:<20} {u.contrasena:<64} {permisos}")

    def menu_editar_usuario(self):
        while True:
            print("\n✏️ MODIFICAR MIS DATOS")
            print("1. Cambiar nombre")
            print("2. Cambiar contraseña")
            print("3. Volver")

            opcion = input("Selecciona una opción (1-3): ").strip()

            if opcion == "1":
                nuevo = input("Nuevo nombre: ").strip()
                if nuevo:
                    self.gestor_roles.actualizar_usuario(self.usuario.cif, nombre=nuevo)
                    self.usuario.nombre = nuevo
                    print("✔ Nombre actualizado.")
            elif opcion == "2":
                nueva = input("Nueva contraseña: ").strip()
                if nueva:
                    self.gestor_roles.actualizar_usuario(self.usuario.cif, contrasena=nueva)
                    print("✔ Contraseña actualizada.")
            elif opcion == "3":
                break
            else:
                print("❌ Opción no válida.")
