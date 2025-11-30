"""API REST ligera para consumir las capacidades inteligentes de PROMPTY."""

from __future__ import annotations

from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ai import ServicioIA
from prompty_core import ACCIONES_DISPONIBLES, ejecutar_accion
from services.gestor_comandos import GestorComandos
from services.interpretador import interpretar

app = FastAPI(
    title="PROMPTY AI Service",
    description=(
        "Servicio HTTP para consultar la capa inteligente de PROMPTY. "
        "Puede reutilizarse desde MyPlanU u otros clientes."
    ),
    version="1.0.0",
)

servicio_ia = ServicioIA()
gestor_comandos = GestorComandos()


class MensajeHistorial(BaseModel):
    rol: str = Field(..., pattern="^(usuario|asistente|user|assistant)$")
    contenido: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1)
    historial: Optional[List[MensajeHistorial]] = None


class ChatResponse(BaseModel):
    respuesta: str
    exito: bool


class SmartChatRequest(BaseModel):
    mensaje: str = Field(..., min_length=1)
    historial: Optional[List[MensajeHistorial]] = None


class SmartChatResponse(BaseModel):
    accion: str
    respuesta_usuario: str
    resultado_accion: Optional[str] = None
    exito: bool


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
async def chat(request: ChatRequest) -> ChatResponse:
    try:
        respuesta, exito = await run_in_threadpool(
            servicio_ia.consultar, request.mensaje, [
                {"rol": h.rol, "contenido": h.contenido} for h in request.historial or []
            ]
        )
    except Exception as exc:  # pragma: no cover - FastAPI convertirá en JSON
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(respuesta=respuesta, exito=exito)


@app.post("/api/chat-inteligente", response_model=SmartChatResponse)
async def chat_inteligente(request: SmartChatRequest) -> SmartChatResponse:
    try:
        decision = await run_in_threadpool(
            servicio_ia.decidir_accion,
            request.mensaje,
            [
                {"rol": h.rol, "contenido": h.contenido} for h in request.historial or []
            ],
        )
    except Exception as exc:  # pragma: no cover - FastAPI convertirá en JSON
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    accion = decision.get("accion") if isinstance(decision, dict) else "ninguna"
    parametros = decision.get("parametros") if isinstance(decision, dict) else {}
    respuesta_usuario = str(
        (decision.get("respuesta_usuario") if isinstance(decision, dict) else "") or ""
    ).strip()
    decision_valida = bool(decision.get("exito", True)) if isinstance(decision, dict) else False

    if accion not in ACCIONES_DISPONIBLES:
        accion = "ninguna"

    resultado_accion: Optional[str] = None
    exito = decision_valida

    if accion != "ninguna":
        try:
            resultado_accion = await run_in_threadpool(
                ejecutar_accion, accion, parametros
            )
        except Exception as exc:  # pragma: no cover - seguridad adicional
            resultado_accion = f"❌ No pude completar la acción: {exc}"

        if isinstance(resultado_accion, str) and resultado_accion.strip():
            exito = exito and not resultado_accion.strip().startswith("❌")
            if respuesta_usuario:
                respuesta_usuario = f"{respuesta_usuario}\n{resultado_accion}" \
                    if resultado_accion else respuesta_usuario
            else:
                respuesta_usuario = resultado_accion

    if not respuesta_usuario:
        respuesta_usuario = "Aquí tienes la respuesta solicitada."

    return SmartChatResponse(
        accion=accion,
        respuesta_usuario=respuesta_usuario,
        resultado_accion=resultado_accion,
        exito=exito,
    )


@app.post("/api/command", response_model=CommandResponse)
async def command(request: CommandRequest) -> CommandResponse:
    """Interpreta un texto y ejecuta el comando si está soportado."""

    try:
        comando, argumentos, _ = interpretar(request.texto)
    except Exception as exc:  # pragma: no cover - FastAPI convertirá en JSON
        raise HTTPException(status_code=400, detail=str(exc)) from exc

    def _entrada_silenciosa(_: str = "") -> str:
        return ""

    if gestor_comandos.admite_comando(comando):
        entrada = _entrada_silenciosa if request.forzar_ejecucion else None
        resultado = await run_in_threadpool(
            gestor_comandos.ejecutar_logica, comando, argumentos, entrada
        )
        exito = not (isinstance(resultado, str) and resultado.strip().startswith("❌"))
        return CommandResponse(
            comando=comando,
            resultado=resultado,
            exito=exito,
            origen="gestor_comandos",
        )

    respuesta_ia, exito = await run_in_threadpool(
        servicio_ia.consultar, request.texto, None
    )
    return CommandResponse(
        comando=comando,
        resultado=respuesta_ia,
        exito=exito,
        origen="ia",
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
