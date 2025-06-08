import tkinter as tk
from tkinter import simpledialog, scrolledtext

from prompty.services.gestor_comandos import GestorComandos
from prompty.services.asistente_voz import ServicioVoz
from prompty.services.gestor_roles import GestorRoles
from prompty.services.interpretador import interpretar
from prompty.utils.helpers import quitar_colores


class VistaGUI:
    """Interfaz gráfica básica para PROMPTY."""

    def __init__(self, usuario):
        self.usuario = usuario
        self.gestor_roles = GestorRoles()
        self.asistente_voz = ServicioVoz(usuario, verificar_admin_callback=self.gestor_roles.autenticar)
        self.gestor_comandos = GestorComandos(usuario)
        self.modo_respuesta = "texto"

    def iniciar(self):
        self.root = tk.Tk()
        self.root.title("PROMPTY 2.5")

        self.texto = scrolledtext.ScrolledText(self.root, width=60, height=20, state=tk.DISABLED)
        self.texto.pack(padx=10, pady=10)

        self.entrada = tk.Entry(self.root, width=50)
        self.entrada.pack(padx=10, pady=5)
        botones = tk.Frame(self.root)
        botones.pack(pady=5)
        tk.Button(botones, text="Enviar", command=self.enviar_texto).pack(side=tk.LEFT, padx=5)
        tk.Button(botones, text="Hablar", command=self.enviar_voz).pack(side=tk.LEFT, padx=5)
        tk.Button(botones, text="Salir", command=self.root.quit).pack(side=tk.LEFT, padx=5)

        self.mostrar_bienvenida()
        self.root.mainloop()

    def _imprimir(self, mensaje):
        self.texto.configure(state=tk.NORMAL)
        self.texto.insert(tk.END, quitar_colores(mensaje) + "\n")
        self.texto.configure(state=tk.DISABLED)
        self.texto.yview(tk.END)

    def mostrar_bienvenida(self):
        mensaje = (
            "¡Hola! Soy PROMPTY 2.5. Escribe o habla un comando."\
            "\nDi 'ayuda' para ver opciones o 'salir' para cerrar."
        )
        self._imprimir(mensaje)

    def enviar_texto(self):
        texto = self.entrada.get().strip()
        self.entrada.delete(0, tk.END)
        if texto:
            self.procesar(texto)

    def enviar_voz(self):
        self._imprimir("🎤 Escuchando...")
        texto = self.asistente_voz.escuchar()
        if texto:
            self._imprimir(f"🗣️ {texto}")
            self.procesar(texto)
        else:
            self._imprimir("❌ No se entendió.")

    def preguntar(self, mensaje):
        respuesta = simpledialog.askstring("PROMPTY", mensaje, parent=self.root)
        return respuesta or ""

    def procesar(self, entrada):
        comando, argumentos = interpretar(entrada)
        if comando == "configurar_voz":
            self._imprimir("La configuración de voz solo está disponible en terminal.")
            return
        if comando == "salir":
            self._imprimir("👋 Hasta luego.")
            self.root.quit()
            return
        if comando == "ayuda":
            self.mostrar_bienvenida()
            return
        if comando == "comando_no_reconocido":
            self._imprimir("❌ Comando no reconocido.")
            return

        interactivos = [
            "abrir_carpeta",
            "abrir_con_opcion",
            "buscar_en_navegador",
            "buscar_en_youtube",
        ]
        if comando in interactivos:
            respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos, entrada_manual_func=self.preguntar)
        else:
            respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos)

        self._imprimir(respuesta)
        if self.modo_respuesta in ["voz", "ambos"]:
            self.asistente_voz.hablar(respuesta)

