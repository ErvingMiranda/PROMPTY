import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_2.5'))

from services.permisos import Permisos


def test_permisos_basicos():
    p = Permisos()
    assert p.tiene_permiso('admin', 'editar_voz')
    assert not p.tiene_permiso('usuario', 'editar_voz')
    assert 'agregar_comando' in p.listar_permisos('admin')
