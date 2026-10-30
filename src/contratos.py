"""Tipos compartidos; este módulo no implementa lexer ni parser."""
from dataclasses import dataclass

EPSILON = 'ε'  # Marca en FIRST; la producción vacía se representa mediante ().
FIN = '$'      # Marcador interno de fin de entrada, nunca una producción.
Produccion = tuple[str, ...]
Gramatica = dict[str, list[Produccion]]


@dataclass(frozen=True)
class Token:
    """Posición desde 1; tipo normalizado y lexema original.

    El futuro lexer debe agregar exactamente un Token('$', '', linea, columna).
    Las reservadas usan su palabra en mayúsculas como tipo; los demás tipos son
    ID, NUM, REL, (, ) y ;. Este contrato debe acordarse al integrar el parser.
    """
    tipo: str
    lexema: str
    linea: int
    columna: int


class ErrorLenguaje(ValueError):
    """Error localizado de la futura integración léxica/sintáctica."""
    def __init__(self, mensaje: str, linea: int, columna: int):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        super().__init__(f'{linea}:{columna}: {mensaje}')


class ErrorLexico(ErrorLenguaje):
    pass


class ErrorSintactico(ErrorLenguaje):
    pass
