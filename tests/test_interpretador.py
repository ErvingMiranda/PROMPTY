import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'PROMPTY_3.0'))
from services.interpretador import interpretar


class TestInterpretador(unittest.TestCase):
    def test_numeros(self):
        self.assertEqual(interpretar('1')[0], 'fecha_hora')
        self.assertEqual(interpretar('dos')[0], 'abrir_con_opcion')
        self.assertEqual(interpretar('10')[0], 'salir')
        self.assertEqual(interpretar('siete')[0], 'modo_admin')

    def test_palabras_clave(self):
        self.assertEqual(interpretar('abre una carpeta')[0], 'abrir_carpeta')
        self.assertEqual(interpretar('abre un archivo')[0], 'abrir_archivo')
        self.assertEqual(interpretar('quiero un dato curioso')[0], 'dato_curioso')
        self.assertEqual(interpretar('cerrar sesion')[0], 'cerrar_sesion')

    def test_busquedas(self):
        self.assertEqual(interpretar('buscar receta en youtube')[0], 'buscar_en_youtube')
        self.assertEqual(interpretar('buscar fotos en google')[0], 'buscar_en_navegador')
        self.assertEqual(interpretar('buscar un archivo')[0], 'buscar_general')
        self.assertEqual(interpretar('escuchar musica')[0], 'reproducir_musica')
        self.assertEqual(interpretar('poner cancion')[0], 'reproducir_musica')
        self.assertEqual(interpretar('oir canciones')[0], 'reproducir_musica')

    def test_admin_frase(self):
        resultado = interpretar('abre las funciones de administrador')[0]
        self.assertEqual(resultado, 'modo_admin')

    def test_admin_solo(self):
        self.assertEqual(interpretar('admin')[0], 'modo_admin')
        self.assertEqual(interpretar('administrador')[0], 'modo_admin')

    def test_arbol(self):
        self.assertEqual(interpretar('tree')[0], 'ver_arbol')
        self.assertEqual(interpretar('árbol')[0], 'ver_arbol')
        self.assertEqual(interpretar('estructura del proyecto')[0], 'ver_arbol')

    def test_saludos(self):
        self.assertEqual(interpretar('hola')[0], 'saludo')
        self.assertEqual(interpretar('hola prompty')[0], 'saludo')
        self.assertNotEqual(interpretar('hola quiero buscar un video')[0], 'saludo')

    def test_sinonimos(self):
        self.assertEqual(interpretar('abre el folder')[0], 'abrir_carpeta')
        self.assertEqual(interpretar('abre un documento')[0], 'abrir_archivo')
        self.assertEqual(interpretar('exit')[0], 'salir')

    def test_fechas_horas(self):
        self.assertEqual(interpretar('fecha y hora')[0], 'fecha_hora')
        self.assertEqual(interpretar('que hora es')[0], 'hora')
        self.assertEqual(interpretar('cual es la fecha')[0], 'fecha')
        self.assertEqual(interpretar('que dia es hoy')[0], 'dia_fecha')

    def test_desconocido(self):
        self.assertEqual(interpretar('xyz')[0], 'comando_no_reconocido')

if __name__ == '__main__':
    unittest.main()
