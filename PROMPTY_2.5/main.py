"""Punto de entrada de PROMPTY 2.5."""

import sys

from views.login import VistaLogin
from views.gui import LoginWindow
from PyQt6.QtWidgets import QApplication


def main():
    """Pregunta si se usará la interfaz de terminal o la gráfica."""
    modo = input("¿Usar interfaz gráfica? [s/N]: ").strip().lower()
    if modo in {"s", "y", "si", "sí"}:
        app = QApplication(sys.argv)
        login = LoginWindow()
        login.show()
        app.exec()
    else:
        VistaLogin().iniciar()


if __name__ == "__main__":
    main()
