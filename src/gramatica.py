"""Gramática candidata basada en la especificación del informe, secciones 1–2.

Propuesta para revisión del grupo, sin nombre de proyecto acordado.
Una regla tiene al menos una acción y un programa al menos una regla.
NOT tiene mayor precedencia que AND, y AND mayor que OR. Los paréntesis
cambian la agrupación. El futuro AST plegará AND/OR a la izquierda.
REGAR incorpora duración obligatoria; Y permite múltiples acciones.
"""
from .contratos import Gramatica

INICIAL = 'Programa'
GRAMATICA: Gramatica = {
    'Programa': [('Regla', 'Resto')],
    'Resto': [('Regla', 'Resto'), ()],
    'Regla': [('WHEN', 'Expr', 'THEN', 'Accion', 'MasAcciones', ';')],
    'Expr': [('Termino', 'ColaOr')],
    'ColaOr': [('OR', 'Termino', 'ColaOr'), ()],
    'Termino': [('Factor', 'ColaAnd')],
    'ColaAnd': [('AND', 'Factor', 'ColaAnd'), ()],
    'Factor': [('NOT', 'Factor'), ('(', 'Expr', ')'), ('Comparacion',)],
    'Comparacion': [('ID', 'REL', 'Valor')],
    'Valor': [('NUM',), ('TRUE',), ('FALSE',)],
    'Accion': [('ACTIVAR', 'ID'), ('DESACTIVAR', 'ID'),
               ('REGAR', 'ID', 'POR', 'NUM', 'MIN')],
    'MasAcciones': [('Y', 'Accion', 'MasAcciones'), ()],
}

# Vocabulario del lexer propuesto. REL agrupa los seis comparadores; el lexema
# conserva el comparador concreto. TRUE/FALSE son tipos propios, no ID.
TERMINALES = frozenset({
    'WHEN', 'THEN', 'OR', 'AND', 'NOT', '(', ')', 'ID', 'REL', 'NUM',
    'TRUE', 'FALSE', 'ACTIVAR', 'DESACTIVAR', 'REGAR', 'POR', 'MIN', 'Y', ';',
})
