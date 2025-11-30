"""API REST ligera para consumir las capacidades inteligentes de PROMPTY.

Esta API expone PROMPTY Lite: solo ofrece conversación con IA y nunca ejecuta
acciones locales. El PROMPTY completo (aplicación de escritorio) mantiene las
funciones de automatización como abrir YouTube, gestionar carpetas o lanzar
programas. Aquí solo se delegan consultas textuales a la IA.
"""

from __future__ import annotations

import logging
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ai import ServicioIA

_LITE_LIMITATION_MESSAGE = (
    "En esta versión (PROMPTY Lite) no puedo abrir aplicaciones ni ver tu sistema. "
    "Pero si estás usando el PROMPTY completo en tu computadora, podés usar el "
    "comando correspondiente para abrir YouTube o la carpeta que necesitás."
)

app = FastAPI(
    title="PROMPTY AI Service",
    description=(
        "Servicio HTTP para consultar la capa inteligente de PROMPTY. "
        "Puede reutilizarse desde MyPlanU u otros clientes."
    ),
    version="1.0.0",
)

servicio_ia = ServicioIA()

logger = logging.getLogger(__name__)


async def _consultar_api_lite(
    mensaje: str, historial: Optional[List[Dict[str, str]]] = None
) -> tuple[str, bool]:
    """Envía la solicitud a la IA Lite sin disparar acciones locales."""

    return await run_in_threadpool(servicio_ia.consultar_lite, mensaje, historial)


def _requiere_accion_local(contenido: Optional[str]) -> bool:
    """Detecta de forma básica peticiones que requieren acceso al sistema local."""

    if not contenido:
        return False

    texto = contenido.lower()
    patrones_directos = [
        "abrí youtube",
        "abre youtube",
        "abrir youtube",
        "mostrame la hora",
        "mostrar la hora",
        "mostrarme la hora",
        "abrí una carpeta",
        "abre una carpeta",
        "abrir una carpeta",
    ]

    if any(patron in texto for patron in patrones_directos):
        return True

    if "youtube" in texto and "abr" in texto:
        return True
    if "carpeta" in texto and "abr" in texto:
        return True
    if "hora" in texto and any(gatil in texto for gatil in ("qué", "que", "dime", "di", "mostrar")):
        return True

    return False


def _es_peticion_de_accion_local(
    mensaje: str, historial: Optional[List[Dict[str, str]]]
) -> bool:
    if _requiere_accion_local(mensaje):
        return True

    if historial:
        for turno in historial:
            rol = (turno.get("rol") or turno.get("role") or "").lower()
            if rol.startswith("u") and _requiere_accion_local(
                turno.get("contenido") or turno.get("content")
            ):
                return True

    return False


class MensajeHistorial(BaseModel):
    rol: Literal["usuario", "asistente"]
    contenido: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1, alias="mensaje")
    historial: Optional[List[Dict[str, str]]] = Field(
        default=None, alias="historial"
    )

    class Config:
        allow_population_by_field_name = True


class ChatResponse(BaseModel):
    respuesta: str
    exito: bool = True


class SmartChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1)
    historial: Optional[List[MensajeHistorial]] = None


class SmartChatResponse(BaseModel):
    respuesta: str


class CommandRequest(BaseModel):
    texto: str = Field(..., min_length=1)
    forzar_ejecucion: bool = False


class CommandResponse(BaseModel):
    comando: str
    resultado: str
    exito: bool
    origen: str


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    mensaje = req.mensaje
    historial = req.historial

    if _es_peticion_de_accion_local(mensaje, historial):
        return ChatResponse(respuesta=_LITE_LIMITATION_MESSAGE, exito=True)

    try:
        respuesta, exito = await _consultar_api_lite(mensaje, historial)
        return ChatResponse(respuesta=respuesta, exito=exito)
    except Exception as exc:  # pragma: no cover - se devuelve error controlado
        logger.exception("Error procesando /api/chat: %s", exc)
        return ChatResponse(
            respuesta="Ocurrió un error al procesar tu solicitud.",
            exito=False,
        )


@app.post("/api/chat-inteligente", response_model=SmartChatResponse)
async def chat_inteligente(request: SmartChatRequest) -> SmartChatResponse:
    if _es_peticion_de_accion_local(
        request.mensaje,
        [
            {"rol": h.rol, "contenido": h.contenido}
            for h in (request.historial or [])
        ],
    ):
        return SmartChatResponse(respuesta=_LITE_LIMITATION_MESSAGE)

    try:
        respuesta, _ = await _consultar_api_lite(
            request.mensaje,
            [
                {"rol": h.rol, "contenido": h.contenido} for h in request.historial or []
            ],
        )
        return SmartChatResponse(respuesta=respuesta)
    except Exception as exc:  # pragma: no cover - FastAPI convertirá en JSON
        raise HTTPException(status_code=500, detail=str(exc)) from exc


@app.post("/api/command", response_model=CommandResponse)
async def command(request: CommandRequest) -> CommandResponse:
    """Responde usando la IA sin ejecutar acciones locales."""

    if _es_peticion_de_accion_local(request.texto, None):
        return CommandResponse(
            comando="sin_ejecucion",
            resultado=_LITE_LIMITATION_MESSAGE,
            exito=True,
            origen="ia-lite",
        )

    respuesta_ia, exito = await _consultar_api_lite(request.texto, None)
    return CommandResponse(
        comando="sin_ejecucion",
        resultado=respuesta_ia,
        exito=exito,
        origen="ia-lite",
    )


@app.get("/")
async def root() -> dict:
    return {
        "mensaje": "PROMPTY API lista",
        "endpoints": [
            "GET /health",
            "POST /api/chat",
            "POST /api/chat-inteligente",
            "POST /api/command",
        ],
    }
