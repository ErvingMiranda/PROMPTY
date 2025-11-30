"""Cliente HTTP para PROMPTY Lite.

Este módulo se usa desde el servidor/API (PROMPTY Lite) únicamente para
mantener una conversación textual. En esta edición no se ejecutan acciones
locales ni comandos del sistema; las capacidades completas (abrir YouTube,
gestionar carpetas, lanzar programas, etc.) siguen viviendo en el PROMPTY de
escritorio y sus módulos de automatización.
"""
from __future__ import annotations

import json
from threading import Lock
from typing import Any, Dict, List, Optional

import httpx

from prompty_core.comandos import ACCIONES_DISPONIBLES

from .config import CONFIG_LOCAL_PATH, IAConfig

_CHAT_SYSTEM_PROMPT = (
    "Eres PROMPTY, un asistente de escritorio. Responde en español de forma clara "
    "y breve. No describas acciones técnicas ni menciones limitaciones; habla "
    "directamente al usuario con la información solicitada."
)

_SYSTEM_PROMPT = (
    "Eres PROMPTY Lite, una versión limitada de un asistente de escritorio en español. "
    "Tu función es mantener una conversación clara y útil con el usuario, "
    "dando explicaciones y pasos concretos en menos de 200 palabras. "
    "No tienes acceso al sistema operativo, no puedes abrir aplicaciones, "
    "no puedes ver la hora real ni manejar archivos o carpetas. "
    "Si el usuario te pide hacer algo que requiera acceso al sistema, "
    "explícale que esta versión solo puede dar indicaciones y recomiéndale "
    "usar la versión completa de PROMPTY instalada en su computadora. "
    "Cuando te pidan abrir YouTube, mostrar la hora, abrir carpetas u otras acciones locales, "
    "responde con claridad que PROMPTY Lite no puede hacerlo y añade un aviso como: "
    "'En esta versión (PROMPTY Lite) no puedo abrir aplicaciones ni ver tu sistema. "
    "Pero si estás usando el PROMPTY completo en tu computadora, podés usar el comando "
    "correspondiente para abrir YouTube o la carpeta que necesitás.' "
    "Nunca finjas que ejecutas acciones reales; solo describe lo que el usuario podría hacer."
)

_AUTOMATION_SYSTEM_PROMPT = """
Eres PROMPTY, un asistente de escritorio en español.

Tu misión es:
1) Interpretar lo que quiere el usuario.
2) Decidir si se debe ejecutar una acción local.
3) Responder SIEMPRE en JSON, con este formato EXACTO:

{
  "accion": "ninguna" | "abrir_youtube" | "decir_hora",
  "parametros": {},
  "respuesta_usuario": "texto a mostrar al usuario"
}

Reglas importantes:
- NO agregues texto fuera del JSON.
- Si el usuario quiere buscar algo en YouTube:
    accion = "abrir_youtube"
    parametros = {"query": "<texto a buscar>"}
- Si el usuario pregunta la hora:
    accion = "decir_hora"
    parametros = {}
- Si solo conversa:
    accion = "ninguna"
- No inventes acciones que no estén en esta lista.
"""

_DEFAULT_JSON_RESPONSE = {
    "accion": "ninguna",
    "parametros": {},
    "respuesta_usuario": (
        "Tuve un problema interpretando la respuesta de la IA. "
        "¿Podrías repetir lo que necesitas?"
    ),
}


