from services.gestor_comandos import GestorComandos
from services.asistente_voz import ServicioVoz
from services.gestor_roles import GestorRoles
from services.interpretador import interpretar
from utils.helpers import quitar_colores
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
        print(f"\n✅ Bienvenido {self.usuario.nombre} ({self.usuario.rol})")
        self.mostrar_bienvenida()

        if self.modo_respuesta in ["voz", "ambos"]:
            self.asistente_voz.hablar(quitar_colores("Hola. Estoy listo para ayudarte."))

        while True:
            comando, argumentos = self.obtener_instruccion()

            if comando == "configurar_voz":
                self.menu_configuracion_voz()
                continue

            if comando == "salir":
                mensaje = "👋 Hasta luego. Fue un placer ayudarte."
                print(mensaje)
                if self.modo_respuesta in ["voz", "ambos"]:
                    self.asistente_voz.hablar(quitar_colores(mensaje))
                break

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

        if self.modo_respuesta in ["voz", "ambos"]:
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

    def mostrar_bienvenida(self):
        print(f"""{Fore.CYAN}
¡Hola! Soy PROMPTY 2.5, tu asistente virtual de escritorio.
{Fore.YELLOW}Estoy listo para ayudarte con tareas básicas usando tu voz o el teclado.

{Fore.GREEN}Puedes pedirme que:{Style.RESET_ALL}
1. Te diga la fecha y hora actual.
2. Abra un archivo o carpeta (puedes escribir la ruta o buscarla).
3. Busque algo en YouTube o en tu navegador preferido (puedes usar un término o ingresar una URL).
4. Te comparta un dato curioso.
5. Te hable sobre el programa y sus creadores.
6. Salir del programa.
7. Acceder al modo administrador (con contraseña).
8. Configurar la voz de PROMPTY (di "configurar voz").
""")

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
