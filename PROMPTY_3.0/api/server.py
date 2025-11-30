"""API REST ligera para consumir las capacidades inteligentes de PROMPTY."""

from __future__ import annotations

import json
import logging
import webbrowser
from datetime import date, datetime
from typing import Any, Dict, List, Literal, Optional, Tuple
from urllib.parse import quote_plus

from fastapi import FastAPI, HTTPException
from fastapi.concurrency import run_in_threadpool
from pydantic import BaseModel, Field

from ai import ServicioIA
from prompty_core import ACCIONES_DISPONIBLES
from prompty_core.comandos import abrir_youtube, obtener_hora_actual
from services.gestor_comandos import GestorComandos
from services import interpretador
from services import datos_curiosos

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


INTENCIONES_PERMITIDAS = {
    "hora",
    "fecha",
    "fecha_hora",
    "dia_fecha",
    "abrir_navegador",
    "buscar_en_navegador",
    "buscar_general",
    "buscar_youtube",
    "reproducir_musica",
    "dato_curioso",
    "informacion",
    "abrir_carpeta",
    "abrir_archivo",
    "abrir_con_opcion",
    "salir",
    "saludo",
}


CLASIFICADOR_SYSTEM_PROMPT = """
Eres un asistente que SOLO clasifica intenciones en español.
Debes devolver únicamente un JSON usando este formato exacto:
{
  "intencion": "hora|fecha|fecha_hora|abrir_navegador|buscar_youtube|reproducir_musica|dato_curioso|informacion|abrir_archivo|abrir_carpeta|salir|saludo",
  "argumento": "texto opcional relacionado (busqueda, ruta, etc.)"
}

Reglas:
- No inventes acciones fuera de la lista.
- No devuelvas explicaciones ni texto fuera del JSON.
- Usa "buscar_youtube" si quiere buscar o reproducir algo en YouTube.
- Usa "abrir_navegador" para búsquedas o URLs genéricas.
- Usa "reproducir_musica" para peticiones de música.
- Si no reconoces la intención, usa "intencion": "saludo" cuando sea un saludo o "intencion": "dato_curioso" solo si lo pide, de lo contrario "intencion": ""
- El modelo cliente ejecutará la acción real; tú solo clasificas.
"""


_MESES_ES = [
    "enero",
    "febrero",
    "marzo",
    "abril",
    "mayo",
    "junio",
    "julio",
    "agosto",
    "septiembre",
    "octubre",
    "noviembre",
    "diciembre",
]

_HORA_PATRONES = (
    "que hora es",
    "qué hora es",
    "dime la hora",
    "dime la hora actual",
    "hora actual",
)

_FECHA_PATRONES = (
    "que fecha es hoy",
    "qué fecha es hoy",
    "dime la fecha",
    "dime la fecha de hoy",
    "fecha de hoy",
)


def _hora_actual() -> str:
    return datetime.now().strftime("%H:%M")


def _fecha_actual() -> str:
    hoy = date.today()
    mes = _MESES_ES[hoy.month - 1]
    return f"{hoy.day} de {mes} de {hoy.year}"


def _extraer_busqueda_youtube(mensaje: str) -> str:
    palabras = [p for p in mensaje.split() if p.lower() != "youtube"]
    termino = " ".join(palabras).strip()
    return termino or "YouTube"


def resolver_comando_local(mensaje: str) -> Optional[str]:
    """
    Si el mensaje coincide con un comando soportado (hora, fecha, youtube,
    dato curioso), devuelve el texto de respuesta ya listo.
    Si no coincide con nada, devuelve None.
    """

    if not mensaje:
        return None

    mensaje_limpio = mensaje.strip()
    mensaje_minusculas = mensaje_limpio.lower()

    if any(patron in mensaje_minusculas for patron in _HORA_PATRONES):
        return f"La hora actual es: {_hora_actual()}"

    if any(patron in mensaje_minusculas for patron in _FECHA_PATRONES):
        return f"Hoy es {_fecha_actual()}"

    if "youtube" in mensaje_minusculas:
        termino = _extraer_busqueda_youtube(mensaje_limpio)
        url = "https://www.youtube.com/results?search_query=" + quote_plus(termino)
        webbrowser.open(url)
        return f"Abriendo YouTube para buscar: {termino}"

    if "dato curioso" in mensaje_minusculas:
        return datos_curiosos.mostrar_curiosidad()

    return None


def _parsear_clasificacion(texto: str) -> Tuple[Optional[str], Optional[str]]:
    if not texto:
        return None, None

    texto_limpio = texto.strip()
    try:
        data = json.loads(texto_limpio)
        intencion = str(
            data.get("intencion") or data.get("accion") or ""
        ).strip().lower()
        argumento = data.get("argumento") or data.get("query") or data.get("busqueda")
    except ValueError:
        intencion = texto_limpio.lower()
        argumento = None

    if intencion not in INTENCIONES_PERMITIDAS:
        return None, None

    if isinstance(argumento, str):
        argumento = argumento.strip() or None

    return intencion, argumento


async def clasificar_intencion(
    mensaje: str, historial: Optional[List[Dict[str, str]]] = None
) -> Tuple[Optional[str], Optional[str]]:
    texto_modelo, exito = await run_in_threadpool(
        servicio_ia._consultar_modelo,  # noqa: SLF001 - uso interno controlado
        mensaje,
        historial,
        CLASIFICADOR_SYSTEM_PROMPT,
    )

    if exito:
        intencion, argumento = _parsear_clasificacion(texto_modelo)
        if intencion:
            return intencion, argumento

    return interpretador.interpretar_intencion_local(mensaje)


@app.get("/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.post("/api/chat", response_model=ChatResponse)
async def chat(req: ChatRequest) -> ChatResponse:
    mensaje = req.mensaje
    historial = req.historial

    try:
        respuesta_local = resolver_comando_local(mensaje)
        if respuesta_local is not None:
            return ChatResponse(respuesta=respuesta_local, exito=True)

        intencion, argumento = await clasificar_intencion(mensaje, historial)

        if not intencion:
            return ChatResponse(
                respuesta="No pude entender tu solicitud. ¿Podrías reformularla?",
                exito=False,
            )

        respuesta, exito = await run_in_threadpool(
            interpretador.ejecutar_intencion, intencion, argumento
        )

        return ChatResponse(
            respuesta=respuesta,
            exito=exito,
        )
    except Exception as exc:  # pragma: no cover - se devuelve error controlado
        logger.exception("Error procesando /api/chat: %s", exc)
        return ChatResponse(
            respuesta="Ocurrió un error al procesar tu solicitud.",
            exito=False,
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
        comando, argumentos, _ = interpretador.interpretar(request.texto)
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
