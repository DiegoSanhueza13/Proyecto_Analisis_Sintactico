import argparse
import sys
from pathlib import Path
from .agro import tokenizar
from .arbol import a_texto
from .contratos import ErrorLexico, ErrorSintactico
from .parser import Parser
 
 
def analizar_texto(texto: str):
    return Parser(tokenizar(texto)).analizar()
 
 
def main(argv=None) -> int:
    cli = argparse.ArgumentParser(description='Analizador sintáctico del lenguaje agrícola')
    cli.add_argument('archivo', type=Path, help='programa fuente (UTF-8)')
    cli.add_argument('--tokens', action='store_true', help='mostrar también los tokens')
    args = cli.parse_args(argv)
    try:
        texto = args.archivo.read_text(encoding='utf-8')
    except OSError as e:
        print(f'No se pudo leer el archivo: {e}', file=sys.stderr)
        return 1
    try:
        tokens = tokenizar(texto)
        if args.tokens:
            for t in tokens:
                print(f'{t.linea}:{t.columna}\t{t.tipo}\t{t.lexema}')
        arbol = Parser(tokens).analizar()
    except ErrorLexico as e:
        print(f'Error léxico [{e.linea}:{e.columna}]: {e.mensaje}.', file=sys.stderr)
        return 1
    except ErrorSintactico as e:
        print(f'Error sintáctico [{e.linea}:{e.columna}]: {e.mensaje}.', file=sys.stderr)
        return 1
    print('Programa válido.')
    print(a_texto(arbol))
    return 0
 
 
if __name__ == '__main__':
    raise SystemExit(main())