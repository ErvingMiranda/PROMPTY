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
    QListWidget,
    QFormLayout,
)
from PyQt6.QtGui import (
    QIcon,
    QFont,
    QFontDatabase,
    QPainter,
    QLinearGradient,
    QBrush,
    QPixmap,
    QColor,
)
from PyQt6.QtCore import Qt, QSize, QTimer
from pathlib import Path
from services.gestor_roles import GestorRoles
from services.gestor_comandos import GestorComandos
from services.interpretador import interpretar
from services.asistente_voz import ServicioVoz
from utils.helpers import quitar_colores

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
RESOURCES_DIR = os.path.normpath(
    os.path.join(BASE_DIR, "..", "data", "resources")
)

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
    """Permite ajustar la voz y la fuente de PROMPTY."""

    def __init__(self, servicio_voz, fuente="Roboto", tamano=16, aplicar_fuente=None):
        super().__init__()
        self.servicio_voz = servicio_voz
        self.aplicar_fuente = aplicar_fuente
        self.setWindowTitle("Configuración")
        self.setGeometry(150, 150, 400, 260)

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

        self.font_combo = QComboBox()
        # En algunos bindings de Qt, QFontDatabase no tiene constructor por defecto
        # por lo que utilizamos sus métodos estáticos para obtener las familias
        fuentes = [str(f) for f in QFontDatabase.families()]
        self.font_combo.addItems(fuentes)
        self.font_combo.setCurrentText(fuente)
        form.addRow("Fuente", self.font_combo)

        self.size_slider = QSlider(Qt.Orientation.Horizontal)
        self.size_slider.setRange(8, 32)
        self.size_slider.setValue(tamano)
        form.addRow("Tamaño letra", self.size_slider)

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
        if self.aplicar_fuente:
            self.aplicar_fuente(
                self.font_combo.currentText(), self.size_slider.value()
            )
        # Aplicar la fuente seleccionada a esta ventana para reflejar el cambio
        self.setFont(QFont(self.font_combo.currentText(), self.size_slider.value()))
        QMessageBox.information(self, "Configuración", "Ajustes guardados")

class EditarUsuarioWindow(QWidget):
    """Permite modificar los datos del usuario actual."""

    def __init__(self, usuario, gestor_roles):
        super().__init__()
        self.usuario = usuario
        self.gestor_roles = gestor_roles
        self.setWindowTitle("Modificar datos")
        self.setGeometry(220, 220, 300, 220)

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


class UsuarioWindow(QWidget):
    """Muestra la información del usuario y acciones disponibles."""

    def __init__(self, usuario, gestor_roles, editar_callback=None, logout_callback=None):
        super().__init__()
        self.usuario = usuario
        self.gestor_roles = gestor_roles
        self.editar_callback = editar_callback
        self.logout_callback = logout_callback
        self.setWindowTitle("Mi cuenta")
        self.setGeometry(200, 200, 300, 200)

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel(f"Usuario: {self.usuario.nombre} ({self.usuario.cif}) - {self.usuario.rol}")
        )

        if self.editar_callback:
            boton_editar = QPushButton("Modificar mis datos")
            boton_editar.clicked.connect(self.editar_callback)
            layout.addWidget(boton_editar)

        if self.logout_callback:
            boton_logout = QPushButton("Cerrar sesión")
            boton_logout.clicked.connect(self.logout_callback)
            layout.addWidget(boton_logout)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)

        self.setLayout(layout)

class AyudaWindow(QWidget):
    """Ventana que muestra las opciones y comandos disponibles."""

    def __init__(self, usuario):
        super().__init__()
        self.setWindowTitle("Ayuda")
        self.setGeometry(250, 250, 400, 350)
        layout = QVBoxLayout()

        ayuda = QTextEdit()
        ayuda.setReadOnly(True)
        ayuda.setHtml(self._generar_texto(usuario))
        layout.addWidget(ayuda)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        layout.addWidget(boton_cerrar)

        self.setLayout(layout)

    def _generar_texto(self, usuario):
        items = [
            "Te diga la fecha y hora actual.",
            "Abra un archivo o carpeta (puedes escribir la ruta o buscarla).",
            "Busque algo en YouTube o en tu navegador preferido (puedes usar un término o ingresar una URL).",
            "Reproduzca música en YouTube Music.",
            "Te comparta un dato curioso.",
            "Te hable sobre el programa y sus creadores.",
        ]
        if usuario.es_admin():
            items.append("Funciones admin.")
        else:
            items.append("Acceder al modo admin (requerirá credenciales de un administrador).")

        items.append("Modificar tus datos de usuario.")
        items.append("Cerrar sesión para iniciar con otro usuario.")
        items.append("Salir del programa.")

        lista = "".join(f"<li>{it}</li>" for it in items)
        return (
            "<h3>¡Hola! Soy PROMPTY 3.0, tu asistente virtual de escritorio.</h3>"
            "<p>Estoy listo para ayudarte con tareas básicas usando tu voz o el teclado.</p>"
            "<p>Puedes pedirme que:</p>"
            f"<ol>{lista}</ol>"
            "<p>Si PROMTY no reconoce un comando, verás un mensaje recordándote que puedes abrir esta ayuda.</p>"
        )

