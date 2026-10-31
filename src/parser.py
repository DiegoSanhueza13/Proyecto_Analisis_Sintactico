"""parser predictivo de descenso recursivo para la gramatica
Una funcion por no terminal; la decicion se toma con el tipo de token actual,
de acuerdo a la tabla ll(1) de la seccion 6.
Las producciones ε no consumen tokens. Cada función devuelve su nodo del AST."""

from .arbol import Nodo
from .contratos import ErrorSintactico, Token

class Parser:
    def __init__(self, tokens: list[Token]):
        if (not isinstance(tokens, list) or not tokens
                or not all(isinstance(t, Token) for t in tokens)
                or tokens[-1].tipo != '$' or tokens[-1].lexema != ''
                or sum(t.tipo == '$' for t in tokens) != 1):
            raise ValueError("Se requiere una lista de Token con un único fin '$', de lexema vacío, al final.")
        self.tokens = list(tokens)
        self.pos = 0
    # Utilidades
    def actual(self) -> Token:
        return self.tokens[self.pos]

    def tipo(self) -> str:
        return self.tokens[self.pos].tipo

    def _encontrado(self, tok:Token) -> str:
        return 'el fin de la entrada' if tok.tipo == '$' else f"'{tok.lexema}'"

    def error(self, esperado: str):
        tok = self.actual()
        raise ErrorSintactico(f'se esperaba {esperado} y se encontró {self._encontrado(tok)}',
                              tok.linea, tok.columna)
    def consumir(self, esperado: str) -> Token:
        if self.tipo() != esperado:
            self.error(esperado)
        tok = self.actual()
        self.pos += 1
        return tok

    # punto de entrada
    def analizar(self) -> Nodo:
        arbol= self.programa()
        self.consumir('$') # si sobra algo, se informa aquí
        return arbol
    # no terminales
    def programa(self) -> Nodo:     # Programa → Regla Resto

        reglas = [self.regla()]
        reglas += self.resto()
        return Nodo('Programa', reglas)

    def resto(self) -> list[Nodo]:    # Resto → Regla Resto | ε

        reglas = []
        while self.tipo() == 'WHEN':
            reglas.append(self.regla())
        return reglas # ε: token en FOLLOW(Resto) = {$}

    def regla(self) -> Nodo:        # Regla → WHEN Expr THEN Accion MasAcciones ;
        self.consumir('WHEN')
        condicion = self.expr()
        self.consumir('THEN')
        acciones = [self.accion()]
        acciones += self.mas_acciones()
        self.consumir(';')
        return Nodo('Regla', [condicion, Nodo('Acciones', acciones)])

    def expr(self) -> Nodo:         # Expr → Termino ColaOr
        return self.cola_or(self.termino())

    def cola_or(self, izq: Nodo) -> Nodo:  # ColaOr → OR Termino ColaOr | ε

        while self.tipo() == 'OR':
            self.consumir('OR')
            der = self.termino()
            izq = Nodo('OR', [izq, der])
        return izq # # ε: token en {THEN, )}

    def termino(self) -> Nodo:      # Termino → Factor ColaAnd
        
        return self.cola_and(self.factor())

    def cola_and(self, izq: Nodo) -> Nodo:  # ColaAnd → AND Factor ColaAnd | ε
        
        while self.tipo() == 'AND':
            self.consumir('AND')
            der = self.factor()
            izq = Nodo('AND', [izq, der])
        return izq #ε: token en {OR, THEN, )}

    def factor(self) -> Nodo:       # Factor → NOT Factor | ( Expr ) | Comparacion
        t = self.tipo()
        if t == 'NOT':
            self.consumir('NOT')
            return Nodo('NOT', [self.factor()])
        if t == '(':
            self.consumir('(')
            interno = self.expr()
            self.consumir(')')
            return interno  #parentesis no genran nodoss
        if t == 'ID':
            return self.comparacion()
        self.error('una condición (NOT, "(" o un identificador)')

    def comparacion(self) -> Nodo:   # Comparacion → ID REL Valor
        sensor = self.consumir('ID')
        rel= self.consumir('REL')
        if self.tipo() not in ('NUM', 'TRUE', 'FALSE'):
            self.error(f'un valor (NUM, TRUE o FALSE) después del operador {rel.lexema}')
        valor = self.valor()
        return Nodo(rel.lexema, [Nodo(sensor.lexema), valor])

    def valor(self) -> Nodo:         # Valor → NUM | TRUE | FALSE 
        t = self.tipo()
        if t in ('NUM', 'TRUE', 'FALSE'):
            return Nodo(self.consumir(t).lexema)
        self.error('un valor (NUM, TRUE o FALSE)')

    def accion(self) -> Nodo:       # Accion → ACTIVAR ID | DESACTIVAR ID | REGAR ID POR NUM MIN
        t = self.tipo()
        if t in ('ACTIVAR', 'DESACTIVAR'):
            verbo = self.consumir(t)
            destino = self.consumir('ID')
            return Nodo(f'{verbo.lexema.upper()} {destino.lexema}')
        if t == 'REGAR':
            self.consumir('REGAR')
            destino = self.consumir('ID')
            self.consumir('POR')
            duracion = self.consumir('NUM')
            self.consumir('MIN')
            return Nodo(f'REGAR {destino.lexema} ({duracion.lexema} MIN)')
        self.error('una acción (ACTIVAR, DESACTIVAR o REGAR)')

    def mas_acciones(self) -> list[Nodo]:  # MasAcciones → Y Accion MasAcciones | ε
        acciones = []
        while self.tipo() == 'Y':
            self.consumir('Y')
            acciones.append(self.accion())
        return acciones # ε: token en FOLLOW(MasAcciones) = {;}
