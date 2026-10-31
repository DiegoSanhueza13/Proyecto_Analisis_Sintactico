"""Ejecutar corpus y generar evidencia real: python -m src.verificar_entrega.

El manifiesto ejemplos/casos.json contiene resultados esperados independientes
de esta ejecución. No sustituye la suite unittest ni modifica el informe.
Los resultados incluyen hashes para detectar evidencia desactualizada.
"""
import csv
import hashlib
import json
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from .agro import tokenizar
from .arbol import a_texto
from .contratos import ErrorLexico, ErrorSintactico
from .exportar_analisis import exportar
from .gramatica import GRAMATICA, INICIAL, TERMINALES
from .analisis_gramatica import validar_gramatica
from .parser import Parser

RAIZ = Path(__file__).resolve().parents[1]


def verificar():
    salida = RAIZ / 'resultados'
    salida.mkdir(exist_ok=True)
    casos = json.loads((RAIZ / 'ejemplos/casos.json').read_text(encoding='utf-8'))
    filas = []
    for caso in casos:
        ruta = (RAIZ / caso['archivo']).resolve()
        if not ruta.is_relative_to(RAIZ / 'ejemplos'):
            raise ValueError('El manifiesto solo admite archivos de ejemplos/.')
        texto = ruta.read_text(encoding='utf-8-sig')
        obtenido, mensaje, linea, columna = 'valido', 'Programa válido.', '', ''
        try:
            Parser(tokenizar(texto)).analizar()
        except (ErrorLexico, ErrorSintactico) as exc:
            obtenido = 'lexico' if isinstance(exc, ErrorLexico) else 'sintactico'
            mensaje, linea, columna = exc.mensaje, exc.linea, exc.columna
        # También se comprueba el programa desde un proceso nuevo, como lo usa
        # un integrante al ejecutar los comandos del README.txt.
        cli = subprocess.run([sys.executable, '-m', 'src.main', str(ruta)],
                             cwd=RAIZ, capture_output=True, encoding='utf-8', timeout=20)
        coincide = (obtenido == caso['esperado']
                    and cli.returncode == (0 if obtenido == 'valido' else 1)
                    and 'Traceback' not in cli.stderr)
        for clave, valor in [('linea', linea), ('columna', columna)]:
            if clave in caso:
                coincide &= caso[clave] == valor
        filas.append({'id': caso['id'], 'archivo': caso['archivo'], 'entrada': texto,
                      'esperado': caso['esperado'], 'obtenido': obtenido,
                      'correcto': coincide, 'linea': linea, 'columna': columna,
                      'mensaje': mensaje, 'codigo_cli': cli.returncode})
    with (salida / 'pruebas_entradas.csv').open('w', encoding='utf-8', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(filas[0]), lineterminator='\n')
        writer.writeheader()
        writer.writerows(filas)
    validar_gramatica(GRAMATICA, INICIAL, TERMINALES)
    conflictos = exportar(GRAMATICA, INICIAL, salida)
    for nombre, archivo in [('ejecucion_valida', 'ejemplos/validos/05_valido.txt'),
                            ('error_falta_then', 'ejemplos/invalidos/01_falta_then.txt'),
                            ('error_falta_valor', 'ejemplos/invalidos/02_invalido.txt')]:
        r = subprocess.run([sys.executable, '-m', 'src.main', archivo],
                           cwd=RAIZ, capture_output=True, encoding='utf-8', timeout=20)
        (salida / f'{nombre}.txt').write_text(
            f'$ python -m src.main {archivo}\n' + r.stdout + r.stderr
            + f'\nCódigo de salida: {r.returncode}\n', encoding='utf-8')
    texto = (RAIZ / 'ejemplos/validos/05_valido.txt').read_text(encoding='utf-8')
    ast = Parser(tokenizar(texto)).analizar()
    (salida / 'ast_ejemplo.txt').write_text(a_texto(ast) + '\n', encoding='utf-8')
    archivos = (list((RAIZ / 'src').glob('*.py')) + list((RAIZ / 'tests').glob('*.py'))
                + list((RAIZ / 'ejemplos').rglob('*.txt')) + [RAIZ / 'ejemplos/casos.json'])
    # Git puede convertir LF a CRLF en Windows: se normalizan solo los saltos
    # para que el mismo código tenga la misma huella en un checkout limpio.
    hashes = {p.relative_to(RAIZ).as_posix(): hashlib.sha256(
                  p.read_bytes().replace(b'\r\n', b'\n')).hexdigest()
              for p in sorted(archivos)}
    resumen = {'fecha_utc': datetime.now(timezone.utc).isoformat(),
               'casos': len(filas), 'correctos': sum(f['correcto'] for f in filas),
               'conflictos_ll1': len(conflictos),
               'normalizacion_sha256': 'CRLF a LF antes de calcular SHA-256',
               'sha256_fuentes_y_entradas': hashes}
    (salida / 'manifest_ejecucion.json').write_text(
        json.dumps(resumen, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    print(f"Corpus: {resumen['correctos']}/{resumen['casos']} correctos. "
          f'Conflictos LL(1): {len(conflictos)}. Evidencia en resultados/.')
    return 0 if resumen['correctos'] == resumen['casos'] and not conflictos else 1


if __name__ == '__main__':
    raise SystemExit(verificar())
