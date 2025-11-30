"""API REST ligera para consumir las capacidades inteligentes de PROMPTY."""

from __future__ import annotations

import logging
from typing import Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ai import ServicioIA

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

    try:
        respuesta, exito = await run_in_threadpool(
            servicio_ia.consultar_lite, mensaje, historial
        )
        return ChatResponse(respuesta=respuesta, exito=exito)
    except Exception as exc:  # pragma: no cover - se devuelve error controlado
        logger.exception("Error procesando /api/chat: %s", exc)
        return ChatResponse(
            respuesta="Ocurrió un error al procesar tu solicitud.",
            exito=False,
        )


@app.post("/api/chat-inteligente", response_model=SmartChatResponse)
async def chat_inteligente(request: SmartChatRequest) -> SmartChatResponse:
    try:
        respuesta, _ = await run_in_threadpool(
            servicio_ia.consultar_lite,
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

    respuesta_ia, exito = await run_in_threadpool(
        servicio_ia.consultar_lite, request.texto, None
    )
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
