"""Exportación reproducible: python -m src.exportar_analisis --salida resultados.

Genera FIRST/FOLLOW, tabla dispersa y conflictos; no construye ni ejecuta un
parser. Código de salida 0 si no hay conflictos, 1 si la gramática no es LL(1).
Los archivos generados se versionan en resultados/; deben regenerarse si
cambia la gramática.
"""
import argparse
import csv
import json
from dataclasses import asdict
from pathlib import Path
from .analisis_gramatica import calcular_first, calcular_follow, construir_tabla, validar_gramatica
from .contratos import EPSILON
from .gramatica import GRAMATICA, INICIAL, TERMINALES


def exportar(g, inicial, carpeta):
    validar_gramatica(g, inicial)
    first = calcular_first(g)
    follow = calcular_follow(g, inicial, first)
    tabla, conflictos = construir_tabla(g, first, follow)
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    def escribir(nombre, datos):
        (carpeta / nombre).write_text(json.dumps(datos, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    escribir('first_follow.json', {
        'inicial': inicial,
        'gramatica': {n: [list(p) for p in g[n]] for n in sorted(g)},
        'FIRST': {n: sorted(first[n]) for n in sorted(g)},
        'FOLLOW': {n: sorted(follow[n]) for n in sorted(g)},
    })
    escribir('conflictos.json', [asdict(c) for c in conflictos])
    with (carpeta / 'tabla_ll1.csv').open('w', encoding='utf-8', newline='') as archivo:
        writer = csv.writer(archivo, lineterminator='\n')
        writer.writerow(['no_terminal', 'token', 'produccion', 'conflicto'])
        for (n, token), alternativas in sorted(tabla.items()):
            for prod in alternativas:
                writer.writerow([n, token, ' '.join(prod) if prod else EPSILON, len(alternativas) > 1])
    return conflictos


def main():
    cli = argparse.ArgumentParser(description='Exportar análisis de la gramática agrícola')
    cli.add_argument('--salida', type=Path, default=Path('resultados'))
    args = cli.parse_args()
    validar_gramatica(GRAMATICA, INICIAL, TERMINALES)
    conflictos = exportar(GRAMATICA, INICIAL, args.salida)
    print(f'Análisis exportado a {args.salida}. Conflictos LL(1): {len(conflictos)}.')
    return 1 if conflictos else 0


if __name__ == '__main__':
    raise SystemExit(main())
