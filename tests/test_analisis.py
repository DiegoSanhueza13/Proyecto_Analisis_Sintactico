"""Oráculos pequeños resueltos a mano y resultados de la gramática candidata."""
import copy
import csv
import json
import tempfile
import unittest
from pathlib import Path
from src.analisis_gramatica import (validar_gramatica, primero_secuencia,
                                   calcular_first, calcular_follow, construir_tabla)
from src.contratos import EPSILON as E, FIN
from src.exportar_analisis import exportar
from src.gramatica import GRAMATICA, INICIAL, TERMINALES


def analizar(g, inicial='S'):
    first = calcular_first(g)
    follow = calcular_follow(g, inicial, first)
    tabla, conflictos = construir_tabla(g, first, follow)
    return first, follow, tabla, conflictos


class ConjuntosTests(unittest.TestCase):
    def test_terminal_y_epsilon(self):
        f, fo, t, c = analizar({'S': [('a',), ()]})
        self.assertEqual(f, {'S': {'a', E}})
        self.assertEqual(fo, {'S': {FIN}})
        self.assertEqual(t, {('S', 'a'): [('a',)], ('S', FIN): [()]})
        self.assertFalse(c)

    def test_secuencia_vacia_y_prefijo_anulable(self):
        f = {'A': {'a', E}, 'B': {'b', E}}
        self.assertEqual(primero_secuencia((), f), {E})
        self.assertEqual(primero_secuencia(('A', 'B', 'c'), f), {'a', 'b', 'c'})
        self.assertEqual(primero_secuencia(('A', 'B'), f), {'a', 'b', E})

    def test_cadena_anulable(self):
        g = {'S': [('A', 'B')], 'A': [('a',), ()], 'B': [('b',), ()]}
        f, fo, _, c = analizar(g)
        self.assertEqual(f, {'S': {'a', 'b', E}, 'A': {'a', E}, 'B': {'b', E}})
        self.assertEqual(fo, {'S': {FIN}, 'A': {'b', FIN}, 'B': {FIN}})
        self.assertFalse(c)

    def test_propagacion_con_orden_inverso(self):
        g = {'C': [('c',)], 'B': [('C',)], 'A': [('B',)], 'S': [('A',)]}
        f, fo, _, _ = analizar(g)
        self.assertTrue(all(v == {'c'} for v in f.values()))
        self.assertTrue(all(v == {FIN} for v in fo.values()))

    def test_follow_inicial_tambien_en_lado_derecho(self):
        _, fo, _, _ = analizar({'S': [('a', 'S', 'b'), ()]})
        self.assertEqual(fo['S'], {'b', FIN})

    def test_recursion_sin_cadena_terminal(self):
        f, fo, tabla, _ = analizar({'S': [('A',)], 'A': [('S',)]})
        self.assertEqual(f, {'S': set(), 'A': set()})
        self.assertEqual(fo, {'S': {FIN}, 'A': {FIN}})
        self.assertEqual(tabla, {})

    def test_no_muta_gramatica_ni_conjuntos(self):
        g = {'S': [('A', 'b')], 'A': [('a',), ()]}
        original = copy.deepcopy(g)
        f = calcular_first(g)
        copia = copy.deepcopy(f)
        fo = calcular_follow(g, 'S', f)
        copia_fo = copy.deepcopy(fo)
        construir_tabla(g, f, fo)
        self.assertEqual(g, original)
        self.assertEqual(f, copia)
        self.assertEqual(fo, copia_fo)


class ConflictosTests(unittest.TestCase):
    def test_first_first_conserva_alternativas(self):
        _, _, tabla, conflictos = analizar({'S': [('a', 'b'), ('a', 'c')]})
        self.assertEqual(tabla['S', 'a'], [('a', 'b'), ('a', 'c')])
        self.assertEqual(len(conflictos), 1)
        self.assertEqual((conflictos[0].no_terminal, conflictos[0].token), ('S', 'a'))
        self.assertTrue(all(a.origenes == ('FIRST',) for a in conflictos[0].alternativas))

    def test_first_follow(self):
        _, _, tabla, conflictos = analizar({'S': [('A', 'a')], 'A': [('a',), ()]})
        self.assertEqual(tabla['A', 'a'], [(), ('a',)])
        self.assertEqual({a.produccion: a.origenes for a in conflictos[0].alternativas},
                         {(): ('FOLLOW',), ('a',): ('FIRST',)})

    def test_dos_alternativas_anulables(self):
        _, _, t, c = analizar({'S': [('A',), ('B',)], 'A': [()], 'B': [()]})
        self.assertEqual(len(t['S', FIN]), 2)
        self.assertTrue(all(a.origenes == ('FOLLOW',) for a in c[0].alternativas))

    def test_produccion_duplicada_no_es_conflicto(self):
        _, _, t, c = analizar({'S': [('a',), ('a',)]})
        self.assertEqual(t['S', 'a'], [('a',)])
        self.assertFalse(c)


