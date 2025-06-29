import sys
from types import SimpleNamespace
from pathlib import Path

# Crear módulo falso de pyttsx3 antes de importar el servicio
_created = []

def _fake_init():
    class FakeEngine:
        def __init__(self):
            self.stopped = False
        def setProperty(self, *args, **kwargs):
            pass
        def say(self, text):
            pass
        def runAndWait(self):
            pass
        def isBusy(self):
            return False
        def stop(self):
            self.stopped = True
    engine = FakeEngine()
    _created.append(engine)
    return engine

sys.modules['pyttsx3'] = SimpleNamespace(init=_fake_init)
class DummyRecognizer:
    def __init__(self):
        pass

class DummyMicrophone:
    pass

sys.modules['speech_recognition'] = SimpleNamespace(Recognizer=DummyRecognizer, Microphone=DummyMicrophone)

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))

import services.asistente_voz as av


def test_recrear_motor_si_se_descarta(monkeypatch):
    usuario = SimpleNamespace(rol="usuario")
    voz = av.ServicioVoz(usuario)
    primero = voz.engine
    voz.detener()
    assert voz.engine is None
    voz.hablar("hola")
    assert voz.engine is not None
    assert voz.engine is not primero
    assert len(_created) == 2


def test_normalizar_numeros(monkeypatch):
    usuario = SimpleNamespace(rol="usuario")
    voz = av.ServicioVoz(usuario)
    texto = voz.hablar("Tengo 1000 pesos")
    assert "mil" in texto
