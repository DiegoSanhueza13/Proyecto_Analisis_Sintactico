class Nodo:
    def __init__(self, etiqueta: str, hijos: list['Nodo'] | None = None):
        self.etiqueta = etiqueta
        self.hijos = hijos or []
 
    def __repr__(self):
        return f'Nodo({self.etiqueta!r}, {self.hijos!r})'
 
 
def a_texto(nodo: Nodo) -> str:
    """Devuelve el árbol con el formato ├── / └── (la raíz va sin conectores)."""
    lineas = [nodo.etiqueta]
 
    # Pila explícita: un AST profundo de AND/OR no depende de la recursión.
    pila = [(hijo, '', i == len(nodo.hijos) - 1)
            for i, hijo in reversed(list(enumerate(nodo.hijos)))]
    while pila:
        actual, prefijo, ultimo = pila.pop()
        lineas.append(prefijo + ('└── ' if ultimo else '├── ') + actual.etiqueta)
        siguiente = prefijo + ('    ' if ultimo else '│   ')
        pila.extend((hijo, siguiente, i == len(actual.hijos) - 1)
                    for i, hijo in reversed(list(enumerate(actual.hijos))))
    return '\n'.join(lineas)
