"""Gestiona el historial de conversación y delega la consulta al servicio de IA."""
from __future__ import annotations

from typing import Dict, List, Optional

from .service import ServicioIA


class AsistenteIA:
    """Gestiona el historial de conversación y delega la consulta al servicio."""

    def __init__(self, servicio: Optional[ServicioIA] = None):
        self.servicio = servicio or ServicioIA()
        self.historial: List[Dict[str, str]] = []

    def reiniciar_historial(self) -> None:
        self.historial.clear()

    def responder(self, mensaje: str) -> str:
        texto, exito = self.servicio.consultar(mensaje, self.historial)
        if exito:
            self.historial.append({"rol": "usuario", "contenido": mensaje.strip()})
            self.historial.append({"rol": "asistente", "contenido": texto})
        return texto
