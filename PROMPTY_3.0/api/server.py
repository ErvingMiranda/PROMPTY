"""API REST ligera para consumir las capacidades inteligentes de PROMPTY."""

from __future__ import annotations

from typing import Any, Dict, List, Literal, Optional

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ai import ServicioIA
from prompty_core import ACCIONES_DISPONIBLES
from prompty_core.comandos import abrir_youtube, obtener_hora_actual
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
    rol: Literal["usuario", "asistente"]
    contenido: str = Field(..., min_length=1)


class ChatRequest(BaseModel):
    Mensaje: str
    Historial: Optional[List[Dict[str, str]]] = None


class ChatResponse(BaseModel):
    respuesta: str
    accion: Optional[str] = None
    argumentos: Dict[str, Any] = Field(default_factory=dict)


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


def detectar_intencion(
    mensaje: str, historial: Optional[List[Dict[str, str]]] = None
) -> tuple[Optional[str], Dict[str, Any]]:
    """
    Devuelve (accion, argumentos) a partir del mensaje del usuario
    y, si es necesario, usando el último mensaje del asistente.
    Acciones soportadas:
      - "decir_hora"
      - "abrir_youtube"
      - None (solo charla)
    """

    texto = (mensaje or "").lower()

    if "hora" in texto or "qué hora es" in texto or "dime la hora" in texto:
        return "decir_hora", {}

    if "youtube" in texto or "video" in texto or "videos" in texto:
        return "abrir_youtube", {"query": mensaje}

    if texto.strip() in ("sí", "si", "dale", "ok") and historial:
        ultimo_asistente = next(
            (m for m in reversed(historial) if m.get("rol") == "asistente"),
            None,
        )
        if ultimo_asistente:
            contenido = (ultimo_asistente.get("contenido") or "").lower()
            if "youtube" in contenido:
                return "abrir_youtube", {"query": "búsqueda en youtube"}
            if "hora actual" in contenido:
                return "decir_hora", {}

    return None, {}


async def llamar_modelo(
    system_prompt: str, mensaje: str, historial: Optional[List[Dict[str, str]]]
) -> str:
    texto_modelo, _ = await run_in_threadpool(
        servicio_ia._consultar_modelo,  # noqa: SLF001 - uso interno controlado
        mensaje,
        historial,
        system_prompt,
    )
    return texto_modelo


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    mensaje = req.Mensaje
    historial = req.Historial

    accion, argumentos = detectar_intencion(mensaje, historial)

    system_prompt = (
        "Eres PROMPTY, un asistente virtual de planificación integrado en otra aplicación.\n"
        "Tu misión es responder en español con mensajes breves y claros.\n"
        "NO digas la hora tú mismo, ni abras YouTube, ni ejecutes acciones reales.\n"
        "Si el usuario pregunta la hora, responde algo como: "
        "'Te digo la hora actual en la aplicación.' sin inventar la hora.\n"
        "Si el usuario pide YouTube, responde algo como: "
        "'Puedo abrir YouTube para buscar eso en tu dispositivo.'\n"
        "El programa cliente se encargará de ejecutar los comandos basándose en la acción."
    )

    try:
        texto_modelo = await llamar_modelo(system_prompt, mensaje, historial)
    except Exception as exc:  # pragma: no cover - FastAPI convertirá en JSON
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    return ChatResponse(
        respuesta=texto_modelo,
        accion=accion,
        argumentos=argumentos,
    )


@app.post("/api/chat-inteligente", response_model=SmartChatResponse)
async def chat_inteligente(request: SmartChatRequest) -> SmartChatResponse:
    try:
        decision = await run_in_threadpool(
            servicio_ia.consultar_inteligente,
            request.mensaje,
            [
                {"rol": h.rol, "contenido": h.contenido} for h in request.historial or []
            ],
        )
    except Exception as exc:  # pragma: no cover - FastAPI convertirá en JSON
        raise HTTPException(status_code=500, detail=str(exc)) from exc

    accion = str(decision.get("accion") if isinstance(decision, dict) else "ninguna").strip()
    parametros = decision.get("parametros") if isinstance(decision, dict) else {}
    if not isinstance(parametros, dict):
        parametros = {}
    respuesta_usuario = str(
        (decision.get("respuesta_usuario") if isinstance(decision, dict) else "") or ""
    ).strip()

    if accion not in ACCIONES_DISPONIBLES:
        accion = "ninguna"

    if not respuesta_usuario:
        respuesta_usuario = (
            "Tuve un problema interpretando la respuesta de la IA. "
            "¿Podrías repetir lo que necesitas?"
        )

    if accion == "abrir_youtube":
        query = str(parametros.get("query", "")).strip()
        if query:
            await run_in_threadpool(abrir_youtube, query)
    elif accion == "decir_hora":
        hora_actual = obtener_hora_actual()
        if "{hora}" in respuesta_usuario:
            respuesta_usuario = respuesta_usuario.replace("{hora}", hora_actual)
        elif "hora" not in respuesta_usuario.lower():
            respuesta_usuario = f"{respuesta_usuario} Son las {hora_actual}."

    return SmartChatResponse(respuesta=respuesta_usuario)


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