class GestionUsuariosWindow(QWidget):
    """Permite crear y modificar usuarios."""

    def __init__(self, gestor_roles):
        super().__init__()
        self.gestor_roles = gestor_roles
        self.setWindowTitle("Gestión de usuarios")
        self.setGeometry(220, 220, 400, 300)
        self.setStyleSheet("background-color: white;")

        layout = QVBoxLayout()
        self.lista = QListWidget()
        layout.addWidget(self.lista)

        botones = QHBoxLayout()
        btn_crear = QPushButton("Crear")
        btn_crear.clicked.connect(self.crear)
        btn_modificar = QPushButton("Modificar")
        btn_modificar.clicked.connect(self.modificar)
        btn_reset = QPushButton("Restablecer contraseña")
        btn_reset.clicked.connect(self.restablecer)
        botones.addWidget(btn_crear)
        botones.addWidget(btn_modificar)
        botones.addWidget(btn_reset)
        layout.addLayout(botones)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)

        self.setLayout(layout)
        self.cargar_usuarios()

    def cargar_usuarios(self):
        self.lista.clear()
        for u in self.gestor_roles.listar_usuarios():
            self.lista.addItem(f"{u.cif} - {u.nombre} ({u.rol})")

    def crear(self):
        nombre, ok = QInputDialog.getText(self, "Crear usuario", "Nombre:")
        if not (ok and nombre.strip()):
            return
        rol, ok = QInputDialog.getItem(
            self,
            "Crear usuario",
            "Rol:",
            ["usuario", "colaborador", "admin"],
            0,
            False,
        )
        if not ok:
            return
        cif, clave = self.gestor_roles.registrar_usuario(nombre.strip(), rol)
        QMessageBox.information(
            self,
            "Usuario",
            f"Usuario creado. CIF: {cif}\nContraseña: {clave}",
        )
        self.cargar_usuarios()

    def modificar(self):
        fila = self.lista.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Usuarios", "Selecciona un usuario primero")
            return
        usuario = self.gestor_roles.listar_usuarios()[fila]
        nuevo_nombre, ok = QInputDialog.getText(
            self, "Modificar", "Nuevo nombre:", text=usuario.nombre
        )
        if not ok:
            return
        nueva_clave, ok = QInputDialog.getText(
            self,
            "Modificar",
            "Nueva contraseña (dejar vacío para no cambiar):",
        )
        if not ok:
            return
        nuevo_rol, ok = QInputDialog.getItem(
            self,
            "Modificar",
            "Rol:",
            ["usuario", "colaborador", "admin"],
            ["usuario", "colaborador", "admin"].index(usuario.rol),
            False,
        )
        if not ok:
            return
        self.gestor_roles.actualizar_usuario(
            usuario.cif,
            nombre=nuevo_nombre.strip() or None,
            contrasena=nueva_clave.strip() or None,
            rol=nuevo_rol,
        )
        QMessageBox.information(self, "Usuarios", "Usuario actualizado")
        self.cargar_usuarios()

    def restablecer(self):
        fila = self.lista.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Usuarios", "Selecciona un usuario primero")
            return
        usuario = self.gestor_roles.listar_usuarios()[fila]
        nueva = self.gestor_roles.restablecer_contrasena(usuario.cif)
        QMessageBox.information(
            self,
            "Contraseña temporal",
            f"Nueva contraseña para {usuario.cif}: {nueva}",
        )


