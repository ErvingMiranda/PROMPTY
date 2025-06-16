import sys
import os
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QLabel,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QTextEdit,
    QLineEdit,
    QMessageBox,
    QInputDialog,
    QComboBox,
    QSlider,
    QFormLayout,
)
from PyQt6.QtGui import (
    QIcon,
    QFont,
    QPainter,
    QLinearGradient,
    QBrush,
    QPixmap,
    QColor,
)
from PyQt6.QtCore import Qt, QSize
from services.gestor_roles import GestorRoles
from services.gestor_comandos import GestorComandos
from services.interpretador import interpretar
from services.asistente_voz import ServicioVoz

def get_colored_icon(icon_path, color):
    """
    Carga el icono desde icon_path y le aplica un tinte con el color especificado.
    Devuelve un QIcon con el icono modificado.
    """
    pixmap = QPixmap(icon_path)
    if pixmap.isNull():
        print(f"⚠ No se pudo cargar la imagen: {icon_path}")
        return QIcon()
    
    # Crear un pixmap con soporte para transparencia
    tinted = QPixmap(pixmap.size())
    tinted.fill(Qt.GlobalColor.transparent)
    
    painter = QPainter(tinted)
    painter.drawPixmap(0, 0, pixmap)
    # Usamos el valor entero 5, que corresponde a SourceIn en Qt
    painter.setCompositionMode(QPainter.CompositionMode(5))
    painter.fillRect(pixmap.rect(), color)
    painter.end()
    
    return QIcon(tinted)


class ConfiguracionWindow(QWidget):
    """Permite ajustar la voz de PROMPTY."""

    def __init__(self, servicio_voz):
        super().__init__()
        self.servicio_voz = servicio_voz
        self.setWindowTitle("Configuración de voz")
        self.setGeometry(150, 150, 350, 220)

        layout = QVBoxLayout()
        form = QFormLayout()

        self.voz_combo = QComboBox()
        for idx, nombre in self.servicio_voz.listar_voces_disponibles():
            self.voz_combo.addItem(f"{idx} - {nombre}", idx)
        form.addRow("Voz", self.voz_combo)

        self.volumen_slider = QSlider(Qt.Orientation.Horizontal)
        self.volumen_slider.setRange(0, 100)
        self.volumen_slider.setValue(int(self.servicio_voz.volumen * 100))
        form.addRow("Volumen", self.volumen_slider)

        self.velocidad_slider = QSlider(Qt.Orientation.Horizontal)
        self.velocidad_slider.setRange(100, 250)
        self.velocidad_slider.setValue(self.servicio_voz.velocidad)
        form.addRow("Velocidad", self.velocidad_slider)

        layout.addLayout(form)

        boton_guardar = QPushButton("Guardar")
        boton_guardar.clicked.connect(self.guardar)
        layout.addWidget(boton_guardar)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)

        self.setLayout(layout)

    def guardar(self):
        indice = self.voz_combo.currentData()
        self.servicio_voz.cambiar_voz(int(indice))
        self.servicio_voz.cambiar_volumen(self.volumen_slider.value() / 100)
        self.servicio_voz.cambiar_velocidad(self.velocidad_slider.value())
        QMessageBox.information(self, "Configuración", "Ajustes guardados")

class UsuarioWindow(QWidget):
    """Permite modificar los datos del usuario actual."""

    def __init__(self, usuario, gestor_roles):
        super().__init__()
        self.usuario = usuario
        self.gestor_roles = gestor_roles
        self.setWindowTitle("Mi cuenta")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()
        self.nombre_edit = QLineEdit(self.usuario.nombre)
        self.pass_edit = QLineEdit()
        self.pass_edit.setPlaceholderText("Nueva contraseña")
        self.pass_edit.setEchoMode(QLineEdit.EchoMode.Password)

        layout.addWidget(QLabel("Nombre"))
        layout.addWidget(self.nombre_edit)
        layout.addWidget(QLabel("Contraseña"))
        layout.addWidget(self.pass_edit)

        boton_guardar = QPushButton("Guardar")
        boton_guardar.clicked.connect(self.guardar)
        layout.addWidget(boton_guardar)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)

        self.setLayout(layout)

    def guardar(self):
        nombre = self.nombre_edit.text().strip()
        clave = self.pass_edit.text().strip()
        self.gestor_roles.actualizar_usuario(
            self.usuario.cif,
            nombre=nombre or None,
            contrasena=clave or None,
        )
        if nombre:
            self.usuario.nombre = nombre
        QMessageBox.information(self, "Usuario", "Datos actualizados")

