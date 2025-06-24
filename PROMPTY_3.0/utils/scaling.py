from PyQt6.QtWidgets import QPushButton, QWidget
from PyQt6.QtGui import QFont
from PyQt6.QtCore import QSize
from data import config

class ScalingMixin:
    """Mixin que ajusta fuentes e iconos según el tamaño de la ventana."""
    base_width: int = 400
    base_height: int = 300
    font_family: str = config.FUENTE_POR_DEFECTO
    base_font_size: int = config.TAMANO_LETRA_POR_DEFECTO

    def get_scale_factor(self) -> float:
        w_factor = self.width() / self.base_width
        h_factor = self.height() / self.base_height
        return max(0.8, min(1.5, min(w_factor, h_factor)))

    def apply_scaling(self) -> None:
        factor = self.get_scale_factor()
        font = QFont(self.font_family, int(self.base_font_size * factor))
        self.setFont(font)

        for btn in self.findChildren(QPushButton):
            base_size = btn.property("base_size")
            base_icon = btn.property("base_icon")
            base_width = btn.property("base_width")
            base_height = btn.property("base_height")

            if base_size is not None:
                btn.setFixedSize(int(base_size * factor), int(base_size * factor))
                if base_icon is not None:
                    btn.setIconSize(QSize(int(base_icon * factor), int(base_icon * factor)))
            else:
                bw = base_width if base_width is not None else btn.width()
                bh = base_height if base_height is not None else 30
                btn.setFixedSize(int(bw * factor), int(bh * factor))

        for child in self.findChildren(QWidget):
            if isinstance(child, QPushButton):
                continue
            bw = child.property("base_width")
            bh = child.property("base_height")
            if bw is not None:
                child.setFixedWidth(int(bw * factor))
            if bh is not None:
                child.setFixedHeight(int(bh * factor))

        if hasattr(self, "on_apply_scaling"):
            self.on_apply_scaling(factor)

    def resizeEvent(self, event):  # type: ignore
        super().resizeEvent(event)
        self.apply_scaling()
