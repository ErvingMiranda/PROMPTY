class Comando:
    """Representa un comando disponible en PROMPTY."""

    def __init__(self, nombre: str, descripcion: str, nivel_requerido: str):
        self.nombre = nombre
        self.descripcion = descripcion
        self.nivel_requerido = nivel_requerido

    def __repr__(self) -> str:
        return f"Comando(nombre={self.nombre!r}, nivel={self.nivel_requerido!r})"
