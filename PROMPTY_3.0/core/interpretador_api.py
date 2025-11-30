from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any, Dict, Optional

from services.comandos_basicos import ComandosBasicos
from services.interpretador import interpretar

logger = logging.getLogger(__name__)

_basicos = ComandosBasicos()


@dataclass
class ResultadoInterpretacion:
    texto_respuesta: str
    accion: Optional[str] = None
    parametros: Optional[Dict[str, Any]] = None


def _extraer_termino(argumentos: Optional[Dict[str, Any]]) -> Optional[str]:
    if isinstance(argumentos, dict):
        for clave in ("termino", "query", "busqueda"):
            valor = argumentos.get(clave)
            if isinstance(valor, str) and valor.strip():
                return valor.strip()
    if isinstance(argumentos, str) and argumentos.strip():
        return argumentos.strip()
    return None


def interpretar_mensaje_api(mensaje: str) -> ResultadoInterpretacion:
    comando, argumentos, _ = interpretar(mensaje)

    parametros: Optional[Dict[str, Any]] = None
    accion: Optional[str] = None
    texto_respuesta: str

    if comando == "hora":
        accion = "decir_hora"
        texto_respuesta = _basicos.mostrar_hora()
    elif comando == "fecha":
        accion = "decir_fecha"
        texto_respuesta = _basicos.mostrar_fecha()
    elif comando == "fecha_hora":
        accion = "decir_fecha_hora"
        texto_respuesta = _basicos.mostrar_fecha_hora()
    elif comando == "dia_fecha":
        accion = "decir_dia_fecha"
        texto_respuesta = _basicos.mostrar_dia_fecha()
    elif comando == "buscar_en_youtube":
        termino = _extraer_termino(argumentos)
        accion = "buscar_youtube"
        parametros = {"query": termino} if termino else {}
        texto_respuesta = (
            f"🔎 Buscar en YouTube: {termino}" if termino else "¿Qué deseas buscar en YouTube?"
        )
    elif comando in ("buscar_en_navegador", "buscar_general"):
        termino = _extraer_termino(argumentos)
        accion = "buscar_navegador"
        parametros = {"query": termino} if termino else {}
        texto_respuesta = (
            f"🔎 Buscar en el navegador: {termino}" if termino else "¿Qué deseas buscar en el navegador?"
        )
    elif comando == "reproducir_musica":
        termino = _extraer_termino(argumentos)
        accion = "reproducir_musica"
        parametros = {"query": termino} if termino else {}
        texto_respuesta = (
            f"🎵 Reproducir en YouTube Music: {termino}"
            if termino
            else "¿Qué canción o artista quieres escuchar?"
        )
    elif comando == "dato_curioso":
        accion = "dato_curioso"
        texto_respuesta = _basicos.mostrar_dato_curioso()
    elif comando == "saludo":
        texto_respuesta = _basicos.responder_saludo()
    else:
        texto_respuesta = ""

    if accion:
        logger.info("[API] Mensaje interpretado: accion=%s, parametros=%s", accion, parametros or {})
        return ResultadoInterpretacion(
            texto_respuesta=texto_respuesta,
            accion=accion,
            parametros=parametros,
        )

    return ResultadoInterpretacion(texto_respuesta=texto_respuesta)
