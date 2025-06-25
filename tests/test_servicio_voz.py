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
