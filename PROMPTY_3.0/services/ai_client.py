"""Cliente para conectarse con modelos de IA externos (Hugging Face por defecto)."""

from __future__ import annotations

from dataclasses import dataclass
import os
from threading import Lock
from typing import Any, Dict, List, Optional

import httpx


_SYSTEM_PROMPT = (
    "Eres PROMPTY, un asistente de escritorio en español. "
    "Tu misión es responder con pasos claros y concretos en menos de 200 palabras. "
    "Puedes razonar y proponer acciones pero nunca inventes datos ni enlaces que no existan."
)


@dataclass
class IAConfig:
    """Configuración necesaria para conectarse al proveedor de IA."""

    api_token: Optional[str] = None
    model_id: str = "mistralai/Mistral-7B-Instruct-v0.3"
    base_url: Optional[str] = None
    timeout: float = 45.0
    max_new_tokens: int = 320
    temperature: float = 0.4

    @property
    def endpoint(self) -> str:
        if self.base_url:
            return self.base_url.rstrip("/")
        return f"https://router.huggingface.co/hf-inference/models/{self.model_id}"

    @classmethod
    def from_env(cls) -> "IAConfig":
        token = (
            os.getenv("PROMPTY_IA_TOKEN")
            or os.getenv("HUGGING_FACE_API_TOKEN")
            or os.getenv("HF_API_TOKEN")
        )
        model = os.getenv("PROMPTY_IA_MODEL") or cls.model_id
        base_url = os.getenv("PROMPTY_IA_BASE_URL")
        timeout = float(os.getenv("PROMPTY_IA_TIMEOUT", cls.timeout))
        max_new_tokens = int(os.getenv("PROMPTY_IA_MAX_TOKENS", cls.max_new_tokens))
        temperature = float(os.getenv("PROMPTY_IA_TEMPERATURE", cls.temperature))
        return cls(
            api_token=token,
            model_id=model,
            base_url=base_url,
            timeout=timeout,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
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

    def _build_prompt(self, mensaje: str, historial: Optional[List[Dict[str, str]]]) -> str:
        bloques = [_SYSTEM_PROMPT, "\nHistorial de la conversación:\n"]
        if historial:
            for turno in historial:
                rol = turno.get("rol") or turno.get("role") or "usuario"
                contenido = turno.get("contenido") or turno.get("content") or ""
                prefijo = "Usuario" if rol.startswith("u") else "PROMPTY"
                bloques.append(f"{prefijo}: {contenido}\n")
        bloques.append(f"Usuario: {mensaje}\nPROMPTY:")
        return "".join(bloques)

    def _build_payload(self, mensaje: str, historial: Optional[List[Dict[str, str]]]) -> Dict[str, Any]:
        prompt = self._build_prompt(mensaje, historial)
        return {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": self.config.max_new_tokens,
                "temperature": self.config.temperature,
                "return_full_text": False,
            },
        }

    def _extraer_texto(self, data: Any) -> Optional[str]:
        if isinstance(data, list) and data:
            candidato = data[0]
            if isinstance(candidato, dict):
                if "generated_text" in candidato:
                    return candidato["generated_text"].strip()
                if "error" in candidato:
                    return f"❌ {candidato['error']}"
        if isinstance(data, dict):
            if "generated_text" in data:
                return data["generated_text"].strip()
            if "error" in data:
                return f"❌ {data['error']}"
        return None

    def consultar(
        self, mensaje: str, historial: Optional[List[Dict[str, str]]] = None
    ) -> tuple[str, bool]:
        mensaje = (mensaje or "").strip()
        if not mensaje:
            return "❌ No recibí ningún mensaje para enviar a la IA.", False

        if not self.config.api_token and not self.config.base_url:
            return (
                "⚠️ Para habilitar el modo inteligente define la variable de entorno "
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


class AsistenteIA:
    """Gestiona el historial de conversación y delega la consulta al servicio."""

    def __init__(self, servicio: Optional[ServicioIA] = None):
        self.servicio = servicio or ServicioIA()
        self.historial: List[Dict[str, str]] = []

    def reiniciar_historial(self) -> None:
        self.historial.clear()

    def responder(self, mensaje: str) -> str:
        texto, exito = self.servicio.consultar(mensaje, self.historial)
        if exito:
            self.historial.append({"rol": "usuario", "contenido": mensaje.strip()})
            self.historial.append({"rol": "asistente", "contenido": texto})
        return texto
