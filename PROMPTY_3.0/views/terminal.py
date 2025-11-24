"""Vista en terminal para interactuar con PROMPTY."""

from pathlib import Path

from colorama import Fore, Style
from services.asistente_voz import ServicioVoz
from ai import AsistenteIA
from services.gestor_comandos import GestorComandos
from services.gestor_roles import GestorRoles
from services.autenticacion import ServicioAutenticacion
from services.interpretador import interpretar
from utils.helpers import limpiar_pantalla, quitar_colores


class VistaTerminal:
    def __init__(self, usuario):
        self.usuario = usuario
        self.gestor_roles = GestorRoles()
        self.auth_service = ServicioAutenticacion(self.gestor_roles)
        self.asistente_voz = ServicioVoz(usuario, verificar_admin_callback=self.gestor_roles.autenticar)
        self.gestor_comandos = GestorComandos(usuario)
        self.asistente_ia = AsistenteIA()
        self.modo_respuesta = "texto"
        self.canal_actual = "texto"

    def iniciar(self):
        self.elegir_modo_respuesta()
        limpiar_pantalla()
        print(f"\n✅ Bienvenido {self.usuario.nombre} ({self.usuario.rol})")
        self.mostrar_bienvenida()

        if self.modo_respuesta in ["voz", "ambos"]:
            self.asistente_voz.hablar(quitar_colores("Hola. Estoy listo para ayudarte."))

        while True:
            comando, argumentos, texto_original, palabra_clave = self.obtener_instruccion()

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
            if comando == "ver_arbol":
                self.mostrar_arbol()
                continue

            if comando == "comando_no_reconocido":
                respuesta = self.asistente_ia.responder(texto_original)
                self._responder(respuesta)
                continue

            if comando == "saludo":
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos)
                self._responder(respuesta)
                self._registrar_historial(texto_original, respuesta)
                continue

            # Comandos que requieren entrada
            comandos_interactivos = [
                "abrir_carpeta",
                "abrir_con_opcion",
                "buscar_general",
                "buscar_en_youtube",
                "buscar_en_navegador",
                "reproducir_musica",
            ]
            self._anunciar_accion(comando, argumentos, palabra_clave)
            if comando in comandos_interactivos:
                respuesta = self.gestor_comandos.ejecutar_comando(
                    comando,
                    argumentos,
                    entrada_manual_func=self._obtener_funcion_entrada(),
                )
            else:
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos)

            self._responder(respuesta)
            self._registrar_historial(texto_original, respuesta)

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
            self.canal_actual = "texto"
        elif self.modo_respuesta == "voz":
            self.asistente_voz.hablar("Estoy escuchando...")
            entrada = self.asistente_voz.escuchar()
            print(f"🗣️ Entendí: {entrada}")
            self.canal_actual = "voz"
        elif self.modo_respuesta == "ambos":
            while True:
                tipo = input("¿Quieres escribir (t) o hablar (v)?: ").strip().lower()
                if tipo == "t":
                    entrada = input("⌨️ Escribe tu comando: ").lower()
                    self.canal_actual = "texto"
                    break
                elif tipo == "v":
                    self.asistente_voz.hablar("Estoy escuchando...")
                    entrada = self.asistente_voz.escuchar()
                    print(f"🗣️ Entendí: {entrada}")
                    self.canal_actual = "voz"
                    break
                else:
                    print("❌ Opción no válida. Intenta de nuevo.")
        else:
            entrada = ""

        comando, argumentos, palabra_clave = interpretar(entrada)
        return comando, argumentos, entrada, palabra_clave

    def salir_programa(self):
        mensaje = "👋 Hasta luego. Fue un placer ayudarte."
        print(mensaje)
        if self.modo_respuesta in ["voz", "ambos"]:
            self.asistente_voz.hablar(quitar_colores(mensaje))
        return "exit"

    def _responder(self, mensaje: str):
        if self.modo_respuesta in ["texto", "ambos"]:
            print(mensaje)
        if self.modo_respuesta in ["voz", "ambos"]:
            self.asistente_voz.hablar(quitar_colores(mensaje))

    def _registrar_historial(self, entrada, respuesta):
        """Añade la interacción al historial de IA para conversaciones fluidas."""

        if not entrada or not respuesta:
            return
        self.asistente_ia.historial.append({"rol": "usuario", "contenido": entrada})
        self.asistente_ia.historial.append({"rol": "asistente", "contenido": quitar_colores(respuesta)})

    def _anunciar_accion(self, comando, argumentos, palabra_clave):
        """Comunica la acción detectada con un tono conversacional."""

        termino = None
        if isinstance(argumentos, dict):
            termino = argumentos.get("termino")
        if comando in ["buscar_en_youtube", "buscar_en_navegador", "buscar_general"] and termino:
            destino = "YouTube" if comando == "buscar_en_youtube" else "el navegador"
            self._responder(f"🚀 Entendido. Buscaré '{termino}' en {destino}.")
        if comando == "reproducir_musica" and termino:
            self._responder(f"🎵 Claro, reproduzco '{termino}' en YouTube Music.")

    def _obtener_funcion_entrada(self):
        """Devuelve una función para solicitar datos por voz o texto según el canal activo."""

        if self.canal_actual == "voz":
            def entrada_voz(mensaje=""):
                mensaje_limpio = quitar_colores(mensaje)
                if mensaje_limpio:
                    self.asistente_voz.hablar(mensaje_limpio)
                respuesta = self.asistente_voz.escuchar()
                print(f"🗣️ Entendí: {respuesta}")
                return (respuesta or "").strip().lower()

            return entrada_voz

        def entrada_texto(mensaje=""):
            return input(quitar_colores(mensaje)).strip()

        return entrada_texto

    def mostrar_bienvenida(self):
        print(f"{Fore.CYAN}¡Hola! Soy PROMPTY 3.0, tu asistente virtual de escritorio.{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Estoy listo para ayudarte con tareas básicas usando tu voz o el teclado.{Style.RESET_ALL}\n")
        print(f"{Fore.GREEN}Puedes pedirme que:{Style.RESET_ALL}")
        print("1. Te diga la fecha y hora actual.")
        print("2. Abra un archivo o carpeta (puedes escribir la ruta o buscarla).")
        print("3. Busque algo en YouTube o en tu navegador preferido (puedes usar un término o ingresar una URL).")
        print("4. Reproduzca música en YouTube Music.")
        print("5. Te comparta un dato curioso.")
        print("6. Te hable sobre el programa y sus creadores.")
        if self.usuario.es_admin():
            print("7. Funciones admin.")
        else:
            print("7. Acceder al modo admin (requerirá credenciales de un administrador).")
        print("8. Modificar tus datos de usuario.")
        print("9. Cerrar sesión para iniciar con otro usuario.")
        print("10. Salir del programa.")

    def mostrar_arbol(self):
        """Imprime la estructura de carpetas del proyecto."""
        root_path = Path(__file__).resolve().parents[2] / "PROMPTY_3.0"
        from utils.helpers import generar_arbol

        for linea in generar_arbol(root_path):
            print(linea)

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
        def pedir():
            cif = input("CIF del administrador: ").strip()
            clave = input("Contraseña: ").strip()
            return cif, clave

        admin = self.auth_service.autenticar_admin(self.usuario, pedir)
        if not admin:
            print("❌ Acceso denegado.")
            return
        print("🔓 Acceso concedido.")
        while True:
            print("\n⚙️ OPCIONES DE ADMINISTRADOR")
            print("1. Configurar voz")
            print("2. Gestionar usuarios")
            print("3. Gestionar datos curiosos")
            print("4. Volver al menú principal")

            opcion = input("Selecciona una opción (1-4): ").strip()

            if opcion == "1":
                self.menu_configuracion_voz()
            elif opcion == "2":
                self.menu_gestion_usuarios()
            elif opcion == "3":
                self.menu_datos_curiosos(admin)
            elif opcion == "4":
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
                nueva_pregunta = input(
                    f"Nueva pregunta [{usuario.pregunta or 'ninguna'}] (vacío para no cambiar, '-' para eliminar): "
                ).strip()
                nueva_respuesta = None
                if nueva_pregunta == "-":
                    nueva_pregunta = None
                elif nueva_pregunta:
                    nueva_respuesta = input("Nueva respuesta: ").strip()
                kwargs = {}
                if nuevo_nombre:
                    kwargs["nombre"] = nuevo_nombre
                if nueva_clave:
                    kwargs["contrasena"] = nueva_clave
                if nuevo_rol:
                    kwargs["rol"] = nuevo_rol
                if nueva_pregunta == "-":
                    kwargs["pregunta"] = None
                    kwargs["respuesta"] = None
                elif nueva_pregunta:
                    kwargs["pregunta"] = nueva_pregunta
                    if nueva_respuesta:
                        kwargs["respuesta"] = nueva_respuesta
                self.gestor_roles.actualizar_usuario(cif, **kwargs)
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
            print("3. Cambiar pregunta de seguridad")
            print("4. Volver")

            opcion = input("Selecciona una opción (1-4): ").strip()

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
                pregunta = input(
                    f"Nueva pregunta [{self.usuario.pregunta or 'ninguna'}] (vacío para no cambiar, '-' para eliminar): "
                ).strip()
                respuesta = None
                if pregunta == "-":
                    pregunta = None
                elif pregunta:
                    respuesta = input("Respuesta: ").strip()
                kwargs = {}
                if pregunta == "-":
                    kwargs["pregunta"] = None
                    kwargs["respuesta"] = None
                elif pregunta:
                    kwargs["pregunta"] = pregunta
                    if respuesta:
                        kwargs["respuesta"] = respuesta
                self.gestor_roles.actualizar_usuario(
                    self.usuario.cif,
                    **kwargs,
                )
                print("✔ Pregunta actualizada.")
            elif opcion == "4":
                break
            else:
                print("❌ Opción no válida.")

    def menu_datos_curiosos(self, admin):
        from services import datos_curiosos

        while True:
            print("\n📚 GESTIÓN DE DATOS CURIOSOS")
            print("1. Listar datos")
            print("2. Agregar dato")
            print("3. Modificar dato")
            print("4. Eliminar dato")
            print("5. Volver")

            opcion = input("Selecciona una opción (1-5): ").strip()

            if opcion == "1":
                lista = datos_curiosos.obtener_lista_datos()
                if not lista:
                    print("❌ No hay datos registrados.")
                else:
                    for i, dato in enumerate(lista, 1):
                        print(f"{i}. {dato}")
            elif opcion == "2":
                nuevo = input("Nuevo dato: ").strip()
                if nuevo:
                    print(quitar_colores(datos_curiosos.agregar_dato(admin, nuevo)))
            elif opcion == "3":
                try:
                    indice = int(input("Número de dato a modificar: ")) - 1
                    nuevo = input("Nuevo texto: ").strip()
                    print(quitar_colores(datos_curiosos.modificar_dato(admin, indice, nuevo)))
                except ValueError:
                    print("❌ Entrada inválida.")
            elif opcion == "4":
                try:
                    indice = int(input("Número de dato a eliminar: ")) - 1
                    print(quitar_colores(datos_curiosos.eliminar_dato(admin, indice)))
                except ValueError:
                    print("❌ Entrada inválida.")
            elif opcion == "5":
                break
            else:
                print("❌ Opción no válida.")