class ValidacionTests(unittest.TestCase):
    def test_gramaticas_invalidas(self):
        casos = [{}, {'S': []}, {'': [()]}, {'S': [('ε',)]},
                 {'S': [('$',)]}, {'S': ['a']}, {'S': [('',)]}, {'S': [('a b',)]}]
        for g in casos:
            with self.subTest(g=g), self.assertRaises(ValueError):
                calcular_first(g)

    def test_inicial_inexistente(self):
        with self.assertRaises(ValueError):
            calcular_follow({'S': [('a',)]}, 'X', {'S': {'a'}})

    def test_conjuntos_incompatibles(self):
        g = {'S': [('a',)]}
        for first in [{}, {'S': {'z'}}, {'S': ['a']}]:
            with self.subTest(first=first), self.assertRaises(ValueError):
                calcular_follow(g, 'S', first)
        with self.assertRaises(ValueError):
            construir_tabla(g, {'S': {'a'}}, {'S': {E}})

    def test_vocabulario_detecta_errata(self):
        with self.assertRaises(ValueError):
            validar_gramatica({'S': [('ExprMalEscrita',)]}, 'S', {'ID'})


class AgricolaTests(unittest.TestCase):
    def test_vocabulario_coincide_con_contrato(self):
        self.assertEqual(validar_gramatica(GRAMATICA, INICIAL, TERMINALES), TERMINALES)

    def test_first_completos(self):
        self.assertEqual(calcular_first(GRAMATICA), {
            'Programa': {'WHEN'}, 'Resto': {'WHEN', E}, 'Regla': {'WHEN'},
            'Expr': {'NOT', '(', 'ID'}, 'ColaOr': {'OR', E},
            'Termino': {'NOT', '(', 'ID'}, 'ColaAnd': {'AND', E},
            'Factor': {'NOT', '(', 'ID'}, 'Comparacion': {'ID'},
            'Valor': {'NUM', 'TRUE', 'FALSE'},
            'Accion': {'ACTIVAR', 'DESACTIVAR', 'REGAR'}, 'MasAcciones': {'Y', E},
        })

    def test_follow_completos(self):
        f = calcular_first(GRAMATICA)
        self.assertEqual(calcular_follow(GRAMATICA, INICIAL, f), {
            'Programa': {FIN}, 'Resto': {FIN}, 'Regla': {FIN, 'WHEN'},
            'Expr': {'THEN', ')'}, 'ColaOr': {'THEN', ')'},
            'Termino': {'OR', 'THEN', ')'}, 'ColaAnd': {'OR', 'THEN', ')'},
            'Factor': {'AND', 'OR', 'THEN', ')'},
            'Comparacion': {'AND', 'OR', 'THEN', ')'},
            'Valor': {'AND', 'OR', 'THEN', ')'},
            'Accion': {'Y', ';'}, 'MasAcciones': {';'},
        })

    def test_celdas_predictivas_y_ausencia_de_conflictos(self):
        _, _, t, c = analizar(GRAMATICA, INICIAL)
        self.assertFalse(c)
        self.assertEqual(t['Factor', 'ID'], [('Comparacion',)])
        self.assertEqual(t['ColaAnd', 'OR'], [()])
        self.assertEqual(t['MasAcciones', ';'], [()])
        self.assertNotIn(('Programa', FIN), t)  # No acepta programa vacío.
        self.assertNotIn(('Valor', 'ID'), t)


class ExportacionTests(unittest.TestCase):
    def test_exportacion_determinista_y_legible(self):
        with tempfile.TemporaryDirectory() as carpeta:
            exportar(GRAMATICA, INICIAL, carpeta)
            p = Path(carpeta)
            originales = {f.name: f.read_bytes() for f in p.iterdir()}
            exportar(GRAMATICA, INICIAL, carpeta)
            self.assertEqual(originales, {f.name: f.read_bytes() for f in p.iterdir()})
            datos = json.loads((p / 'first_follow.json').read_text(encoding='utf-8'))
            self.assertEqual(datos['FIRST']['Programa'], ['WHEN'])
            self.assertEqual(json.loads((p / 'conflictos.json').read_text()), [])
            with (p / 'tabla_ll1.csv').open(encoding='utf-8', newline='') as f:
                filas = list(csv.DictReader(f))
            self.assertTrue(any(r['no_terminal'] == 'Resto' and r['token'] == FIN
                                and r['produccion'] == E for r in filas))

    def test_exportacion_no_oculta_conflictos(self):
        with tempfile.TemporaryDirectory() as carpeta:
            conflictos = exportar({'S': [('a',), ('a', 'b')]}, 'S', carpeta)
            self.assertEqual(len(conflictos), 1)
            datos = json.loads((Path(carpeta) / 'conflictos.json').read_text())
            self.assertEqual(len(datos[0]['alternativas']), 2)


if __name__ == '__main__':
    unittest.main()