class ServicioIA:
    """Encapsula las llamadas HTTP hacia el proveedor de IA."""

    # Este cliente HTTP se usa desde la API de PROMPTY Lite: solo conversa y
    # nunca ejecuta acciones locales. Las acciones reales siguen viviendo en los
    # módulos del PROMPTY de escritorio que interactúan con el sistema operativo.

    def __init__(self, config: Optional[IAConfig] = None, client: Optional[httpx.Client] = None):
        self.config = config or IAConfig.from_env()
        self._client = client
        self._client_lock = Lock()

    def _get_client(self) -> httpx.Client:
        with self._client_lock:
            if self._client is None:
                self._client = httpx.Client(timeout=self.config.timeout)
            return self._client

    def _headers(self) -> Dict[str, str]:
        headers = {"Content-Type": "application/json"}
        if self.config.api_token:
            headers["Authorization"] = f"Bearer {self.config.api_token}"
        return headers

    def _build_messages(
        self,
        mensaje: str,
        historial: Optional[List[Dict[str, str]]],
        system_prompt: str = _CHAT_SYSTEM_PROMPT,
    ) -> List[Dict[str, str]]:
        mensajes: List[Dict[str, str]] = [
            {"role": "system", "content": system_prompt}
        ]
        if historial:
            for turno in historial:
                rol = (turno.get("rol") or turno.get("role") or "usuario").lower()
                contenido = turno.get("contenido") or turno.get("content") or ""
                role = "assistant" if rol.startswith("a") else "user"
                mensajes.append({"role": role, "content": contenido})
        mensajes.append({"role": "user", "content": mensaje})
        return mensajes

    def _build_payload(
        self,
        mensaje: str,
        historial: Optional[List[Dict[str, str]]],
        system_prompt: str = _CHAT_SYSTEM_PROMPT,
    ) -> Dict[str, Any]:
        return {
            "model": self.config.model_id,
            "messages": self._build_messages(
                mensaje, historial, system_prompt or _CHAT_SYSTEM_PROMPT
            ),
            "temperature": self.config.temperature,
            "max_tokens": self.config.max_new_tokens,
        }

    def _extraer_texto(self, data: Any) -> Optional[str]:
        if isinstance(data, dict):
            if "choices" in data and isinstance(data["choices"], list):
                for choice in data["choices"]:
                    mensaje = choice.get("message") if isinstance(choice, dict) else None
                    if isinstance(mensaje, dict) and "content" in mensaje:
                        return str(mensaje.get("content", "")).strip()
                    delta = choice.get("delta") if isinstance(choice, dict) else None
                    if isinstance(delta, dict) and "content" in delta:
                        return str(delta.get("content", "")).strip()
            if "generated_text" in data:
                return str(data["generated_text"]).strip()
            if "error" in data:
                return f"❌ {data['error']}"

        if isinstance(data, list) and data:
            candidato = data[0]
            if isinstance(candidato, dict):
                if "generated_text" in candidato:
                    return candidato["generated_text"].strip()
                if "error" in candidato:
                    return f"❌ {candidato['error']}"
        return None

    def _consultar_conversacion(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]], system_prompt: str
    ) -> tuple[str, bool]:
        mensaje = (mensaje or "").strip()
        if not mensaje:
            return "❌ No recibí ningún mensaje para enviar a la IA.", False

        if not self.config.api_token:
            return (
                "⚠️ Para habilitar el modo inteligente coloca tu token en 'config_local.json' "
                f"({CONFIG_LOCAL_PATH}) o define la variable de entorno "
                "'HUGGING_FACE_API_TOKEN' (puedes obtener un token gratuito en huggingface.co).",
                False,
            )

        payload = self._build_payload(mensaje, historial, system_prompt)
        try:
            respuesta = self._get_client().post(
                self.config.endpoint,
                headers=self._headers(),
                json=payload,
            )
            respuesta.raise_for_status()
        except httpx.HTTPStatusError as exc:
            cuerpo = exc.response.json() if exc.response.content else {}
            detalle = cuerpo.get("error") if isinstance(cuerpo, dict) else str(cuerpo)
            return f"❌ Error al consultar la IA: {detalle or exc}", False
        except httpx.RequestError as exc:
            return f"❌ No pude comunicarme con la IA: {exc}", False

        try:
            data = respuesta.json()
        except ValueError:
            return "❌ La IA devolvió una respuesta inválida.", False

        texto = self._extraer_texto(data)
        if not texto:
            return "⚠️ La IA no envió contenido útil.", False

        return texto.strip(), True

    def _consultar_automatizacion(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        texto, exito = self._consultar_conversacion(
            mensaje, historial, _AUTOMATION_SYSTEM_PROMPT
        )
        if not exito:
            fallback = dict(_DEFAULT_JSON_RESPONSE)
            fallback["respuesta_usuario"] = texto or fallback["respuesta_usuario"]
            return fallback

        try:
            data = json.loads(texto)
        except ValueError:
            return dict(_DEFAULT_JSON_RESPONSE)

        accion = str(data.get("accion", "ninguna") or "ninguna").strip()
        parametros = data.get("parametros") if isinstance(data, dict) else {}
        if not isinstance(parametros, dict):
            parametros = {}
        respuesta_usuario = str(data.get("respuesta_usuario") or "").strip()
        if not respuesta_usuario:
            respuesta_usuario = _DEFAULT_JSON_RESPONSE["respuesta_usuario"]

        if accion not in ACCIONES_DISPONIBLES:
            accion = "ninguna"

        return {
            "accion": accion,
            "parametros": parametros,
            "respuesta_usuario": respuesta_usuario,
        }

    def consultar(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, bool]:
        return self._consultar_conversacion(mensaje, historial, _CHAT_SYSTEM_PROMPT)

    def consultar_lite(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, bool]:
        return self._consultar_conversacion(mensaje, historial, _SYSTEM_PROMPT)

    def consultar_inteligente(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        return self._consultar_automatizacion(mensaje, historial)
