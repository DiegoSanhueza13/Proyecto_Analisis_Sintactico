class Nodo:
    def __init__(self, etiqueta: str, hijos: list['Nodo'] | None = None):
        self.etiqueta = etiqueta
        self.hijos = hijos or []
 
    def __repr__(self):
        return f'Nodo({self.etiqueta!r}, {self.hijos!r})'
 
 
def a_texto(nodo: Nodo) -> str:
    """Devuelve el árbol con el formato ├── / └── (la raíz va sin conectores)."""
    lineas = [nodo.etiqueta]
 
    def recorrer(n: Nodo, prefijo: str):
        for i, hijo in enumerate(n.hijos):
            ultimo = i == len(n.hijos) - 1
            lineas.append(prefijo + ('└── ' if ultimo else '├── ') + hijo.etiqueta)
            recorrer(hijo, prefijo + ('    ' if ultimo else '│   '))
 
    recorrer(nodo, '')
    return '\n'.join(lineas)