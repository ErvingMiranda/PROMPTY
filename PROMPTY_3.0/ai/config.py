"""Carga y modela la configuración necesaria para usar la IA remota."""
from __future__ import annotations

from dataclasses import dataclass
import json
import os
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_BASE_URL = "https://router.huggingface.co"
CONFIG_LOCAL_PATH = Path(__file__).resolve().parent.parent / "config_local.json"


@dataclass
class IAConfig:
    """Configuración necesaria para conectarse al proveedor de IA."""

    api_token: Optional[str] = None
    model_id: str = "mistralai/Mistral-7B-Instruct-v0.3"
    base_url: Optional[str] = DEFAULT_BASE_URL
    timeout: float = 45.0
    max_new_tokens: int = 320
    temperature: float = 0.4

    @property
    def endpoint(self) -> str:
        base = (self.base_url or DEFAULT_BASE_URL).rstrip("/")
        if base.endswith("/v1/chat"):
            return f"{base}/completions"
        if base.endswith("/v1"):
            return f"{base}/chat/completions"
        return f"{base}/v1/chat/completions"

    @classmethod
    def _load_local_config(cls) -> Dict[str, Any]:
        if not CONFIG_LOCAL_PATH.exists():
            return {}
        try:
            with CONFIG_LOCAL_PATH.open("r", encoding="utf-8") as handler:
                data = json.load(handler)
            if isinstance(data, dict):
                return data
        except (OSError, ValueError):
            pass
        return {}

    @classmethod
    def from_env(cls) -> "IAConfig":
        local_config = cls._load_local_config()
        token = local_config.get("api_token") if isinstance(local_config, dict) else None
        model = local_config.get("model_id") if isinstance(local_config, dict) else None
        base_url = local_config.get("base_url") if isinstance(local_config, dict) else None
        timeout = local_config.get("timeout") if isinstance(local_config, dict) else None
        max_new_tokens = (
            local_config.get("max_new_tokens") if isinstance(local_config, dict) else None
        )
        temperature = local_config.get("temperature") if isinstance(local_config, dict) else None

        token = token or (
            os.getenv("PROMPTY_IA_TOKEN")
            or os.getenv("HUGGING_FACE_API_TOKEN")
            or os.getenv("HF_API_TOKEN")
        )
        model = model or os.getenv("PROMPTY_IA_MODEL") or cls.model_id
        base_url = base_url or os.getenv("PROMPTY_IA_BASE_URL") or DEFAULT_BASE_URL
        timeout = float(timeout or os.getenv("PROMPTY_IA_TIMEOUT", cls.timeout))
        max_new_tokens = int(max_new_tokens or os.getenv("PROMPTY_IA_MAX_TOKENS", cls.max_new_tokens))
        temperature = float(temperature or os.getenv("PROMPTY_IA_TEMPERATURE", cls.temperature))
        return cls(
            api_token=token,
            model_id=model,
            base_url=base_url,
            timeout=timeout,
            max_new_tokens=max_new_tokens,
            temperature=temperature,
        )
