import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QWidget, QTextEdit
from PyQt6.QtGui import QIcon, QFont, QPainter, QLinearGradient, QBrush, QPixmap, QPainter, QColor
from PyQt6.QtCore import Qt, QSize

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
    """Ventana secundaria para configuración."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Configuración")
        self.setGeometry(150, 150, 300, 200)
        layout = QVBoxLayout()
        label = QLabel("Opciones de configuración en desarrollo...")
        layout.addWidget(label)
        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)
        self.setLayout(layout)

class UsuarioWindow(QWidget):
    """Ventana secundaria para usuario."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Usuario")
        self.setGeometry(200, 200, 300, 200)
        layout = QVBoxLayout()
        label = QLabel("Opciones de usuario en desarrollo...")
        layout.addWidget(label)
        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)
        self.setLayout(layout)

class AyudaWindow(QWidget):
    """Ventana secundaria para ayuda."""
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ayuda")
        self.setGeometry(250, 250, 300, 200)
        layout = QVBoxLayout()
        label = QLabel("Opciones de ayuda en desarrollo...")
        layout.addWidget(label)
        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)
        self.setLayout(layout)

class PROMPTYWindow(QMainWindow):
    """Ventana principal con botones interactivos y una caja de texto para salida."""
    def __init__(self):
        super().__init__()
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
            self.ventana_usuario = UsuarioWindow()
        self.ventana_usuario.show()

    def ver_ayuda(self):
        """Abre la ventana de ayuda."""
        if self.ventana_ayuda is None:
            self.ventana_ayuda = AyudaWindow()
        self.ventana_ayuda.show()

    def ver_configuracion(self):
        """Abre la ventana de configuración."""
        if self.ventana_configuracion is None:
            self.ventana_configuracion = ConfiguracionWindow()
        self.ventana_configuracion.show()

    def activate_voice(self):
        """Simula la activación de reconocimiento de voz y muestra un mensaje en la caja de texto."""
        self.label.setText("Escuchando...")
        self.text_output.setText("El asistente de voz ha comenzado a escuchar.")
        print("Se activó el reconocimiento de voz.")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PROMPTYWindow()
    window.show()
    sys.exit(app.exec())
