import datetime
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_2.5'))

from services import comandos_basicos


class FixedDateTime(datetime.datetime):
    fixed = datetime.datetime(2020, 1, 2, 15, 30, 45)

    @classmethod
    def now(cls):
        return cls.fixed


def test_mostrar_fechas(monkeypatch):
    monkeypatch.setattr(comandos_basicos.datetime, "datetime", FixedDateTime)
    cb = comandos_basicos.ComandosBasicos()
    assert cb.mostrar_fecha() == "📅 La fecha de hoy es 02/01/2020."
    assert cb.mostrar_hora() == "🕒 La hora actual es 03:30 PM."
    assert cb.mostrar_fecha_hora() == "📆 02/01/2020 🕒 15:30:45"


def test_construir_url():
    cb = comandos_basicos.ComandosBasicos()
    assert cb.construir_url("hola mundo", "youtube") == "https://www.youtube.com/results?search_query=hola+mundo"
    assert cb.construir_url("hola mundo", "navegador") == "https://www.google.com/search?q=hola+mundo"
    assert cb.construir_url("hola", "otro") is None


def test_abrir_url(monkeypatch):
    opened = {}
    monkeypatch.setattr(comandos_basicos.shutil, "which", lambda _: None)
    monkeypatch.setattr(comandos_basicos.webbrowser, "open", lambda url: opened.setdefault("url", url))

    cb = comandos_basicos.ComandosBasicos()
    assert cb.abrir_url("ftp://example.com").startswith("\u274c")
    assert cb.abrir_url("https://example.com") == "🌐 Abriendo: https://example.com"
    assert opened["url"] == "https://example.com"
