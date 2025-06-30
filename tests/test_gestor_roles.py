import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))

from services.gestor_roles import GestorRoles
from utils import helpers


def crear_archivo_usuarios(tmp_path):
    datos = {
        "usuarios": [
            {
                "cif": "1111",
                "nombre": "User1",
                "rol": "admin",
                "contrasena": helpers.hash_password("pass1"),
                "pregunta": "Color?",
                "respuesta": helpers.hash_password("verde"),
            }
        ]
    }
    ruta = tmp_path / "usuarios.json"
    ruta.write_text(json.dumps(datos), encoding="utf-8")
    return ruta


def test_autenticar_ok(tmp_path):
    ruta = crear_archivo_usuarios(tmp_path)
    gr = GestorRoles(ruta)
    usuario = gr.autenticar("1111", "pass1")
    assert usuario is not None
    assert usuario.nombre == "User1"


def test_autenticar_falla(tmp_path):
    ruta = crear_archivo_usuarios(tmp_path)
    gr = GestorRoles(ruta)
    assert gr.autenticar("1111", "no") is None


def test_registrar_usuario(monkeypatch, tmp_path):
    ruta = crear_archivo_usuarios(tmp_path)
    gr = GestorRoles(ruta)

    monkeypatch.setattr(helpers, "generar_cif", lambda existentes=None: "2222")
    monkeypatch.setattr(helpers, "generar_contrasena", lambda longitud=8: "pass2")

    cif, contrasena = gr.registrar_usuario("User2", "usuario")
    assert cif == "2222"
    assert contrasena == "pass2"
    nuevo = gr.obtener_usuario_por_cif("2222")
    assert nuevo.nombre == "User2"


def test_restablecer_contrasena_ok(tmp_path):
    ruta = crear_archivo_usuarios(tmp_path)
    gr = GestorRoles(ruta)
    nueva = gr.restablecer_contrasena("1111", "verde")
    assert nueva is not None
    usuario = gr.obtener_usuario_por_cif("1111")
    assert usuario.verificar_contrasena(nueva)


def test_restablecer_contrasena_falla(tmp_path):
    ruta = crear_archivo_usuarios(tmp_path)
    gr = GestorRoles(ruta)
    assert gr.restablecer_contrasena("1111", "azul") is None