class AyudaWindow(QWidget):
    """Muestra información de ayuda básica."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayuda")
        self.setGeometry(250, 250, 400, 300)
        layout = QVBoxLayout()

        ruta = os.path.join(os.path.dirname(__file__), "..", "data", "info_programa.txt")
        try:
            with open(ruta, "r", encoding="utf-8") as f:
                texto = f.read()
        except Exception:
            texto = "No se encontró la información de ayuda."

        ayuda = QTextEdit(texto)
        ayuda.setReadOnly(True)
        layout.addWidget(ayuda)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)
        self.setLayout(layout)

class PROMPTYWindow(QMainWindow):
    """Ventana principal con botones interactivos y una caja de texto para salida."""

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.gestor_roles = GestorRoles()
        self.servicio_voz = ServicioVoz(usuario, verificar_admin_callback=self.gestor_roles.autenticar)
        self.gestor_comandos = GestorComandos(usuario)
        self.setWindowTitle("PROMPTY - Asistente de Voz")
        self.setGeometry(100, 100, 400, 600)
        
        # Ventanas secundarias
        self.ventana_configuracion = None
        self.ventana_usuario = None
        self.ventana_ayuda = None
        
        # Variable para alternar entre modo oscuro y claro
        self.dark_mode_enabled = False
        
        self.setup_ui()

    def paintEvent(self, event):
        """Dibuja el fondo degradado sin afectar los widgets."""
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, Qt.GlobalColor.blue)
        gradient.setColorAt(1, Qt.GlobalColor.white)
        brush = QBrush(gradient)
        painter.fillRect(self.rect(), brush)

    def setup_ui(self):
        """Configura la interfaz con los botones en la esquina superior derecha, 
        una etiqueta de bienvenida, el botón de micrófono y una caja de texto en la parte inferior."""
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        # Layout superior horizontal para los iconos de usuario, ayuda, modo oscuro y configuración
        top_layout = QHBoxLayout()
        top_layout.addStretch()  # Esto empuja los botones hacia la derecha

        self.button_usuario = self.create_icon_button("Usuario", "usuario.png")
        self.button_usuario.clicked.connect(self.ver_usuario)
        top_layout.addWidget(self.button_usuario)

        self.button_ayuda = self.create_icon_button("Ayuda", "ayuda.png")
        self.button_ayuda.clicked.connect(self.ver_ayuda)
        top_layout.addWidget(self.button_ayuda)

        self.button_modo_oscuro = self.create_icon_button("Modo Oscuro", "oscuro.png")
        self.button_modo_oscuro.clicked.connect(self.activar_modo_oscuro)
        top_layout.addWidget(self.button_modo_oscuro)

        self.button_config = self.create_icon_button("Configuración", "configuracion.png")
        self.button_config.clicked.connect(self.ver_configuracion)
        top_layout.addWidget(self.button_config)

        main_layout.addLayout(top_layout)

        # Etiqueta de bienvenida centrada
        self.label = QLabel("Hola, soy PROMPTY! \ntu asistente de voz", self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont("Roboto", 16))
        main_layout.addWidget(self.label)

        # Entrada para comandos de texto
        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Escribe un comando y presiona Enter")
        self.command_input.returnPressed.connect(self.process_command)
        main_layout.addWidget(self.command_input)

        # Botón de micrófono centrado
        self.button_microfono = QPushButton("")
        self.button_microfono.setFixedSize(100, 100)
        self.button_microfono.setStyleSheet("""
            QPushButton {
                border: none;
                border-radius: 50px;
                background-color: #c1eaf0;
            }
            QPushButton:hover {
                background-color: #ea8278;
            }
        """)
        directorio_actual = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
        ruta_icono_mic = os.path.join(directorio_actual, "microphone_icon.png")
        if os.path.exists(ruta_icono_mic):
            self.button_microfono.setIcon(QIcon(ruta_icono_mic))
            self.button_microfono.setIconSize(QSize(50, 50))
        else:
            print(f"⚠ Icono no encontrado en: {ruta_icono_mic}")
        self.button_microfono.clicked.connect(self.activate_voice)
        main_layout.addWidget(self.button_microfono, alignment=Qt.AlignmentFlag.AlignCenter)

        # Caja de texto para mostrar lo que diga el asistente de voz (solo lectura)
        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("Aquí se mostrará lo que diga el asistente de voz...")
        self.text_output.setFixedHeight(100)
        main_layout.addWidget(self.text_output)

        # Botón de salir centrado en la parte inferior
        self.button_salir = QPushButton("Salir")
        self.button_salir.setFixedSize(150, 40)
        self.button_salir.setStyleSheet("background-color: #ff6347; color: white; border-radius: 10px;")
        self.button_salir.clicked.connect(self.close)
        main_layout.addWidget(self.button_salir, alignment=Qt.AlignmentFlag.AlignCenter)

    def create_icon_button(self, tooltip, icon_file):
        """Crea un botón con icono y tooltip, sin texto visible. Guarda la ruta original en el botón."""
        button = QPushButton("")
        button.setToolTip(tooltip)
        button.setFixedSize(40, 40)
        button.setStyleSheet("border: none; background-color: transparent;")
        directorio_actual = os.path.join(os.path.dirname(os.path.abspath(__file__)), "resources")
        ruta_icono = os.path.join(directorio_actual, icon_file)
        if os.path.exists(ruta_icono):
            button.setIcon(QIcon(ruta_icono))
            button.setIconSize(QSize(30, 30))
            # Guardamos la ruta original para poder actualizar el icono según el modo
            button.icon_file = ruta_icono
        else:
            print(f"⚠ Icono no encontrado: {ruta_icono}")
        return button

    def ver_usuario(self):
        """Abre la ventana de usuario."""
        if self.ventana_usuario is None:
            self.ventana_usuario = UsuarioWindow(self.usuario, self.gestor_roles)
        self.ventana_usuario.show()

    def ver_ayuda(self):
        """Abre la ventana de ayuda."""
        if self.ventana_ayuda is None:
            self.ventana_ayuda = AyudaWindow()
        self.ventana_ayuda.show()

    def ver_configuracion(self):
        """Abre la ventana de configuración."""
        if self.ventana_configuracion is None:
            self.ventana_configuracion = ConfiguracionWindow(self.servicio_voz)
        self.ventana_configuracion.show()

    def activate_voice(self):
        """Escucha desde el micrófono e interpreta la orden."""
        self.text_output.append("🎙️ Escuchando...")
        texto = self.servicio_voz.escuchar()
        if not texto:
            self.text_output.append("❌ No se entendió el comando")
            return
        self.text_output.append(f"🗣️ {texto}")
        self.ejecutar_comando_desde_texto(texto)

    def process_command(self):
        """Interpreta lo escrito y ejecuta la acción correspondiente."""
        texto = self.command_input.text().strip()
        if texto:
            self.ejecutar_comando_desde_texto(texto)
            self.command_input.clear()

    def ejecutar_comando_desde_texto(self, texto):
        comando, argumentos = interpretar(texto)
        interactivos = {"abrir_carpeta", "abrir_con_opcion", "buscar_en_navegador", "buscar_en_youtube"}
        if comando in interactivos:
            respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos, self.preguntar)
        else:
            respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos)
        self.text_output.append(respuesta)

    def preguntar(self, mensaje):
        texto, ok = QInputDialog.getText(self, "PROMPTY", mensaje)
        return texto if ok else ""

    def activar_modo_oscuro(self):
        """Alterna entre modo oscuro y modo claro y actualiza el color de los iconos."""
        if not self.dark_mode_enabled:
            # Modo oscuro: aplicar stylesheet oscuro, actualizar iconos a blanco
            self.setStyleSheet("background-color: #222; color: white;")
            self.label.setText("Modo oscuro activado.")
            self.dark_mode_enabled = True

            # Actualizar iconos a blanco usando get_colored_icon
            self.button_usuario.setIcon(get_colored_icon(self.button_usuario.icon_file, QColor("white")))
            self.button_ayuda.setIcon(get_colored_icon(self.button_ayuda.icon_file, QColor("white")))
            self.button_modo_oscuro.setIcon(get_colored_icon(self.button_modo_oscuro.icon_file, QColor("white")))
            self.button_config.setIcon(get_colored_icon(self.button_config.icon_file, QColor("white")))
        else:
            # Modo claro: eliminar stylesheet personalizado y restaurar iconos originales
            self.setStyleSheet("")
            self.label.setText("Modo claro activado.")
            self.dark_mode_enabled = False

            # Restaurar iconos originales
            self.button_usuario.setIcon(QIcon(self.button_usuario.icon_file))
            self.button_ayuda.setIcon(QIcon(self.button_ayuda.icon_file))
            self.button_modo_oscuro.setIcon(QIcon(self.button_modo_oscuro.icon_file))
            self.button_config.setIcon(QIcon(self.button_config.icon_file))

class LoginWindow(QWidget):
    """Pantalla de inicio de sesión simple."""

    def __init__(self, gestor_roles=None):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        self.gestor_roles = gestor_roles or GestorRoles()
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.cif_input = QLineEdit()
        self.cif_input.setPlaceholderText("CIF")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.clicked.connect(self.verificar)
        self.forgot_button = QPushButton("Olvidé mi contraseña")
        self.forgot_button.clicked.connect(self.restablecer)
        layout.addWidget(QLabel("🔐 Iniciar sesión en PROMPTY"))
        layout.addWidget(self.cif_input)
        layout.addWidget(self.pass_input)
        layout.addWidget(self.login_button)
        layout.addWidget(self.forgot_button)
        self.setLayout(layout)

    def verificar(self):
        usuario = self.gestor_roles.autenticar(
            self.cif_input.text().strip(), self.pass_input.text().strip()
        )
        if usuario:
            self.hide()
            self.main = PROMPTYWindow(usuario)
            self.main.show()
        else:
            QMessageBox.warning(self, "Error", "CIF o contraseña incorrectos")

    def restablecer(self):
        cif = self.cif_input.text().strip()
        if not cif:
            QMessageBox.information(self, "Info", "Ingresa tu CIF para continuar")
            return
        nueva = self.gestor_roles.restablecer_contrasena(cif)
        if nueva:
            QMessageBox.information(
                self,
                "Contraseña temporal",
                f"Tu nueva contraseña temporal es: {nueva}",
            )
        else:
            QMessageBox.warning(self, "Error", "CIF no encontrado")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    login = LoginWindow()
    login.show()
    sys.exit(app.exec())
