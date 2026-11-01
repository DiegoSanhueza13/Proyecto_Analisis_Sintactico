# Analizador sintáctico — Automatización agrícola

Proyecto del curso **Teoría de la Computación (INFO1148)**, Universidad Católica de Temuco.

Mini lenguaje de dominio específico para escribir reglas de riego y control de dispositivos a partir de sensores. El programa revisa si las reglas están bien escritas (análisis sintáctico LL(1) por descenso recursivo), construye su **árbol sintáctico (AST)** e informa los errores con su línea y columna. No controla equipos reales.

**Integrantes:** Nataly Huaiquinao Sáez · Diego Sanhueza Reveco · Alvaro Valenzuela Paillacar

📄 **Informe completo:** carpeta [`docs/`](docs/)

---

## Contenido

1. [Requisitos](#requisitos)
2. [Cómo ejecutarlo](#cómo-ejecutarlo)
3. [El lenguaje](#el-lenguaje)
4. [Estructura del repositorio](#estructura-del-repositorio)
5. [Pruebas y evidencia](#pruebas-y-evidencia)
6. [Limitaciones](#limitaciones)

---

## Requisitos

- **Python 3.10 o superior.**
- No necesita instalar paquetes externos.

## Cómo ejecutarlo

Abrir una terminal en la carpeta raíz del repositorio (la que contiene este README).

> En Windows, si `python` no funciona, usar `py` en su lugar.

**Analizar un programa válido** (muestra el AST):

```bash
python -m src.main ejemplos/validos/05_valido.txt
```

Salida:

```
Programa válido.
Programa
└── Regla
    ├── NOT
    │   └── OR
    │       ├── ==
    │       │   ├── lluvia
    │       │   └── TRUE
    │       └── >=
    │           ├── humedad
    │           └── 60
    └── Acciones
        ├── REGAR norte (10 MIN)
        └── ACTIVAR bomba
```

**Analizar un programa con error:**

```bash
python -m src.main ejemplos/invalidos/01_falta_then.txt
```

```
Error sintáctico [1:19]: se esperaba THEN y se encontró 'ACTIVAR'.
```

**Otros comandos útiles:**

| Comando | Qué hace |
|---|---|
| `python -m src.main ARCHIVO --tokens` | Muestra además la lista de tokens (análisis léxico) |
| `python -m unittest discover -s tests -v` | Ejecuta todas las pruebas automáticas |
| `python -m src.exportar_analisis --salida resultados` | Calcula FIRST, FOLLOW y la tabla LL(1) y los guarda en [`resultados/`](resultados/) |
| `python -m src.verificar_entrega` | Ejecuta las 25 entradas de ejemplo y regenera toda la evidencia |

**Formato de entrada:** archivo de texto UTF-8 con una o más reglas. El programa termina con código `0` si la entrada es válida y `1` si hay un error.

> ⚠️ Ejecutar siempre con `python -m src.main` desde la raíz, no `python src/main.py`.

## El lenguaje

Cada regla tiene la forma `WHEN condición THEN acciones;`

```
WHEN humedad < 30 AND lluvia == FALSE THEN REGAR norte POR 15 MIN Y ACTIVAR bomba;
```

| Elemento | Detalle |
|---|---|
| Palabras reservadas | `WHEN THEN AND OR NOT TRUE FALSE ACTIVAR DESACTIVAR REGAR POR MIN Y` (no distinguen mayúsculas) |
| Identificadores | Letra o `_` seguida de letras, dígitos o `_`. Ej: `humedad_suelo`, `bomba` |
| Valores | Enteros no negativos (`30`) y booleanos (`TRUE`, `FALSE`) |
| Comparadores | `>` `<` `>=` `<=` `==` `!=` |
| Operadores lógicos | `NOT`, `AND`, `OR` y paréntesis para agrupar |
| Prioridad | paréntesis → `NOT` → `AND` → `OR` |
| Acciones | `ACTIVAR id` · `DESACTIVAR id` · `REGAR id POR número MIN` |
| Varias acciones | Se unen con `Y` (mientras que `AND` une condiciones) |

La gramática completa está en [`src/gramatica.py`](src/gramatica.py) y en la sección 3 del informe.

## Estructura del repositorio

| Carpeta / archivo | Contenido |
|---|---|
| [`src/`](src/) | Código fuente |
| ├ [`agro.py`](src/agro.py) | Analizador léxico (adaptado del entregado por el docente) |
| ├ [`parser.py`](src/parser.py) | Parser de descenso recursivo: una función por no terminal |
| ├ [`arbol.py`](src/arbol.py) | Nodos del AST y su dibujo en texto |
| ├ [`gramatica.py`](src/gramatica.py) | Definición de la gramática |
| ├ [`analisis_gramatica.py`](src/analisis_gramatica.py) | Cálculo de FIRST, FOLLOW, tabla LL(1) y conflictos |
| ├ [`contratos.py`](src/contratos.py) | Clase `Token` y errores compartidos |
| ├ [`main.py`](src/main.py) | Programa de línea de comandos |
| ├ [`exportar_analisis.py`](src/exportar_analisis.py) | Exporta FIRST/FOLLOW y la tabla a JSON/CSV |
| └ [`verificar_entrega.py`](src/verificar_entrega.py) | Ejecuta el corpus completo y guarda la evidencia |
| [`tests/`](tests/) | Pruebas automáticas (análisis formal, parser, AST e integración) |
| [`ejemplos/`](ejemplos/) | Entradas de prueba |
| ├ [`validos/`](ejemplos/validos/) | 10 programas válidos |
| ├ [`invalidos/`](ejemplos/invalidos/) | 10 programas con errores |
| ├ [`limite/`](ejemplos/limite/) | 5 casos límite |
| └ [`casos.json`](ejemplos/casos.json) | Resultado esperado de cada entrada |
| [`resultados/`](resultados/) | Evidencia generada al ejecutar |
| ├ [`tabla_ll1.csv`](resultados/tabla_ll1.csv) | Tabla predictiva LL(1) |
| ├ [`first_follow.json`](resultados/first_follow.json) | Conjuntos FIRST y FOLLOW |
| ├ [`pruebas_entradas.csv`](resultados/pruebas_entradas.csv) | Resultado de las 25 entradas |
| ├ [`pruebas_unitarias.txt`](resultados/pruebas_unitarias.txt) | Salida de las pruebas automáticas |
| ├ [`ast_ejemplo.txt`](resultados/ast_ejemplo.txt) | AST de ejemplo |
| └ [`capturas/`](resultados/capturas/) | Capturas de pantalla de la demostración |
| [`docs/`](docs/) | Informe final en PDF |

## Pruebas y evidencia

- **44 pruebas automáticas**, todas correctas: [`tests/`](tests/) → salida en [`pruebas_unitarias.txt`](resultados/pruebas_unitarias.txt).
- **25 entradas de ejemplo** (10 válidas, 10 inválidas y 5 límite), todas con el resultado esperado: [`pruebas_entradas.csv`](resultados/pruebas_entradas.csv).
- **Tabla LL(1) sin conflictos:** [`conflictos.json`](resultados/conflictos.json) está vacío.
- [`manifest_ejecucion.json`](resultados/manifest_ejecucion.json) registra la fecha y las huellas SHA-256 del código y las entradas usadas.

Si se cambia la gramática, el código o los ejemplos, volver a generar la evidencia con `python -m src.verificar_entrega`.

## Limitaciones

- Solo revisa la **estructura** de las reglas: no comprueba que los sensores existan, que los tipos sean compatibles ni que los valores sean razonables para un cultivo.
- No admite decimales, números negativos, cadenas de texto ni comentarios.
- Se detiene en el **primer error** encontrado.
- Anidar cientos de paréntesis o `NOT` puede superar el límite de recursión de Python; en ese caso el programa lo informa sin cerrarse con error interno.

## Autoría

- Módulo de análisis formal: commit `c0ce1c5` (Alvaro Valenzuela).
- Lexer, parser, AST, CLI y pruebas de entradas: commit `c18d9bf` (Diego Sanhueza).
- Integración posterior registrada en los commits siguientes.

Se utilizó IA generativa como apoyo; el grupo es responsable de comprender y explicar todo el código.
