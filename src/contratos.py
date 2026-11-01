"""Tipos compartidos; este módulo no implementa lexer ni parser."""
from dataclasses import dataclass

EPSILON = 'ε'  # Marca en FIRST; la producción vacía se representa mediante ().
FIN = '$'      # Marcador interno de fin de entrada, nunca una producción.
Produccion = tuple[str, ...]
Gramatica = dict[str, list[Produccion]]


@dataclass(frozen=True)
class Token:
    """Posición desde 1; tipo normalizado y lexema original.

    El lexer agrega exactamente un Token('$', '', linea, columna) al final.
    Las reservadas usan su palabra en mayúsculas como tipo; los demás tipos son
    ID, NUM, REL, (, ) y ;. El parser valida este contrato al recibir los tokens.
    """
    tipo: str
    lexema: str
    linea: int
    columna: int


class ErrorLenguaje(ValueError):
    """Error léxico o sintáctico con su línea y columna (desde 1)."""
    def __init__(self, mensaje: str, linea: int, columna: int):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(f'{linea}:{columna}: {mensaje}')


class ErrorLexico(ErrorLenguaje):
    pass


class ErrorSintactico(ErrorLenguaje):
    pass
