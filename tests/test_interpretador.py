import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))
from services.interpretador import interpretar

class TestInterpretador(unittest.TestCase):
    def test_numeros(self):
        self.assertEqual(interpretar('1')[0], 'fecha_hora')
        self.assertEqual(interpretar('dos')[0], 'abrir_con_opcion')
        self.assertEqual(interpretar('9')[0], 'salir')
        self.assertEqual(interpretar('seis')[0], 'modo_admin')

    def test_palabras_clave(self):
        self.assertEqual(interpretar('abre una carpeta')[0], 'abrir_con_opcion')
        self.assertEqual(interpretar('quiero un dato curioso')[0], 'dato_curioso')
        self.assertEqual(interpretar('cerrar sesion')[0], 'cerrar_sesion')

    def test_desconocido(self):
        self.assertEqual(interpretar('xyz')[0], 'comando_no_reconocido')

if __name__ == '__main__':
    unittest.main()
