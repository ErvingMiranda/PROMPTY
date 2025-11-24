"""Interfaces públicas para la integración de IA en PROMPTY."""
from .assistant import AsistenteIA
from .config import CONFIG_LOCAL_PATH, DEFAULT_BASE_URL, IAConfig
from .service import ServicioIA

__all__ = [
    "AsistenteIA",
    "CONFIG_LOCAL_PATH",
    "DEFAULT_BASE_URL",
    "IAConfig",
    "ServicioIA",
]
