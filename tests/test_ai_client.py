"""Tests unitarios para la capa de integración con IA."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))

from services.ai_client import IAConfig, ServicioIA


def test_config_from_env(monkeypatch):
    monkeypatch.setenv("HUGGING_FACE_API_TOKEN", "abc123")
    monkeypatch.setenv("PROMPTY_IA_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    monkeypatch.setenv("PROMPTY_IA_BASE_URL", "https://demo.test/model")
    monkeypatch.setenv("PROMPTY_IA_TIMEOUT", "12.5")
    monkeypatch.setenv("PROMPTY_IA_MAX_TOKENS", "128")
    monkeypatch.setenv("PROMPTY_IA_TEMPERATURE", "0.75")

    config = IAConfig.from_env()

    assert config.api_token == "abc123"
    assert config.model_id == "meta-llama/Llama-3.1-8B-Instruct"
    assert config.endpoint == "https://demo.test/model"
    assert config.timeout == 12.5
    assert config.max_new_tokens == 128
    assert config.temperature == 0.75


def test_default_endpoint_uses_router_domain():
    config = IAConfig()

    assert config.endpoint == "https://router.huggingface.co/hf-inference/models/mistralai/Mistral-7B-Instruct-v0.3"


def test_build_payload_includes_historial():
    config = IAConfig(api_token="token", model_id="demo-model")
    servicio = ServicioIA(config=config, client=None)

    historial = [
        {"rol": "usuario", "contenido": "Hola"},
        {"rol": "asistente", "contenido": "¿En qué te ayudo?"},
    ]

    payload = servicio._build_payload("Necesito ideas", historial)

    assert "Necesito ideas" in payload["inputs"]
    assert "Usuario: Hola" in payload["inputs"]
    assert "PROMPTY: ¿En qué te ayudo?" in payload["inputs"]
    assert payload["parameters"]["max_new_tokens"] == config.max_new_tokens
    assert payload["parameters"]["temperature"] == config.temperature
