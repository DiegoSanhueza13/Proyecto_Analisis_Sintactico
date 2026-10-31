"""Regresiones de integración: archivos reales, CLI, errores y listas largas."""
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from src.agro import tokenizar
from src.arbol import a_texto
from src.contratos import Token
from src.main import analizar_texto
from src.parser import Parser

RAIZ = Path(__file__).resolve().parents[1]


def cli(*args):
    return subprocess.run([sys.executable, '-m', 'src.main', *map(str, args)],
                          cwd=RAIZ, capture_output=True, encoding='utf-8', timeout=20)


class IntegracionTests(unittest.TestCase):
    def test_fin_interno_no_puede_ocultar_tokens(self):
        tokens = tokenizar('WHEN a < 1 THEN ACTIVAR b;')
        corruptos = tokens[:-1] + [tokens[-1], Token('ID', 'sobrante', 1, 40), tokens[-1]]
        with self.assertRaises(ValueError):
            Parser(corruptos)

    def test_contrato_de_tokens_invalido(self):
        for tokens in [[], ['no soy un token'], [Token('ID', 'x', 1, 1)],
                       [Token('$', 'texto', 1, 1)]]:
            with self.subTest(tokens=tokens), self.assertRaises(ValueError):
                Parser(tokens)

    def test_cola_or_larga_y_renderizado(self):
        texto = 'WHEN ' + ' OR '.join(['a < 1'] * 1100) + ' THEN ACTIVAR b;'
        ast = analizar_texto(texto)
        self.assertEqual(a_texto(ast).count('OR'), 1099)

    def test_cola_and_larga_y_asociacion(self):
        ast = analizar_texto('WHEN ' + ' AND '.join(['a < 1'] * 1100) + ' THEN ACTIVAR b;')
        actual, cantidad = ast.hijos[0].hijos[0], 0
        while actual.etiqueta == 'AND':
            cantidad += 1
            self.assertEqual(actual.hijos[1].etiqueta, '<')
            actual = actual.hijos[0]
        self.assertEqual(cantidad, 1099)

    def test_cli_archivo_valido_y_tokens(self):
        r = cli(RAIZ / 'ejemplos/validos/01_activar.txt', '--tokens')
        self.assertEqual(r.returncode, 0, r.stderr)
        self.assertIn('Programa válido.', r.stdout)
        self.assertIn('└──', r.stdout)
        self.assertIn('WHEN', r.stdout)

    def test_cli_archivo_invalido(self):
        r = cli(RAIZ / 'ejemplos/invalidos/01_falta_then.txt')
        self.assertEqual(r.returncode, 1)
        self.assertIn('Error sintáctico [1:19]', r.stderr)
        self.assertNotIn('Traceback', r.stderr)

    def test_cli_archivo_inexistente(self):
        r = cli(RAIZ / 'ejemplos/archivo_que_no_existe.txt')
        self.assertEqual(r.returncode, 1)
        self.assertIn('No se pudo leer', r.stderr)

    def test_cli_utf8_bom_y_utf8_invalido(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p = Path(carpeta) / 'entrada.txt'
            p.write_text('WHEN h < 1 THEN ACTIVAR b;', encoding='utf-8-sig')
            self.assertEqual(cli(p).returncode, 0)
            p.write_bytes(b'\xff\xfe\x80')
            r = cli(p)
            self.assertEqual(r.returncode, 1)
            self.assertNotIn('Traceback', r.stderr)

    def test_cli_limite_de_anidamiento(self):
        with tempfile.TemporaryDirectory() as carpeta:
            p = Path(carpeta) / 'anidado.txt'
            p.write_text('WHEN ' + '(' * 1500 + 'h < 1' + ')' * 1500 + ' THEN ACTIVAR b;')
            r = cli(p)
            self.assertEqual(r.returncode, 1)
            self.assertIn('anidadas', r.stderr)
            self.assertNotIn('Traceback', r.stderr)


if __name__ == '__main__':
    unittest.main()
