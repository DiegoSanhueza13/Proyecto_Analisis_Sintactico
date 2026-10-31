'''Analizador lexico del lenguaje de automatizacion agricola.
adapta el analizdor lexico basico entregado(analizador_lexico.py):
    expreciones regulares con nombres para los tokens del lenguaje de automatizacion agricola
    identificadores primero y luego verificar las palabras reservadas, para que no se confundan con los identificadores.
    Cada token guarda un tipo, lexema, linia y columna. Al final se agrega un token('$', '',1,c) '''



import re
from .contratos import ErrorLexico, FIN ,Token

RESERVADAS = frozenset(['WHEN', 'THEN', 'AND','OR','NOT','TRUE','FALSE'
                        ,'ACTIVAR','DESACTIVAR','REGAR','POR','MIN','Y'])

#los comparadores de dos caracteres van antes que los de uno.

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
    'convertir un texto en  tokens, Lanza ErrorLexico si encuentra un token inesperado'
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
            raise ErrorLexico(f"simbolo no reconocido:'{lexema}'", linea, columna)
        if tipo == 'ID' and lexema.upper() in RESERVADAS:
            tipo = lexema.upper()
        tokens.append(Token(tipo, lexema, linea, columna))
    columna_fin= len(texto) - inicio_linea + 1
    tokens.append(Token(FIN, '', linea, columna_fin))
    return tokens