class AdminWindow(QWidget):
    """Opciones básicas de administración."""

    def __init__(self, parent, servicio_voz, gestor_roles, usuario):
        super().__init__()
        self.parent = parent
        self.servicio_voz = servicio_voz
        self.gestor_roles = gestor_roles
        self.usuario = usuario
        self.setWindowTitle("Funciones admin")
        self.setGeometry(200, 200, 260, 200)
        self.setStyleSheet("background-color: white;")
        self.ventana_usuarios = None
        layout = QVBoxLayout()

        btn_voz = QPushButton("Configurar voz")
        btn_voz.clicked.connect(parent.ver_configuracion)
        layout.addWidget(btn_voz)

        btn_users = QPushButton("Gestionar usuarios")
        btn_users.clicked.connect(self.abrir_gestion_usuarios)
        layout.addWidget(btn_users)

        btn_curiosos = QPushButton("Gestionar datos curiosos")
        btn_curiosos.clicked.connect(self.abrir_datos_curiosos)
        layout.addWidget(btn_curiosos)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)

        self.setLayout(layout)

    def abrir_datos_curiosos(self):
        if not hasattr(self, "ventana_datos"):
            self.ventana_datos = DatosCuriososWindow(self.usuario)
        self.ventana_datos.show()

    def abrir_gestion_usuarios(self):
        if self.ventana_usuarios is None:
            self.ventana_usuarios = GestionUsuariosWindow(self.gestor_roles)
        self.ventana_usuarios.show()

    def no_implementado(self):
        QMessageBox.information(self, "Admin", "Función no implementada en la interfaz")


