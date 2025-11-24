"""Tests unitarios para la capa de integración con IA."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))

from ai import IAConfig, ServicioIA


def test_config_prefers_local_file(tmp_path, monkeypatch):
    dummy_config = tmp_path / "config_local.json"
    dummy_config.write_text(
        '{"api_token": "local_token", "model_id": "local-model", "base_url": "https://custom"}',
        encoding="utf-8",
    )
    monkeypatch.setattr("ai.config.CONFIG_LOCAL_PATH", dummy_config)
    monkeypatch.delenv("HUGGING_FACE_API_TOKEN", raising=False)

    config = IAConfig.from_env()

    assert config.api_token == "local_token"
    assert config.model_id == "local-model"
    assert config.endpoint == "https://custom/v1/chat/completions"


def test_config_falls_back_to_env(monkeypatch):
    monkeypatch.setattr("ai.config.CONFIG_LOCAL_PATH", Path("/tmp/not_found.json"))
    monkeypatch.setenv("HUGGING_FACE_API_TOKEN", "abc123")
    monkeypatch.setenv("PROMPTY_IA_MODEL", "meta-llama/Llama-3.1-8B-Instruct")
    monkeypatch.setenv("PROMPTY_IA_BASE_URL", "https://demo.test/api")
    monkeypatch.setenv("PROMPTY_IA_TIMEOUT", "12.5")
    monkeypatch.setenv("PROMPTY_IA_MAX_TOKENS", "128")
    monkeypatch.setenv("PROMPTY_IA_TEMPERATURE", "0.75")

    config = IAConfig.from_env()

    assert config.api_token == "abc123"
    assert config.model_id == "meta-llama/Llama-3.1-8B-Instruct"
    assert config.endpoint == "https://demo.test/api/v1/chat/completions"
    assert config.timeout == 12.5
    assert config.max_new_tokens == 128
    assert config.temperature == 0.75


def test_build_payload_includes_historial():
    config = IAConfig(api_token="token", model_id="demo-model")
    servicio = ServicioIA(config=config, client=None)

    historial = [
        {"rol": "usuario", "contenido": "Hola"},
        {"rol": "asistente", "contenido": "¿En qué te ayudo?"},
    ]

    payload = servicio._build_payload("Necesito ideas", historial)

    assert payload["model"] == "demo-model"
    assert payload["temperature"] == config.temperature
    assert payload["max_tokens"] == config.max_new_tokens
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][-1]["content"] == "Necesito ideas"
