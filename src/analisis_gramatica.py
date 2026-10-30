"""FIRST, FOLLOW y tabla LL(1) por punto fijo, sin generadores de parsers.

Los algoritmos reciben cualquier gramática según contratos.Gramatica y no
importan la gramática agrícola, el lexer ni el parser. Las claves son los no
terminales; otros símbolos son terminales. Una errata en un no terminal puede
parecer un terminal: contrastar con el vocabulario esperado al validar.
"""
from dataclasses import dataclass
from .contratos import EPSILON, FIN, Gramatica, Produccion


def validar_gramatica(g: Gramatica, inicial: str | None = None,
                      terminales_esperados: set[str] | frozenset[str] | None = None) -> set[str]:
    """Rechaza estructura inválida; devuelve los terminales observados.

    No exige ausencia de recursión ni productividad: el análisis de conjuntos
    también debe poder inspeccionar gramáticas conflictivas o no productivas.
    """
    if not isinstance(g, dict) or not g:
        raise ValueError('La gramática debe ser un diccionario no vacío.')
    def simbolo_valido(s):
        return isinstance(s, str) and bool(s) and s not in (EPSILON, FIN) and not any(c.isspace() for c in s)
    if not all(simbolo_valido(n) for n in g):
        raise ValueError('Nombre de no terminal vacío, reservado o con espacios.')
    if inicial is not None and inicial not in g:
        raise ValueError('El símbolo inicial no está definido.')
    usados = set()
    for n, alternativas in g.items():
        if not isinstance(alternativas, list) or not alternativas:
            raise ValueError(f'{n} debe tener una lista no vacía de producciones.')
        for prod in alternativas:
            if not isinstance(prod, tuple) or not all(simbolo_valido(s) for s in prod):
                raise ValueError(f'Producción inválida de {n}; epsilon se representa con ().')
            usados.update(prod)
    terminales = usados - g.keys()
    if terminales_esperados is not None and terminales != set(terminales_esperados):
        raise ValueError(f'Vocabulario distinto: faltan {sorted(set(terminales_esperados)-terminales)}; '
                         f'sobran {sorted(terminales-set(terminales_esperados))}.')
    return terminales


def primero_secuencia(secuencia: Produccion, first: dict[str, set[str]]) -> set[str]:
    """FIRST de una secuencia; first contiene exactamente los no terminales.

    Se sigue hacia la derecha mientras el símbolo anterior sea anulable.
    Un símbolo que no es clave de first se trata como terminal.
    """
    resultado = set()
    for simbolo in secuencia:
        conjunto = first.get(simbolo, {simbolo})
        resultado.update(conjunto - {EPSILON})
        if EPSILON not in conjunto:
            return resultado
    resultado.add(EPSILON)
    return resultado


def calcular_first(g: Gramatica) -> dict[str, set[str]]:
    """Itera hasta estabilizar. Los conjuntos solo crecen y el universo es finito."""
    validar_gramatica(g)
    first = {n: set() for n in g}
    cambio = True
    while cambio:
        cambio = False
        for n, alternativas in g.items():
            for prod in alternativas:
                nuevo = primero_secuencia(prod, first) - first[n]
                if nuevo:
                    first[n].update(nuevo)
                    cambio = True
    return first


def _validar_conjuntos(g, conjuntos, permitidos, nombre):
    if not isinstance(conjuntos, dict) or conjuntos.keys() != g.keys():
        raise ValueError(f'{nombre} debe incluir exactamente los no terminales.')
    for valores in conjuntos.values():
        if not isinstance(valores, (set, frozenset)) or not valores <= permitidos:
            raise ValueError(f'{nombre} contiene valores inválidos.')


def calcular_follow(g: Gramatica, inicial: str,
                     first: dict[str, set[str]]) -> dict[str, set[str]]:
    """Para A -> alfa B beta: FIRST(beta)-epsilon se agrega a FOLLOW(B).

    Si beta es anulable, se agrega FOLLOW(A). Se inicia FOLLOW(inicial) con $.
    first debe ser el cálculo completo de esta misma gramática.
    """
    terminales = validar_gramatica(g, inicial)
    _validar_conjuntos(g, first, terminales | {EPSILON}, 'FIRST')
    follow = {n: set() for n in g}
    follow[inicial].add(FIN)
    cambio = True
    while cambio:
        cambio = False
        for n, alternativas in g.items():
            for prod in alternativas:
                for i, simbolo in enumerate(prod):
                    if simbolo not in g:
                        continue
                    resto = primero_secuencia(prod[i + 1:], first)
                    nuevos = resto - {EPSILON}
                    if EPSILON in resto:
                        nuevos |= follow[n]
                    nuevos -= follow[simbolo]
                    if nuevos:
                        follow[simbolo].update(nuevos)
                        cambio = True
    return follow


@dataclass(frozen=True)
class Alternativa:
    """Una producción candidata y la razón de su selección en una celda."""
    produccion: Produccion
    origenes: tuple[str, ...]  # FIRST, FOLLOW, o ambos


@dataclass(frozen=True)
class Conflicto:
    no_terminal: str
    token: str
    alternativas: tuple[Alternativa, ...]


def construir_tabla(g: Gramatica, first: dict[str, set[str]],
                    follow: dict[str, set[str]]) -> tuple[dict, list[Conflicto]]:
    """Devuelve tabla dispersa y conflictos sin sobrescribir alternativas.

    Clave: (no_terminal, token). Valor: lista de producciones distintas.
    Una celda ausente significa error. () es la producción vacía seleccionada.
    FIRST/FOLLOW deben ser resultados completos de esta misma gramática.
    """
    terminales = validar_gramatica(g)
    _validar_conjuntos(g, first, terminales | {EPSILON}, 'FIRST')
    _validar_conjuntos(g, follow, terminales | {FIN}, 'FOLLOW')
    evidencia = {}
    for n, alternativas in g.items():
        for prod in alternativas:
            conjunto = primero_secuencia(prod, first)
            seleccion = {t: {'FIRST'} for t in conjunto - {EPSILON}}
            if EPSILON in conjunto:
                for t in follow[n]:
                    seleccion.setdefault(t, set()).add('FOLLOW')
            for token, origenes in seleccion.items():
                evidencia.setdefault((n, token), {}).setdefault(prod, set()).update(origenes)
    tabla, conflictos = {}, []
    for clave in sorted(evidencia):
        candidatos = evidencia[clave]
        tabla[clave] = sorted(candidatos)
        if len(candidatos) > 1:
            conflictos.append(Conflicto(*clave, tuple(
                Alternativa(p, tuple(sorted(candidatos[p]))) for p in sorted(candidatos))))
    return tabla, conflictos
