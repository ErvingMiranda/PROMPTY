"""Cliente HTTP que delega llamadas al proveedor de IA."""
from __future__ import annotations

from threading import Lock
from typing import Any, Dict, List, Optional

import httpx

from .config import CONFIG_LOCAL_PATH, IAConfig

_SYSTEM_PROMPT = (
    "Eres PROMPTY, un asistente de escritorio en español. "
    "Tu misión es responder con pasos claros y concretos en menos de 200 palabras. "
    "Puedes razonar y proponer acciones pero nunca inventes datos ni enlaces que no existan."
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

    def _build_messages(self, mensaje: str, historial: Optional[List[Dict[str, str]]]) -> List[Dict[str, str]]:
        mensajes: List[Dict[str, str]] = [
            {"role": "system", "content": _SYSTEM_PROMPT}
        ]
        if historial:
            for turno in historial:
                rol = (turno.get("rol") or turno.get("role") or "usuario").lower()
                contenido = turno.get("contenido") or turno.get("content") or ""
                role = "assistant" if rol.startswith("a") else "user"
                mensajes.append({"role": role, "content": contenido})
        mensajes.append({"role": "user", "content": mensaje})
        return mensajes

    def _build_payload(self, mensaje: str, historial: Optional[List[Dict[str, str]]]) -> Dict[str, Any]:
        return {
            "model": self.config.model_id,
            "messages": self._build_messages(mensaje, historial),
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

    def consultar(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
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

        payload = self._build_payload(mensaje, historial)
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