class DatosCuriososWindow(QWidget):
    """Permite gestionar el archivo de datos curiosos."""

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Datos curiosos")
        self.setGeometry(220, 220, 400, 300)

        layout = QVBoxLayout()
        self.lista = QListWidget()
        layout.addWidget(self.lista)

        botones = QHBoxLayout()
        btn_agregar = QPushButton("Agregar")
        btn_agregar.clicked.connect(self.agregar)
        btn_modificar = QPushButton("Modificar")
        btn_modificar.clicked.connect(self.modificar)
        btn_eliminar = QPushButton("Eliminar")
        btn_eliminar.clicked.connect(self.eliminar)
        botones.addWidget(btn_agregar)
        botones.addWidget(btn_modificar)
        botones.addWidget(btn_eliminar)
        layout.addLayout(botones)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)

        self.setLayout(layout)
        self.cargar_datos()

    def cargar_datos(self):
        from services import datos_curiosos

        self.lista.clear()
        for dato in datos_curiosos.obtener_lista_datos():
            self.lista.addItem(dato)

    def agregar(self):
        from services import datos_curiosos

        texto, ok = QInputDialog.getText(self, "Agregar", "Nuevo dato curioso:")
        if ok and texto.strip():
            msg = datos_curiosos.agregar_dato(self.usuario, texto)
            QMessageBox.information(self, "Datos curiosos", quitar_colores(msg))
            self.cargar_datos()

    def modificar(self):
        from services import datos_curiosos

        fila = self.lista.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Datos curiosos", "Selecciona un dato primero")
            return
        actual = self.lista.item(fila).text()
        texto, ok = QInputDialog.getText(self, "Modificar", "Nuevo texto:", text=actual)
        if ok and texto.strip():
            msg = datos_curiosos.modificar_dato(self.usuario, fila, texto)
            QMessageBox.information(self, "Datos curiosos", quitar_colores(msg))
            self.cargar_datos()

    def eliminar(self):
        from services import datos_curiosos

        fila = self.lista.currentRow()
        if fila < 0:
            QMessageBox.warning(self, "Datos curiosos", "Selecciona un dato primero")
            return
        ok = QMessageBox.question(self, "Eliminar", "¿Eliminar el dato seleccionado?",
                                  QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        if ok == QMessageBox.StandardButton.Yes:
            msg = datos_curiosos.eliminar_dato(self.usuario, fila)
            QMessageBox.information(self, "Datos curiosos", quitar_colores(msg))
            self.cargar_datos()
class TreeWindow(QWidget):
    """Muestra un árbol simple de la estructura del proyecto."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Árbol del proyecto")
        self.setGeometry(200, 200, 400, 400)

        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        btn_cerrar = QPushButton("Cerrar")
        btn_cerrar.clicked.connect(self.close)
        layout.addWidget(btn_cerrar)

        self.setLayout(layout)
        self.cargar_arbol()

    def cargar_arbol(self):
        root_path = Path(__file__).resolve().parents[2] / "PROMPTY_3.0"
        lineas = []
        for ruta, dirs, files in os.walk(root_path):
            nivel = len(Path(ruta).relative_to(root_path).parts)
            indent = "    " * nivel
            lineas.append(f"{indent}{Path(ruta).name}/")
            for f in files:
                lineas.append(f"{indent}    {f}")
        self.text.setPlainText("\n".join(lineas))
        
class PROMPTYWindow(QMainWindow):
    def __init__(self, usuario, logout_callback=None):
        super().__init__()
        self.usuario = usuario
        self.logout_callback = logout_callback
        self.gestor_roles = GestorRoles()
        self.servicio_voz = ServicioVoz(usuario, verificar_admin_callback=self.gestor_roles.autenticar)
        self.gestor_comandos = GestorComandos(usuario)
        self.setWindowTitle("PROMPTY - Asistente de Voz")
        self.setGeometry(100, 100, 400, 600)
        self.font_family = "Roboto"
        self.base_font_size = 16
        self.saludo = "Hola, soy PROMPTY! \ntu asistente de voz"
        self.mensaje_timer = QTimer(self)
        self.ventana_configuracion = None
        self.ventana_usuario = None
        self.ventana_editor_usuario = None
        self.ventana_ayuda = None
        self.ventana_admin = None
        self.dark_mode_enabled = False
        self.ventana_tree = None
        self.setup_ui()

    def paintEvent(self, event):
        painter = QPainter(self)
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, Qt.GlobalColor.blue)
        gradient.setColorAt(1, Qt.GlobalColor.white)
        brush = QBrush(gradient)
        painter.fillRect(self.rect(), brush)

    def setup_ui(self):
        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout()
        central_widget.setLayout(main_layout)

        top_layout = QHBoxLayout()
        top_layout.addStretch()

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

        self.button_tree = self.create_icon_button("Árbol del programa", "tree_icon.png")
        self.button_tree.clicked.connect(self.ver_arbol_programa)
        top_layout.addWidget(self.button_tree)

        main_layout.addLayout(top_layout)

        self.label = QLabel(self.saludo, self)
        self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label.setFont(QFont(self.font_family, self.base_font_size))
        main_layout.addWidget(self.label)

        self.command_input = QLineEdit()
        self.command_input.setPlaceholderText("Escribe un comando y presiona Enter")
        self.command_input.returnPressed.connect(self.process_command)
        main_layout.addWidget(self.command_input)

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
        ruta_icono_mic = os.path.join(RESOURCES_DIR, "microphone_icon.png")
        if os.path.exists(ruta_icono_mic):
            self.button_microfono.setIcon(QIcon(ruta_icono_mic))
            self.button_microfono.setIconSize(QSize(50, 50))
        else:
            print(f"\u26a0 Icono no encontrado en: {ruta_icono_mic}")
        self.button_microfono.clicked.connect(self.activate_voice)
        main_layout.addWidget(self.button_microfono, alignment=Qt.AlignmentFlag.AlignCenter)

        self.text_output = QTextEdit()
        self.text_output.setReadOnly(True)
        self.text_output.setPlaceholderText("Aquí se mostrará lo que diga el asistente de voz...")
        self.text_output.setFixedHeight(100)
        main_layout.addWidget(self.text_output)

        self.button_salir = QPushButton("Salir")
        self.button_salir.setFixedSize(150, 40)
        self.button_salir.setStyleSheet("background-color: #ff6347; color: white; border-radius: 10px;")
        self.button_salir.clicked.connect(self.close)
        main_layout.addWidget(self.button_salir, alignment=Qt.AlignmentFlag.AlignCenter)

        self.apply_scaling()

    def create_icon_button(self, tooltip, icon_file):
        button = QPushButton("")
        button.setToolTip(tooltip)
        button.setFixedSize(40, 40)
        button.setStyleSheet("border: none; background-color: transparent;")
        ruta_icono = os.path.join(RESOURCES_DIR, icon_file)
        if os.path.exists(ruta_icono):
            button.setIcon(QIcon(ruta_icono))
            button.setIconSize(QSize(30, 30))
            button.icon_file = ruta_icono
        else:
            print(f"\u26a0 Icono no encontrado: {ruta_icono}")
        return button

    def ver_usuario(self):
        if self.ventana_usuario is None:
            self.ventana_usuario = UsuarioWindow(
                self.usuario,
                self.gestor_roles,
                editar_callback=self.mostrar_editor_usuario,
                logout_callback=self.cerrar_sesion,
            )
        self.ventana_usuario.show()

    def mostrar_editor_usuario(self):
        if self.ventana_editor_usuario is None:
            self.ventana_editor_usuario = EditarUsuarioWindow(
                self.usuario, self.gestor_roles
            )
        self.ventana_editor_usuario.show()

    def ver_ayuda(self):
        if self.ventana_ayuda is None:
            self.ventana_ayuda = AyudaWindow(self.usuario)
        self.ventana_ayuda.show()

    def ver_configuracion(self):
        if self.ventana_configuracion is None:
            self.ventana_configuracion = ConfiguracionWindow(
                self.servicio_voz,
                fuente=self.font_family,
                tamano=self.base_font_size,
                aplicar_fuente=self.actualizar_fuente,
            )
        self.ventana_configuracion.show()

    def ver_admin(self):
        usuario_admin = self.usuario
        if not self.usuario.es_admin():
            cif, ok = QInputDialog.getText(self, "Modo admin", "CIF del administrador:")
            if not ok:
                return
            clave, ok2 = QInputDialog.getText(
                self, "Modo admin", "Contraseña:", QLineEdit.EchoMode.Password
            )
            if not ok2:
                return
            usuario_admin = self.gestor_roles.autenticar(cif.strip(), clave.strip())
            if not usuario_admin or not usuario_admin.es_admin():
                QMessageBox.warning(self, "Error", "Credenciales incorrectas")
                return
        if self.ventana_admin is None:
            self.ventana_admin = AdminWindow(self, self.servicio_voz, self.gestor_roles, usuario_admin)
        self.ventana_admin.show()

    def ver_arbol_programa(self):
        if self.ventana_tree is None:
            self.ventana_tree = TreeWindow()
        self.ventana_tree.show()

    def activate_voice(self):
        mensaje_original = self.label.text()
        self.label.setText("\ud83c\udf99\ufe0f Escuchando...")
        
        def notify_gui(msg):
            self.text_output.append(msg)
            QApplication.processEvents()

        texto = self.servicio_voz.escuchar(notify=notify_gui)

        self.label.setText(mensaje_original)
        if not texto:
            self.text_output.append("\u274c No se entendió el comando")
            self.servicio_voz.hablar("No se entendió el comando")
            return
        self.text_output.append(f"\ud83d\udde3\ufe0f Entendí: {texto}")
        self.ejecutar_comando_desde_texto(texto)

    def process_command(self):
        texto = self.command_input.text().strip()
        if texto:
            self.ejecutar_comando_desde_texto(texto)
            self.command_input.clear()

    def ejecutar_comando_desde_texto(self, texto):
        comando, argumentos = interpretar(texto)
        self.text_output.clear()

        if comando == "editar_usuario":
            self.mostrar_editor_usuario()
            respuesta = "Abriendo editor de usuario..."
        elif comando == "modo_admin":
            self.ver_admin()
            respuesta = "Abriendo funciones de administrador..."
        elif comando == "cerrar_sesion":
            respuesta = "\ud83d\udd12 Sesión cerrada."
            self.mostrar_respuesta(respuesta)
            self.cerrar_sesion()
            return
        elif comando == "salir":
            respuesta = "\ud83d\udc4b Hasta luego. Fue un placer ayudarte."
            self.mostrar_respuesta(respuesta)
            self.close()
            return
        else:
            interactivos = {
                "abrir_carpeta",
                "abrir_con_opcion",
                "buscar_en_navegador",
                "buscar_en_youtube",
                "buscar_general",
                "info_programa",
                "reproducir_musica",
            }
            if comando in interactivos:
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos, self.preguntar)
            else:
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos)

        self.mostrar_respuesta(respuesta)

    def mostrar_respuesta(self, respuesta: str):
        """Muestra y lee en voz alta la respuesta sin códigos de color."""
        texto_limpio = quitar_colores(respuesta)
        self.text_output.append(texto_limpio)
        self.servicio_voz.hablar(texto_limpio)

    def actualizar_fuente(self, familia, tamano):
        self.font_family = familia
        self.base_font_size = tamano
        self.apply_scaling()

    def apply_scaling(self):
        """Ajusta tamaños de fuente y botones de forma proporcional."""
        w_factor = self.width() / 400
        h_factor = self.height() / 600
        factor = max(0.8, min(1.5, min(w_factor, h_factor)))
        fuente = QFont(self.font_family, int(self.base_font_size * factor))
        self.label.setFont(fuente)
        self.command_input.setFont(fuente)
        self.text_output.setFont(fuente)
        for btn in [
            self.button_usuario,
            self.button_ayuda,
            self.button_modo_oscuro,
            self.button_config,
            self.button_tree,
        ]:
            btn.setFixedSize(int(40 * factor), int(40 * factor))
            btn.setIconSize(QSize(int(30 * factor), int(30 * factor)))
        self.button_microfono.setFixedSize(int(100 * factor), int(100 * factor))
        self.button_microfono.setIconSize(QSize(int(50 * factor), int(50 * factor)))
        self.button_salir.setFixedSize(int(150 * factor), int(40 * factor))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_scaling()

    def preguntar(self, mensaje):
        texto, ok = QInputDialog.getText(self, "PROMPTY", mensaje)
        return texto if ok else ""

    def activar_modo_oscuro(self):
        if not self.dark_mode_enabled:
            self.setStyleSheet("background-color: #222; color: white;")
            self.label.setText("Modo oscuro activado.")
            self.dark_mode_enabled = True
            self.button_usuario.setIcon(get_colored_icon(self.button_usuario.icon_file, QColor("white")))
            self.button_ayuda.setIcon(get_colored_icon(self.button_ayuda.icon_file, QColor("white")))
            self.button_modo_oscuro.setIcon(get_colored_icon(self.button_modo_oscuro.icon_file, QColor("white")))
            self.button_config.setIcon(get_colored_icon(self.button_config.icon_file, QColor("white")))
            self.button_tree.setIcon(get_colored_icon(self.button_tree.icon_file, QColor("white")))
        else:
            self.setStyleSheet("")
            self.label.setText("Modo claro activado.")
            self.dark_mode_enabled = False
            self.button_usuario.setIcon(QIcon(self.button_usuario.icon_file))
            self.button_ayuda.setIcon(QIcon(self.button_ayuda.icon_file))
            self.button_modo_oscuro.setIcon(QIcon(self.button_modo_oscuro.icon_file))
            self.button_config.setIcon(QIcon(self.button_config.icon_file))
            self.button_tree.setIcon(QIcon(self.button_tree.icon_file))

        self.mensaje_timer.stop()
        self.mensaje_timer.singleShot(5000, lambda: self.label.setText(self.saludo))

    def cerrar_sesion(self):
        self.close()
        if self.logout_callback:
            self.logout_callback()

class LoginWindow(QWidget):
    def __init__(self, gestor_roles=None):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.gestor_roles = gestor_roles or GestorRoles()
        self.font_family = "Roboto"
        self.base_font_size = 14
        self.setup_ui()
        self.apply_scaling()

    def show(self):
        """Muestra la ventana asegurando que quede al frente."""
        super().show()
        self.raise_()
        self.activateWindow()

    def showEvent(self, event):
        """Garantiza que la ventana reciba el foco al mostrarse."""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def apply_scaling(self):
        """Escala la interfaz tomando en cuenta el tamaño de la ventana."""
        w_factor = self.width() / 300
        h_factor = self.height() / 200
        factor = max(0.8, min(1.5, min(w_factor, h_factor)))
        fuente = QFont(self.font_family, int(self.base_font_size * factor))
        self.title_label.setFont(fuente)
        self.cif_input.setFont(fuente)
        self.pass_input.setFont(fuente)
        self.login_button.setFont(fuente)
        self.forgot_button.setFont(fuente)
        for btn in [self.login_button, self.forgot_button]:
            btn.setFixedHeight(int(30 * factor))

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.apply_scaling()

    def setup_ui(self):
        layout = QVBoxLayout()
        self.title_label = QLabel("\ud83d\udd10 Iniciar sesión en PROMPTY")
        layout.addWidget(self.title_label)

        self.cif_input = QLineEdit()
        self.cif_input.setPlaceholderText("CIF")
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.clicked.connect(self.verificar)
        self.forgot_button = QPushButton("Olvidé mi contraseña")
        self.forgot_button.clicked.connect(self.restablecer)
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
            self.main = PROMPTYWindow(usuario, logout_callback=self.show)
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

