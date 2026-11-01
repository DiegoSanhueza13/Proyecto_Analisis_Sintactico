"""Analizador léxico del lenguaje de automatización agrícola.

Adapta el analizador léxico básico entregado por el docente
(anlizador_lexico1.ipynb):
    - Usa expresiones regulares con nombre para cada categoría de token.
    - Reconoce primero el identificador y luego comprueba si es una palabra
      reservada, para que las reservadas no se confundan con identificadores.
    - Cada Token guarda tipo, lexema, línea y columna (desde 1).
    - Al final agrega el marcador de fin de entrada Token('$', '', línea, columna).
"""



import re
from .contratos import ErrorLexico, FIN ,Token

RESERVADAS = frozenset(['WHEN', 'THEN', 'AND','OR','NOT','TRUE','FALSE'
                        ,'ACTIVAR','DESACTIVAR','REGAR','POR','MIN','Y'])

# Los comparadores de dos caracteres van antes que los de uno.

ESPECIFICACION =[
    ('NUM', r'[0-9]+'),
    ('REL', r'>=|<=|==|!=|>|<'),
    ('(', r'\('),
    (')',r'\)'),
    (';', r';'),
    ('ID', r'[a-zA-Z_][a-zA-Z0-9_]*'),
    ('ESPACIO', r'[ \t\r\n]+'),
    ('ERROR', r'.'),
]

PATRON = re.compile('|'.join(f'(?P<G{i}>{e})' for i, (_, e) in enumerate(ESPECIFICACION)))
NOMBRES = {f'G{i}': nombre for i, (nombre, _) in enumerate(ESPECIFICACION)}

def tokenizar(texto: str) -> list[Token]:
    """Convierte un texto en tokens. Lanza ErrorLexico ante un símbolo no reconocido."""
    tokens = []
    linea, inicio_linea= 1, 0
    for m in PATRON.finditer(texto):
        tipo = NOMBRES[m.lastgroup]
        lexema = m.group()
        columna = m.start() - inicio_linea + 1
        if tipo == 'ESPACIO':
            saltos = lexema.count('\n')
            if saltos:
                linea += saltos
                inicio_linea = m.start() + lexema.rindex('\n') + 1
            continue
        if tipo == 'ERROR':
            raise ErrorLexico(f"símbolo no reconocido: '{lexema}'", linea, columna)
        if tipo == 'ID' and lexema.upper() in RESERVADAS:
            tipo = lexema.upper()
        tokens.append(Token(tipo, lexema, linea, columna))
    columna_fin= len(texto) - inicio_linea + 1
    tokens.append(Token(FIN, '', linea, columna_fin))
    return tokens
