import sys
from types import SimpleNamespace
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))
from services.asistente_voz import ServicioVoz

class DummyEngine:
    def __init__(self):
        self.voices = [SimpleNamespace(id='1', name='voice')]
        self.stopped = False
        self.busy = False
        self.last_said = None
    def say(self, text):
        self.last_said = text
        self.busy = True
    def runAndWait(self):
        self.busy = False
    def setProperty(self, *args, **kwargs):
        pass
    def getProperty(self, name):
        if name == 'voices':
            return self.voices
    def isBusy(self):
        return self.busy
    def stop(self):
        self.stopped = True
        self.busy = False

class DummyRecognizer:
    pass

class DummyUser:
    rol = 'usuario'


def test_hablar_detiene_si_ocupado(monkeypatch):
    engine = DummyEngine()
    monkeypatch.setattr('services.asistente_voz.pyttsx3.init', lambda: engine)
    monkeypatch.setattr('services.asistente_voz.sr.Recognizer', lambda: DummyRecognizer())
    voz = ServicioVoz(DummyUser())
    engine.busy = True
    voz.hablar('hola')
    assert engine.stopped
    assert engine.last_said == 'hola'


def test_cambiar_voz_indice_invalido(monkeypatch):
    engine = DummyEngine()
    monkeypatch.setattr('services.asistente_voz.pyttsx3.init', lambda: engine)
    monkeypatch.setattr('services.asistente_voz.sr.Recognizer', lambda: DummyRecognizer())
    voz = ServicioVoz(DummyUser())
    resultado = voz.cambiar_voz(5)
    assert resultado.startswith('❌')
    assert voz.voz_actual is None
class DummyAdmin:
    rol = 'admin'


def test_cambiar_voz_con_admin(monkeypatch):
    engine = DummyEngine()
    monkeypatch.setattr('services.asistente_voz.pyttsx3.init', lambda: engine)
    monkeypatch.setattr('services.asistente_voz.sr.Recognizer', lambda: DummyRecognizer())
    user = SimpleNamespace(rol='guest')
    voz = ServicioVoz(user, verificar_admin_callback=lambda c, p: DummyAdmin())
    monkeypatch.setattr('builtins.input', lambda _: 'dummy')
    resultado = voz.cambiar_voz(0)
    assert resultado.startswith('✔')
    assert voz.voz_actual == '1'

def test_cambiar_voz_detiene_engine(monkeypatch):
    engine = DummyEngine()
    engine.busy = True
    monkeypatch.setattr('services.asistente_voz.pyttsx3.init', lambda: engine)
    monkeypatch.setattr('services.asistente_voz.sr.Recognizer', lambda: DummyRecognizer())
    voz = ServicioVoz(DummyUser())
    resultado = voz.cambiar_voz(0)
    assert resultado.startswith('✔')
    assert engine.stopped
