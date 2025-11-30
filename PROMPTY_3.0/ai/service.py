"""Cliente HTTP que delega llamadas al proveedor de IA."""
from __future__ import annotations

import json
from threading import Lock
from typing import Any, Dict, List, Optional

import httpx

from prompty_core.comandos import ACCIONES_DISPONIBLES

from .config import CONFIG_LOCAL_PATH, IAConfig

_SYSTEM_PROMPT = (
    "PROMPTY es un asistente virtual de escritorio desarrollado en Python. "
    "Su función principal es ayudar a los usuarios a realizar tareas cotidianas como abrir archivos, "
    "mostrar la hora, buscar en YouTube y ofrecer datos curiosos, respondiendo tanto por texto como por voz. "
    "En el futuro se integrará con la aplicación MyPlanU (desarrollada en .NET y WinForms) a través de una API, "
    "lo que le permitirá crear tareas y realizar acciones dentro de MyPlanU según las instrucciones del usuario. "
    "Por ahora, si un usuario solicita algo relacionado con tareas, simplemente informa que esta funcionalidad estará disponible "
    "próximamente mediante esa integración y que en el futuro podrá realizar esas tareas directamente en MyPlanU. "
    "Actúa siempre de forma clara y concisa, sin inventar datos ni enlaces que no existan."
)

_ACTION_SYSTEM_PROMPT = (
    "Eres PROMPTY, un asistente local que decide qué acción ejecutar en el equipo. "
    "Analiza la solicitud del usuario y responde únicamente con JSON válido siguiendo esta estructura: "
    '{"accion": "<accion>", "parametros": {}, "respuesta_usuario": "<mensaje>"}. '
    "Las acciones permitidas son: "
    f"{', '.join(ACCIONES_DISPONIBLES)}. "
    "Usa 'abrir_youtube' cuando debas abrir YouTube con una búsqueda (parametros: {\"query\": \"texto\"}). "
    "Usa 'decir_hora' cuando pidan la hora (parametros vacío: {}). "
    "Cuando no proceda acción alguna devuelve 'accion': 'ninguna'. "
    "No inventes acciones nuevas, no añadas texto fuera del JSON, evita explicaciones adicionales y no uses Markdown. "
    "La clave 'respuesta_usuario' debe contener un mensaje amable y breve en español para mostrar al usuario."
)


class ServicioIA:
    """Encapsula las llamadas HTTP hacia el proveedor de IA."""

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
        system_prompt: str,
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
        system_prompt: str,
    ) -> Dict[str, Any]:
        return {
            "model": self.config.model_id,
            "messages": self._build_messages(mensaje, historial, system_prompt),
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

    def _consultar_modelo(
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

    def consultar(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, bool]:
        return self._consultar_modelo(mensaje, historial, _SYSTEM_PROMPT)

    def decidir_accion(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        texto, exito = self._consultar_modelo(mensaje, historial, _ACTION_SYSTEM_PROMPT)
        if not exito:
            return {
                "accion": "ninguna",
                "parametros": {},
                "respuesta_usuario": texto,
                "exito": False,
            }

        try:
            data = json.loads(texto)
        except ValueError:
            return {
                "accion": "ninguna",
                "parametros": {},
                "respuesta_usuario": texto,
                "exito": False,
            }

        accion = str(data.get("accion", "ninguna") or "ninguna").strip()
        if accion not in ACCIONES_DISPONIBLES:
            accion = "ninguna"
        parametros = data.get("parametros") if isinstance(data, dict) else {}
        if not isinstance(parametros, dict):
            parametros = {}
        respuesta_usuario = str(data.get("respuesta_usuario") or "").strip()
        if not respuesta_usuario:
            respuesta_usuario = "Aquí tienes la respuesta solicitada."

        return {
            "accion": accion,
            "parametros": parametros,
            "respuesta_usuario": respuesta_usuario,
            "exito": True,
        }
