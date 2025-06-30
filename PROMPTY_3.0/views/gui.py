"""Interfaz gráfica principal de PROMPTY construida con PyQt."""

import os
import sys
from pathlib import Path

from data import config
from PyQt6.QtCore import QSize, Qt, QTimer
from PyQt6.QtGui import (
    QBrush,
    QColor,
    QFont,
    QFontDatabase,
    QIcon,
    QLinearGradient,
    QPainter,
    QPixmap,
)
from PyQt6.QtWidgets import (
    QApplication,
    QComboBox,
    QFormLayout,
    QHBoxLayout,
    QInputDialog,
    QLabel,
    QLineEdit,
    QListWidget,
    QMainWindow,
    QMessageBox,
    QPushButton,
    QSlider,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
from services.asistente_voz import ServicioVoz
from services.gestor_comandos import GestorComandos
from services.gestor_roles import GestorRoles
from services.autenticacion import ServicioAutenticacion
from services.interpretador import interpretar
from utils import ScalingMixin
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


class ConfiguracionWindow(ScalingMixin, QWidget):
    """Permite ajustar la voz y la fuente de PROMPTY."""

    def __init__(
        self,
        servicio_voz,
        fuente=config.FUENTE_POR_DEFECTO,
        tamano=config.TAMANO_LETRA_POR_DEFECTO,
        aplicar_fuente=None,
    ):
        super().__init__()
        self.servicio_voz = servicio_voz
        self.aplicar_fuente = aplicar_fuente
        self.setWindowTitle("Configuración")
        self.setGeometry(150, 150, 400, 260)
        self.base_width = 400
        self.base_height = 260
        self.font_family = fuente
        self.base_font_size = tamano

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
        boton_guardar.setProperty("base_height", 30)
        boton_guardar.setProperty(
            "base_width", boton_guardar.sizeHint().width()
        )
        layout.addWidget(boton_guardar, alignment=Qt.AlignmentFlag.AlignCenter)

        boton_restaurar = QPushButton("Restablecer")
        boton_restaurar.clicked.connect(self.restablecer)
        boton_restaurar.setProperty("base_height", 30)
        boton_restaurar.setProperty(
            "base_width", boton_restaurar.sizeHint().width()
        )
        layout.addWidget(
            boton_restaurar, alignment=Qt.AlignmentFlag.AlignCenter
        )

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        boton_cerrar.setProperty("base_height", 30)
        boton_cerrar.setProperty("base_width", boton_cerrar.sizeHint().width())
        layout.addWidget(boton_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()

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

    def restablecer(self):
        """Vuelve a cargar la configuración predeterminada."""
        idx = self.voz_combo.findData(config.VOZ_POR_DEFECTO)
        if idx >= 0:
            self.voz_combo.setCurrentIndex(idx)
        self.volumen_slider.setValue(int(config.VOLUMEN_POR_DEFECTO * 100))
        self.velocidad_slider.setValue(config.VELOCIDAD_POR_DEFECTO)
        self.font_combo.setCurrentText(config.FUENTE_POR_DEFECTO)
        self.size_slider.setValue(config.TAMANO_LETRA_POR_DEFECTO)

        self.servicio_voz.cambiar_voz(config.VOZ_POR_DEFECTO)
        self.servicio_voz.cambiar_volumen(config.VOLUMEN_POR_DEFECTO)
        self.servicio_voz.cambiar_velocidad(config.VELOCIDAD_POR_DEFECTO)

        if self.aplicar_fuente:
            self.aplicar_fuente(
                config.FUENTE_POR_DEFECTO,
                config.TAMANO_LETRA_POR_DEFECTO,
            )
        self.setFont(
            QFont(config.FUENTE_POR_DEFECTO, config.TAMANO_LETRA_POR_DEFECTO)
        )
        QMessageBox.information(
            self, "Configuración", "Valores predeterminados restablecidos"
        )

class EditarUsuarioWindow(ScalingMixin, QWidget):
    """Permite modificar los datos del usuario actual."""

    def __init__(self, usuario, gestor_roles):
        super().__init__()
        self.usuario = usuario
        self.gestor_roles = gestor_roles
        self.setWindowTitle("Modificar datos")
        self.setGeometry(220, 220, 300, 220)
        self.base_width = 300
        self.base_height = 220

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
        boton_guardar.setProperty("base_height", 30)
        boton_guardar.setProperty(
            "base_width", boton_guardar.sizeHint().width()
        )
        layout.addWidget(boton_guardar, alignment=Qt.AlignmentFlag.AlignCenter)

        boton_cerrar = QPushButton("Cerrar")
        boton_cerrar.clicked.connect(self.close)
        boton_cerrar.setProperty("base_height", 30)
        boton_cerrar.setProperty("base_width", boton_cerrar.sizeHint().width())
        layout.addWidget(boton_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()

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


class UsuarioWindow(ScalingMixin, QWidget):
    """Muestra la información del usuario y acciones disponibles."""

    def __init__(self, usuario, gestor_roles, editar_callback=None, logout_callback=None):
        super().__init__()
        self.usuario = usuario
        self.gestor_roles = gestor_roles
        self.editar_callback = editar_callback
        self.logout_callback = logout_callback
        self.setWindowTitle("Mi cuenta")
        self.setGeometry(200, 200, 300, 200)
        self.base_width = 300
        self.base_height = 200

        layout = QVBoxLayout()
        layout.addWidget(
            QLabel(f"Usuario: {self.usuario.nombre} ({self.usuario.cif}) - {self.usuario.rol}")
        )

        if self.editar_callback:
            self.boton_editar = QPushButton("Modificar mis datos")
            self.boton_editar.clicked.connect(self.editar_callback)
            self.boton_editar.setProperty("base_height", 30)
            self.boton_editar.setProperty(
                "base_width", self.boton_editar.sizeHint().width()
            )
            layout.addWidget(
                self.boton_editar, alignment=Qt.AlignmentFlag.AlignCenter
            )

        if self.logout_callback:
            self.boton_logout = QPushButton("Cerrar sesión")
            self.boton_logout.clicked.connect(self.logout_callback)
            self.boton_logout.setProperty("base_height", 30)
            self.boton_logout.setProperty(
                "base_width", self.boton_logout.sizeHint().width()
            )
            layout.addWidget(
                self.boton_logout, alignment=Qt.AlignmentFlag.AlignCenter
            )

        self.boton_cerrar = QPushButton("Cerrar")
        self.boton_cerrar.clicked.connect(self.close)
        self.boton_cerrar.setProperty("base_height", 30)
        self.boton_cerrar.setProperty(
            "base_width", self.boton_cerrar.sizeHint().width()
        )
        layout.addWidget(
            self.boton_cerrar, alignment=Qt.AlignmentFlag.AlignCenter
        )

        self.setLayout(layout)
        self.apply_scaling()

class AyudaWindow(ScalingMixin, QWidget):
    """Ventana que muestra las opciones y comandos disponibles."""

    def __init__(self, usuario):
        super().__init__()
        self.setWindowTitle("Ayuda")
        self.setGeometry(
            config.AYUDA_POS_X,
            config.AYUDA_POS_Y,
            config.AYUDA_ANCHO,
            config.AYUDA_ALTO,
        )
        self.base_width = config.AYUDA_ANCHO
        self.base_height = config.AYUDA_ALTO
        layout = QVBoxLayout()

        ayuda = QTextEdit()
        ayuda.setReadOnly(True)
        ayuda.setHtml(self._generar_texto(usuario))
        layout.addWidget(ayuda)

        self.boton_cerrar = QPushButton("Cerrar")
        self.boton_cerrar.clicked.connect(self.close)
        self.boton_cerrar.setProperty("base_height", 30)
        self.boton_cerrar.setProperty(
            "base_width", self.boton_cerrar.sizeHint().width()
        )
        layout.addWidget(self.boton_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()

    def _generar_texto(self, usuario):
        items = list(config.AYUDA_ITEMS_BASE)
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

class GestionUsuariosWindow(ScalingMixin, QWidget):
    """Permite crear y modificar usuarios."""

    def __init__(self, gestor_roles):
        super().__init__()
        self.gestor_roles = gestor_roles
        self.setWindowTitle("Gestión de usuarios")
        self.setGeometry(220, 220, 400, 300)
        self.setStyleSheet("background-color: white;")
        self.base_width = 400
        self.base_height = 300

        layout = QVBoxLayout()
        self.lista = QListWidget()
        layout.addWidget(self.lista)

        botones = QHBoxLayout()
        self.btn_crear = QPushButton("Crear")
        self.btn_crear.clicked.connect(self.crear)
        self.btn_crear.setProperty("base_height", 30)
        self.btn_crear.setProperty("base_width", self.btn_crear.sizeHint().width())
        self.btn_modificar = QPushButton("Modificar")
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_modificar.setProperty("base_height", 30)
        self.btn_modificar.setProperty("base_width", self.btn_modificar.sizeHint().width())
        self.btn_reset = QPushButton("Restablecer contraseña")
        self.btn_reset.clicked.connect(self.restablecer)
        self.btn_reset.setProperty("base_height", 30)
        self.btn_reset.setProperty("base_width", self.btn_reset.sizeHint().width())
        botones.addWidget(self.btn_crear)
        botones.addWidget(self.btn_modificar)
        botones.addWidget(self.btn_reset)
        botones.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(botones)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_cerrar.setProperty("base_height", 30)
        self.btn_cerrar.setProperty("base_width", self.btn_cerrar.sizeHint().width())
        layout.addWidget(self.btn_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()
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
            f"Usuario creado.\nCIF: {cif}\nContraseña: {clave}\n"
            "Anota estos datos en un lugar seguro.",
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


class AdminWindow(ScalingMixin, QWidget):
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
        self.base_width = 260
        self.base_height = 200
        layout = QVBoxLayout()

        self.btn_voz = QPushButton("Configurar voz")
        self.btn_voz.clicked.connect(parent.ver_configuracion)
        self.btn_voz.setProperty("base_height", 30)
        self.btn_voz.setProperty("base_width", self.btn_voz.sizeHint().width())
        layout.addWidget(self.btn_voz, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_users = QPushButton("Gestionar usuarios")
        self.btn_users.clicked.connect(self.abrir_gestion_usuarios)
        self.btn_users.setProperty("base_height", 30)
        self.btn_users.setProperty("base_width", self.btn_users.sizeHint().width())
        layout.addWidget(self.btn_users, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_curiosos = QPushButton("Gestionar datos curiosos")
        self.btn_curiosos.clicked.connect(self.abrir_datos_curiosos)
        self.btn_curiosos.setProperty("base_height", 30)
        self.btn_curiosos.setProperty("base_width", self.btn_curiosos.sizeHint().width())
        layout.addWidget(self.btn_curiosos, alignment=Qt.AlignmentFlag.AlignCenter)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_cerrar.setProperty("base_height", 30)
        self.btn_cerrar.setProperty("base_width", self.btn_cerrar.sizeHint().width())
        layout.addWidget(self.btn_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()

    def abrir_datos_curiosos(self):
        if not hasattr(self, "ventana_datos"):
            self.ventana_datos = DatosCuriososWindow(self.usuario)
        self.parent._sincronizar_fuente(self.ventana_datos)
        self.ventana_datos.show()

    def abrir_gestion_usuarios(self):
        if self.ventana_usuarios is None:
            self.ventana_usuarios = GestionUsuariosWindow(self.gestor_roles)
        self.parent._sincronizar_fuente(self.ventana_usuarios)
        self.ventana_usuarios.show()

    def no_implementado(self):
        QMessageBox.information(self, "Admin", "Función no implementada en la interfaz")


class DatosCuriososWindow(ScalingMixin, QWidget):
    """Permite gestionar el archivo de datos curiosos."""

    def __init__(self, usuario):
        super().__init__()
        self.usuario = usuario
        self.setWindowTitle("Datos curiosos")
        self.setGeometry(220, 220, 400, 300)
        self.base_width = 400
        self.base_height = 300

        layout = QVBoxLayout()
        self.lista = QListWidget()
        layout.addWidget(self.lista)

        botones = QHBoxLayout()
        self.btn_agregar = QPushButton("Agregar")
        self.btn_agregar.clicked.connect(self.agregar)
        self.btn_agregar.setProperty("base_height", 30)
        self.btn_agregar.setProperty("base_width", self.btn_agregar.sizeHint().width())
        self.btn_modificar = QPushButton("Modificar")
        self.btn_modificar.clicked.connect(self.modificar)
        self.btn_modificar.setProperty("base_height", 30)
        self.btn_modificar.setProperty("base_width", self.btn_modificar.sizeHint().width())
        self.btn_eliminar = QPushButton("Eliminar")
        self.btn_eliminar.clicked.connect(self.eliminar)
        self.btn_eliminar.setProperty("base_height", 30)
        self.btn_eliminar.setProperty("base_width", self.btn_eliminar.sizeHint().width())
        botones.addWidget(self.btn_agregar)
        botones.addWidget(self.btn_modificar)
        botones.addWidget(self.btn_eliminar)
        botones.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addLayout(botones)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_cerrar.setProperty("base_height", 30)
        self.btn_cerrar.setProperty("base_width", self.btn_cerrar.sizeHint().width())
        layout.addWidget(self.btn_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()
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
class TreeWindow(ScalingMixin, QWidget):
    """Muestra un árbol simple de la estructura del proyecto."""

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Árbol del proyecto")
        self.setGeometry(200, 200, 400, 400)
        self.base_width = 400
        self.base_height = 400

        layout = QVBoxLayout()
        self.text = QTextEdit()
        self.text.setReadOnly(True)
        layout.addWidget(self.text)

        self.btn_cerrar = QPushButton("Cerrar")
        self.btn_cerrar.clicked.connect(self.close)
        self.btn_cerrar.setProperty("base_height", 30)
        self.btn_cerrar.setProperty("base_width", self.btn_cerrar.sizeHint().width())
        layout.addWidget(self.btn_cerrar, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()
        self.cargar_arbol()

    def cargar_arbol(self):
        root_path = Path(__file__).resolve().parents[1]
        from utils.helpers import generar_arbol

        lineas = generar_arbol(root_path)
        self.text.setPlainText("\n".join(lineas))
        
class PROMTYWindow(ScalingMixin, QMainWindow):
    def __init__(self, usuario, logout_callback=None):
        super().__init__()
        self.usuario = usuario
        self.logout_callback = logout_callback
        self.gestor_roles = GestorRoles()
        self.auth_service = ServicioAutenticacion(self.gestor_roles)
        self.servicio_voz = ServicioVoz(usuario, verificar_admin_callback=self.gestor_roles.autenticar)
        self.gestor_comandos = GestorComandos(usuario)
        self.setWindowTitle("PROMTY - Asistente de Voz")
        self.setGeometry(100, 100, 400, 600)
        self.base_width = 400
        self.base_height = 600
        self.font_family = config.FUENTE_POR_DEFECTO
        self.base_font_size = config.TAMANO_LETRA_POR_DEFECTO
        self.saludo = "Hola, soy PROMTY! \ntu asistente de voz"
        self.mensaje_timer = QTimer(self)
        self.ventana_configuracion = None
        self.ventana_usuario = None
        self.ventana_editor_usuario = None
        self.ventana_ayuda = None
        self.ventana_admin = None
        self.dark_mode_enabled = False
        self.ventana_tree = None
        self.setup_ui()

    def show(self):
        """Muestra la ventana principal en pantalla completa."""
        super().showFullScreen()

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
        self.button_microfono.setProperty("base_size", 100)
        self.button_microfono.setProperty("base_icon", 50)
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
        self.text_output.setProperty("base_height", 100)
        main_layout.addWidget(self.text_output)

        self.button_salir = QPushButton("Salir")
        self.button_salir.setStyleSheet(
            "background-color: #ff6347; color: white; border-radius: 10px;"
        )
        # Hacemos el botón de salida más grande por defecto
        self.button_salir.setProperty("base_height", 60)
        # Aumentamos también el ancho base para que sea más visible
        base_width_salir = max(150, self.button_salir.sizeHint().width())
        self.button_salir.setProperty("base_width", base_width_salir)
        self.button_salir.clicked.connect(self.close)
        main_layout.addWidget(self.button_salir, alignment=Qt.AlignmentFlag.AlignCenter)

        self.apply_scaling()

    def create_icon_button(self, tooltip, icon_file):
        button = QPushButton("")
        button.setToolTip(tooltip)
        button.setFixedSize(40, 40)
        button.setProperty("base_size", 40)
        button.setProperty("base_icon", 30)
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
        self._sincronizar_fuente(self.ventana_usuario)
        self.ventana_usuario.show()

    def mostrar_editor_usuario(self):
        if self.ventana_editor_usuario is None:
            self.ventana_editor_usuario = EditarUsuarioWindow(
                self.usuario, self.gestor_roles
            )
        self._sincronizar_fuente(self.ventana_editor_usuario)
        self.ventana_editor_usuario.show()

    def ver_ayuda(self):
        if self.ventana_ayuda is None:
            self.ventana_ayuda = AyudaWindow(self.usuario)
        self._sincronizar_fuente(self.ventana_ayuda)
        self.ventana_ayuda.show()

    def ver_configuracion(self):
        if self.ventana_configuracion is None:
            self.ventana_configuracion = ConfiguracionWindow(
                self.servicio_voz,
                fuente=self.font_family,
                tamano=self.base_font_size,
                aplicar_fuente=self.actualizar_fuente,
            )
        self._sincronizar_fuente(self.ventana_configuracion)
        self.ventana_configuracion.show()

    def ver_admin(self) -> bool:
        """Muestra la ventana de administración si las credenciales son válidas.

        Returns
        -------
        bool
            ``True`` si se abrió la ventana de administración, ``False`` en caso
            contrario.
        """

        def pedir():
            cif, ok = QInputDialog.getText(self, "Modo admin", "CIF del administrador:")
            if not ok:
                return None, None
            clave, ok2 = QInputDialog.getText(
                self, "Modo admin", "Contraseña:", QLineEdit.EchoMode.Password
            )
            if not ok2:
                return None, None
            return cif.strip(), clave.strip()

        usuario_admin = self.auth_service.autenticar_admin(self.usuario, pedir)
        if not usuario_admin:
            QMessageBox.warning(self, "Error", "Acceso denegado")
            return False

        if self.ventana_admin is None:
            self.ventana_admin = AdminWindow(
                self, self.servicio_voz, self.gestor_roles, usuario_admin
            )

        self._sincronizar_fuente(self.ventana_admin)
        self.ventana_admin.show()
        return True

    def ver_arbol_programa(self):
        if self.ventana_tree is None:
            self.ventana_tree = TreeWindow()
        self._sincronizar_fuente(self.ventana_tree)
        self.ventana_tree.show()

    def activate_voice(self):
        self.servicio_voz.detener()
        mensaje_original = self.label.text()
        self.label.setText("\ud83c\udf99\ufe0f Escuchando...")

        # Limpiar la salida para mostrar el estado de escucha
        self.text_output.clear()

        def notify_gui(msg):
            self.text_output.append(msg)
            QApplication.processEvents()

        texto = self.servicio_voz.escuchar(notify=notify_gui)

        self.label.setText(mensaje_original)
        if not texto:
            self.text_output.append("\u274c No se entendió el comando")
            self.servicio_voz.hablar("No se entendió el comando")
            return

        # Mostrar lo entendido y dar tiempo a leerlo antes de procesar
        self.text_output.append(f"\ud83d\udde3\ufe0f Entendí: {texto}")
        QApplication.processEvents()
        QTimer.singleShot(1500, lambda: self.ejecutar_comando_desde_texto(texto))

    def process_command(self):
        texto = self.command_input.text().strip()
        if texto:
            self.servicio_voz.detener()
            self.text_output.append("\U0001F5E3\ufe0f Entendí: " + texto)
            self.ejecutar_comando_desde_texto(texto)
            self.command_input.clear()

    def ejecutar_comando_desde_texto(self, texto):
        self.servicio_voz.detener()
        # Obtener la acción y limpiar la salida previa
        comando, argumentos = interpretar(texto)
        self.text_output.clear()

        if comando == "editar_usuario":
            self.mostrar_editor_usuario()
            respuesta = "Abriendo editor de usuario..."
        elif comando == "modo_admin":
            if self.ver_admin():
                respuesta = "Abriendo funciones de administrador..."
            else:
                respuesta = "❌ Acceso denegado."
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
        elif comando == "ver_arbol":
            self.ver_arbol_programa()
            respuesta = "Mostrando estructura del proyecto..."
        else:
            # Llamadas que requieren interacción del usuario
            interactivos = {
                "abrir_carpeta",
                "abrir_con_opcion",
                "buscar_general",
                "buscar_en_youtube",
                "buscar_en_navegador",
                "info_programa",
                "reproducir_musica",
            }
            if comando in interactivos:
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos, self.preguntar)
            else:
                respuesta = self.gestor_comandos.ejecutar_comando(comando, argumentos)

        # Mostrar respuesta final al usuario
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
        self._actualizar_fuente_ventanas()

    def _sincronizar_fuente(self, ventana):
        if ventana is not None:
            ventana.font_family = self.font_family
            ventana.base_font_size = self.base_font_size
            ventana.apply_scaling()

    def _actualizar_fuente_ventanas(self):
        ventanas = [
            self.ventana_configuracion,
            self.ventana_usuario,
            self.ventana_editor_usuario,
            self.ventana_ayuda,
            self.ventana_admin,
            self.ventana_tree,
        ]
        for v in ventanas:
            self._sincronizar_fuente(v)
            if hasattr(v, "ventana_usuarios"):
                self._sincronizar_fuente(getattr(v, "ventana_usuarios"))
            if hasattr(v, "ventana_datos"):
                self._sincronizar_fuente(getattr(v, "ventana_datos"))

    def on_apply_scaling(self, factor: float) -> None:
        fuente = QFont(self.font_family, int(self.base_font_size * factor))
        self.label.setFont(fuente)
        self.command_input.setFont(fuente)
        self.text_output.setFont(fuente)
        self.button_salir.setFont(fuente)

    def preguntar(self, mensaje):
        texto, ok = QInputDialog.getText(self, "PROMTY", mensaje)
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

class LoginWindow(ScalingMixin, QWidget):
    def __init__(self, gestor_roles=None):
        super().__init__()
        self.setWindowTitle("Iniciar sesión")
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.gestor_roles = gestor_roles or GestorRoles()
        self.base_width = 300
        self.base_height = 200
        self.font_family = config.FUENTE_POR_DEFECTO
        self.base_font_size = config.TAMANO_LETRA_POR_DEFECTO
        self.setup_ui()
        self.apply_scaling()

    def show(self):
        """Muestra la ventana en pantalla completa y al frente."""
        super().showFullScreen()
        self.raise_()
        self.activateWindow()

    def showEvent(self, event):
        """Garantiza que la ventana reciba el foco al mostrarse."""
        super().showEvent(event)
        self.raise_()
        self.activateWindow()

    def on_apply_scaling(self, factor: float) -> None:
        fuente = QFont(self.font_family, int(self.base_font_size * factor))
        self.title_label.setFont(fuente)
        self.cif_input.setFont(fuente)
        self.pass_input.setFont(fuente)
        self.login_button.setFont(fuente)
        self.forgot_button.setFont(fuente)
        self.register_button.setFont(fuente)
        self.exit_button.setFont(fuente)

    def setup_ui(self):
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label = QLabel("\ud83d\udd10 Iniciar sesión en PROMPTY")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.title_label)

        self.cif_input = QLineEdit()
        self.cif_input.setPlaceholderText("CIF")
        self.cif_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.pass_input = QLineEdit()
        self.pass_input.setPlaceholderText("Contraseña")
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.cif_input)
        layout.addWidget(self.pass_input)

        self.login_button = QPushButton("Iniciar sesión")
        self.login_button.clicked.connect(self.verificar)
        self.login_button.setProperty("base_height", 30)
        self.login_button.setProperty("base_width", self.login_button.sizeHint().width())
        layout.addWidget(self.login_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.forgot_button = QPushButton("Olvidé mi contraseña")
        self.forgot_button.clicked.connect(self.restablecer)
        self.forgot_button.setProperty("base_height", 30)
        self.forgot_button.setProperty("base_width", self.forgot_button.sizeHint().width())
        layout.addWidget(self.forgot_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.register_button = QPushButton("Registrarse")
        self.register_button.clicked.connect(self.registrar)
        self.register_button.setProperty("base_height", 30)
        self.register_button.setProperty("base_width", self.register_button.sizeHint().width())
        layout.addWidget(self.register_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.exit_button = QPushButton("Salir")
        self.exit_button.clicked.connect(self.close)
        # Botón de salida más grande para facilitar su pulsación
        self.exit_button.setProperty("base_height", 50)
        base_exit_width = max(120, self.exit_button.sizeHint().width())
        self.exit_button.setProperty("base_width", base_exit_width)
        layout.addWidget(self.exit_button, alignment=Qt.AlignmentFlag.AlignCenter)

        self.setLayout(layout)
        self.apply_scaling()

    def registrar(self):
        nombre, ok = QInputDialog.getText(self, "Registro", "Nombre:")
        if not (ok and nombre.strip()):
            return
        clave, ok = QInputDialog.getText(
            self,
            "Registro",
            "Contrase\u00f1a:",
            QLineEdit.EchoMode.Password,
        )
        if not (ok and clave):
            return
        cif, _ = self.gestor_roles.registrar_usuario(
            nombre.strip(), "usuario", contrasena=clave
        )
        QMessageBox.information(
            self,
            "Registro",
            f"Registro exitoso.\nCIF: {cif}\nContrase\u00f1a: {clave}\n"
            "Anota estos datos en un lugar seguro.",
        )

    def verificar(self):
        usuario = self.gestor_roles.autenticar(
            self.cif_input.text().strip(), self.pass_input.text().strip()
        )
        if usuario:
            self.hide()
            self.main = PROMTYWindow(usuario, logout_callback=self.show)
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

