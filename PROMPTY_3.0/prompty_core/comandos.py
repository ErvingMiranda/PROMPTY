"""Acciones reutilizables para ejecutar comandos locales de PROMPTY."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, Optional

from services.comandos_basicos import ComandosBasicos


_ACCIONES_MAPEADAS = {
    "ninguna": "ninguna",
    "abrir_youtube": "abrir_youtube",
    "decir_hora": "decir_hora",
}

ACCIONES_DISPONIBLES = tuple(_ACCIONES_MAPEADAS.keys())

_comandos = ComandosBasicos()


def _extraer_query(parametros: Optional[Dict[str, Any]]) -> Optional[str]:
    if isinstance(parametros, dict):
        for clave in ("query", "termino", "busqueda"):
            valor = parametros.get(clave)
            if isinstance(valor, str) and valor.strip():
                return valor.strip()
    if isinstance(parametros, str) and parametros.strip():
        return parametros.strip()
    return None


def abrir_youtube(query: str) -> str:
    termino = (query or "").strip()
    if not termino:
        return "❌ No se especificó qué buscar en YouTube."
    return _comandos.buscar_en_navegador_con_opcion(
        destino_predefinido="youtube", termino=termino
    )


def obtener_hora_actual() -> str:
    return datetime.now().strftime("%H:%M")


def decir_hora(_: Optional[Dict[str, Any]] = None) -> str:
    return _comandos.mostrar_hora()


def ejecutar_accion(accion: str, parametros: Optional[Dict[str, Any]] = None) -> str:
    """Ejecuta la acción solicitada si está soportada."""

    accion_normalizada = (accion or "").strip().lower()
    if accion_normalizada not in ACCIONES_DISPONIBLES:
        accion_normalizada = "ninguna"

    if accion_normalizada == "abrir_youtube":
        query = _extraer_query(parametros)
        if not query:
            return "❌ No se especificó qué buscar en YouTube."
        return abrir_youtube(query)
    if accion_normalizada == "decir_hora":
        return decir_hora(parametros)

    return "No hay acciones para ejecutar."
