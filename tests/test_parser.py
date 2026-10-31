"""Casos de prueba de entradas: 10 válidas, 10 inválidas y 5 límite, más el AST."""
import unittest
from src.agro import tokenizar
from src.arbol import a_texto
from src.contratos import ErrorLexico, ErrorSintactico
from src.parser import Parser
 
 
def analizar(texto):
    return Parser(tokenizar(texto)).analizar()
 
 
VALIDAS = [
    "WHEN humedad < 30 THEN ACTIVAR bomba;",
    "WHEN humedad >= 70 THEN DESACTIVAR bomba;",
    "WHEN lluvia == FALSE THEN REGAR norte POR 15 MIN;",
    "WHEN humedad < 30 AND temperatura > 20 THEN ACTIVAR bomba;",
    "WHEN NOT (lluvia == TRUE OR humedad >= 60) THEN REGAR norte POR 10 MIN Y ACTIVAR bomba;",
    "WHEN humedad < 30 THEN ACTIVAR bomba;\nWHEN humedad >= 70 THEN DESACTIVAR bomba;",
    "WHEN a == 1 OR b == 2 OR c == 3 THEN ACTIVAR bomba;",
    "WHEN a == 1 OR b == 2 AND c == 3 THEN ACTIVAR bomba;",
    "WHEN NOT NOT lluvia == TRUE THEN DESACTIVAR bomba;",
    "WHEN (a < 1 OR (b > 2 AND c != 3)) THEN ACTIVAR x Y DESACTIVAR ventilador Y REGAR z POR 5 MIN;",
]
 
# (entrada, línea, columna, fragmento esperado del mensaje)
INVALIDAS = [
    ("WHEN humedad < 30 ACTIVAR bomba;", 1, 19, "se esperaba THEN"),
    ("WHEN humedad < THEN ACTIVAR bomba;", 1, 16, "un valor (NUM, TRUE o FALSE) después del operador <"),
    ("WHEN humedad < 30 THEN ACTIVAR bomba", 1, 37, "se esperaba ;"),
    ("WHEN (humedad < 30 THEN ACTIVAR bomba;", 1, 20, "se esperaba )"),
    ("WHEN humedad < 30 THEN REGAR norte 10 MIN;", 1, 36, "se esperaba POR"),
    ("WHEN humedad < 30 THEN REGAR norte POR 10;", 1, 42, "se esperaba MIN"),
    ("WHEN humedad < limite THEN ACTIVAR bomba;", 1, 16, "un valor (NUM, TRUE o FALSE)"),
    ("WHEN TRUE THEN ACTIVAR bomba;", 1, 6, "una condición"),
    ("WHEN humedad < 30 THEN ACTIVAR;", 1, 31, "se esperaba ID"),
    ("WHEN humedad < 30 THEN ACTIVAR bomba Y;", 1, 39, "una acción"),
]
 
 
class ValidasTests(unittest.TestCase):
    def test_diez_entradas_validas(self):
        for texto in VALIDAS:
            with self.subTest(texto=texto):
                self.assertEqual(analizar(texto).etiqueta, 'Programa')
 
 
class InvalidasTests(unittest.TestCase):
    def test_diez_entradas_invalidas_con_ubicacion(self):
        for texto, linea, columna, fragmento in INVALIDAS:
            with self.subTest(texto=texto):
                with self.assertRaises(ErrorSintactico) as ctx:
                    analizar(texto)
                self.assertIn(fragmento, ctx.exception.mensaje)
                self.assertEqual((ctx.exception.linea, ctx.exception.columna), (linea, columna))
 
 
class LimiteTests(unittest.TestCase):
    def test_programa_vacio_se_rechaza(self):
        for texto in ("", "   \n  "):
            with self.subTest(texto=texto), self.assertRaises(ErrorSintactico) as ctx:
                analizar(texto)
            self.assertIn("se esperaba WHEN", ctx.exception.mensaje)
 
    def test_reservadas_en_minusculas(self):
        self.assertEqual(analizar("when humedad < 30 then activar bomba;").etiqueta, 'Programa')
 
    def test_error_lexico_con_ubicacion(self):
        with self.assertRaises(ErrorLexico) as ctx:
            tokenizar("WHEN humedad < 30 THEN ACTIVAR bomba;\nWHEN a @ 3 THEN ACTIVAR b;")
        self.assertEqual((ctx.exception.linea, ctx.exception.columna), (2, 8))
 
    def test_error_en_segunda_linea(self):
        with self.assertRaises(ErrorSintactico) as ctx:
            analizar("WHEN a < 1 THEN ACTIVAR b;\nWHEN a < 1 ACTIVAR b;")
        self.assertEqual((ctx.exception.linea, ctx.exception.columna), (2, 12))
 
    def test_texto_sobrante_tras_el_programa(self):
        with self.assertRaises(ErrorSintactico) as ctx:
            analizar("WHEN a < 1 THEN ACTIVAR b; basura")
        self.assertIn("se esperaba $", ctx.exception.mensaje)
 
 
class ArbolTests(unittest.TestCase):
    def test_ast_de_la_sentencia_5(self):
        esperado = "\n".join([
            "Programa",
            "└── Regla",
            "    ├── NOT",
            "    │   └── OR",
            "    │       ├── ==",
            "    │       │   ├── lluvia",
            "    │       │   └── TRUE",
            "    │       └── >=",
            "    │           ├── humedad",
            "    │           └── 60",
            "    └── Acciones",
            "        ├── REGAR norte (10 MIN)",
            "        └── ACTIVAR bomba",
        ])
        self.assertEqual(a_texto(analizar(VALIDAS[4])), esperado)
 
    def test_and_tiene_mayor_precedencia_que_or(self):
        arbol = analizar("WHEN a == 1 OR b == 2 AND c == 3 THEN ACTIVAR x;")
        cond = arbol.hijos[0].hijos[0]
        self.assertEqual(cond.etiqueta, 'OR')
        self.assertEqual(cond.hijos[1].etiqueta, 'AND')
 
    def test_asociacion_a_la_izquierda(self):
        arbol = analizar("WHEN a == 1 OR b == 2 OR c == 3 THEN ACTIVAR x;")
        cond = arbol.hijos[0].hijos[0]
        self.assertEqual(cond.etiqueta, 'OR')
        self.assertEqual(cond.hijos[0].etiqueta, 'OR')       # (a OR b) OR c
        self.assertEqual(cond.hijos[1].etiqueta, '==')
 
    def test_varias_reglas(self):
        self.assertEqual(len(analizar(VALIDAS[5]).hijos), 2)
 
 
if __name__ == '__main__':
    unittest.main()