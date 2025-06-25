"""Punto de entrada de PROMPTY 3.0."""

import sys

from PyQt6.QtWidgets import QApplication
from utils.helpers import preguntar_modo_interfaz
from views.gui import LoginWindow
from views.login import VistaLogin


def main():
    """Inicia PROMPTY usando la interfaz elegida por el usuario."""
    if preguntar_modo_interfaz():
        app = QApplication(sys.argv)
        login = LoginWindow()
        login.show()
        app.exec()
    else:
        VistaLogin().iniciar()


if __name__ == "__main__":
    main()
