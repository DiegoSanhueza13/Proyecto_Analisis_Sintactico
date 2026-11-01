# Analizador sintáctico — Automatización agrícola

Proyecto del curso **Teoría de la Computación (INFO1148)**, Universidad Católica de Temuco.

Mini lenguaje de dominio específico para escribir reglas de riego y control de dispositivos a partir de sensores. El programa revisa si las reglas están bien escritas (análisis sintáctico LL(1) por descenso recursivo), construye su **árbol sintáctico (AST)** e informa los errores con su línea y columna. No controla equipos reales.

**Integrantes:** Nataly Huaiquinao Sáez · Diego Sanhueza Reveco · Alvaro Valenzuela Paillacar

📄 **Informe completo:** carpeta [`docs/`](docs/)

---

## Contenido

1. [Requisitos](#requisitos)
2. [Cómo ejecutarlo](#cómo-ejecutarlo)
3. [Demostración](#demostración)
4. [El lenguaje](#el-lenguaje)
5. [Cómo funciona](#cómo-funciona)
6. [Estructura del repositorio](#estructura-del-repositorio)
7. [Pruebas y evidencia](#pruebas-y-evidencia)
8. [Limitaciones](#limitaciones)

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

**Formato de entrada:** archivo de texto UTF-8 (con o sin BOM) con una o más reglas. El programa termina con código `0` si la entrada es válida y `1` si hay un error de lectura, léxico o sintáctico. El AST se dibuja con caracteres Unicode y la salida usa UTF-8.

> ⚠️ Ejecutar siempre con `python -m src.main` desde la raíz, no `python src/main.py`.

## Demostración

Capturas de ejecuciones reales en el equipo de un integrante. Todas están en [`resultados/capturas/`](resultados/capturas/).

### Figura 1. Entrada válida V05

`python -m src.main ejemplos/validos/05_valido.txt`

![Figura 1. Entrada válida V05](resultados/capturas/Entrada%20v%C3%A1lida%20V05.png)

El parser acepta la regla y muestra su AST: la negación agrupa la condición OR y las dos acciones quedan unidas bajo `Acciones`.

### Figura 2. Entrada inválida I01 — falta THEN

`python -m src.main ejemplos/invalidos/01_falta_then.txt`

![Figura 2. Entrada inválida I01 — falta THEN](resultados/capturas/Entrada%20inv%C3%A1lida%20I01.png)

El parser informa qué esperaba, qué encontró y la posición del error (línea 1, columna 19).

### Figura 3. Entrada inválida I02 — falta un valor

`python -m src.main ejemplos/invalidos/02_invalido.txt`

![Figura 3. Entrada inválida I02 — falta un valor](resultados/capturas/Entrada%20inv%C3%A1lida%20I02.png)

Error después del operador `<`, indicando los valores admitidos (NUM, TRUE o FALSE).

### Figura 4. Tokens y AST de la entrada V01

`python -m src.main ejemplos/validos/01_activar.txt --tokens`

![Figura 4. Tokens y AST de la entrada V01](resultados/capturas/Entrada%20v%C3%A1lida%20V01.png)

Con `--tokens` se ven las dos etapas: primero los tokens del analizador léxico (posición, tipo y lexema) y luego el AST.

### Figura 5. Pruebas automáticas

`python -m unittest discover -s tests`

![Figura 5. Pruebas automáticas](resultados/capturas/Ejecuci%C3%B3n%20de%20las%2044%20pruebas%20autom%C3%A1ticas.png)

Las 44 pruebas terminan correctamente.

### Figura 6. Verificación del corpus

`python -m src.verificar_entrega`

![Figura 6. Verificación del corpus](resultados/capturas/Verificaci%C3%B3n%20del%20corpus.png)

Las 25 entradas de ejemplo obtienen el resultado esperado y la tabla LL(1) no tiene conflictos.

## El lenguaje

Un programa tiene **una o más reglas**, cada una con la forma `WHEN condición THEN acciones;`

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
| Prioridad | paréntesis → `NOT` → `AND` → `OR`. `AND` y `OR` se asocian a la izquierda en el AST |
| Acciones | `ACTIVAR id` · `DESACTIVAR id` · `REGAR id POR número MIN` |
| Varias acciones | Se unen con `Y` (mientras que `AND` une condiciones) |

**No se admite:** cadenas de texto, comentarios, decimales, números negativos, un booleano solo como condición (`WHEN TRUE THEN ...`) ni un identificador como valor de comparación (`humedad < limite`).

La gramática completa está en [`src/gramatica.py`](src/gramatica.py) y en la sección 3 del informe.

## Cómo funciona

El análisis pasa por tres etapas, cada una en su propio archivo:

```
texto del archivo ──► Lexer (agro.py) ──► tokens ──► Parser (parser.py) ──► AST (arbol.py)
                           │                               │
                           └──► Error léxico               └──► Error sintáctico
```

**1. Análisis léxico** — [`src/agro.py`](src/agro.py)
Recorre el texto con expresiones regulares y lo separa en *tokens*. Cada token guarda su tipo, el texto original y su línea y columna. Los espacios se ignoran, las palabras reservadas se reconocen sin importar mayúsculas y al final se agrega el token `$` (fin de entrada). Si aparece un símbolo desconocido, como `@`, se detiene con un error léxico.

Con la opción `--tokens` se ve el resultado de esta etapa:

```
$ python -m src.main mi_regla.txt --tokens
1:1	WHEN	WHEN
1:6	ID	humedad
1:14	REL	<
1:16	NUM	30
1:19	THEN	THEN
1:24	ACTIVAR	ACTIVAR
1:32	ID	bomba
1:37	;	;
2:1	$
```

**2. Análisis sintáctico** — [`src/parser.py`](src/parser.py)
Es un parser **predictivo de descenso recursivo**: cada no terminal de la gramática es una función (`regla()`, `expr()`, `factor()`, `accion()`, etc.). Cada función mira solo el token actual y, según la tabla LL(1), decide qué producción aplicar. Si el token no corresponde, informa qué se esperaba, qué se encontró y dónde.

**3. Construcción del AST** — [`src/arbol.py`](src/arbol.py)
Mientras reconoce la entrada, el parser va creando nodos. El árbol final conserva solo lo importante (condiciones, operadores y acciones) y omite `WHEN`, `THEN`, `;` y los paréntesis, que ya quedaron reflejados en la forma del árbol.

**Análisis formal de la gramática** — [`src/gramatica.py`](src/gramatica.py) y [`src/analisis_gramatica.py`](src/analisis_gramatica.py)
Por separado del parser, la gramática está escrita como datos en Python y un módulo calcula automáticamente sus conjuntos FIRST y FOLLOW, la tabla LL(1) y los posibles conflictos. Así se comprueba que la gramática es LL(1) y que coincide con la del informe.

### Probar una regla propia

1. Crear un archivo de texto, por ejemplo `mi_regla.txt`, con una o más reglas:
   ```
   WHEN humedad < 30 THEN ACTIVAR bomba;
   WHEN lluvia == TRUE THEN DESACTIVAR bomba;
   ```
2. Ejecutar:
   ```bash
   python -m src.main mi_regla.txt
   ```

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
| ├ [`verificar_entrega.py`](src/verificar_entrega.py) | Ejecuta el corpus completo y guarda la evidencia |
| └ `__init__.py` | Marca `src` como paquete de Python (por eso se ejecuta con `python -m`) |
| [`tests/`](tests/) | Pruebas automáticas |
| ├ [`test_analisis.py`](tests/test_analisis.py) | FIRST, FOLLOW, tabla LL(1), detección de conflictos y exportación |
| ├ [`test_parser.py`](tests/test_parser.py) | Entradas válidas, inválidas y límite; mensajes y posiciones de error; forma del AST |
| └ [`test_integracion.py`](tests/test_integracion.py) | Línea de comandos, archivos reales, codificación UTF-8 y cadenas largas de AND/OR |
| [`ejemplos/`](ejemplos/) | Entradas de prueba |
| ├ [`validos/`](ejemplos/validos/) | 10 programas válidos (`01_activar.txt` … `10_valido.txt`) |
| ├ [`invalidos/`](ejemplos/invalidos/) | 10 programas con errores (`01_falta_then.txt` … `10_invalido.txt`) |
| ├ [`limite/`](ejemplos/limite/) | 5 casos límite (`01_limite.txt` … `05_limite.txt`) |
| └ [`casos.json`](ejemplos/casos.json) | Resultado esperado de cada entrada |
| [`resultados/`](resultados/) | Evidencia generada al ejecutar |
| ├ [`tabla_ll1.csv`](resultados/tabla_ll1.csv) | Tabla predictiva LL(1) |
| ├ [`first_follow.json`](resultados/first_follow.json) | Conjuntos FIRST y FOLLOW |
| ├ [`pruebas_entradas.csv`](resultados/pruebas_entradas.csv) | Resultado de las 25 entradas |
| ├ [`pruebas_unitarias.txt`](resultados/pruebas_unitarias.txt) | Salida de las pruebas automáticas |
| ├ [`ast_ejemplo.txt`](resultados/ast_ejemplo.txt) | AST de ejemplo |
| ├ [`conflictos.json`](resultados/conflictos.json) | Conflictos LL(1) encontrados (vacío) |
| ├ [`ejecucion_valida.txt`](resultados/ejecucion_valida.txt) | Transcripción real de una ejecución válida |
| ├ [`error_falta_then.txt`](resultados/error_falta_then.txt) | Transcripción real del error "falta THEN" |
| ├ [`error_falta_valor.txt`](resultados/error_falta_valor.txt) | Transcripción real del error "falta valor" |
| ├ [`manifest_ejecucion.json`](resultados/manifest_ejecucion.json) | Fecha y huellas SHA-256 de la ejecución |
| └ [`capturas/`](resultados/capturas/) | 6 capturas de pantalla de la demostración (ver [Demostración](#demostración)) |
| [`docs/`](docs/) | Informe final en PDF |
| `.gitignore` | Excluye de Git los archivos temporales de Python (`__pycache__`, entornos virtuales) |

## Pruebas y evidencia

- **44 pruebas automáticas**, todas correctas: [`tests/`](tests/) → salida en [`pruebas_unitarias.txt`](resultados/pruebas_unitarias.txt). Incluyen casos de FIRST/FOLLOW resueltos a mano, gramáticas con conflictos, posiciones de error, precedencia y asociación del AST.
- **25 entradas de ejemplo** (10 válidas, 10 inválidas y 5 límite), todas con el resultado esperado: [`pruebas_entradas.csv`](resultados/pruebas_entradas.csv).
- **Tabla LL(1) sin conflictos:** [`conflictos.json`](resultados/conflictos.json) está vacío.
- [`manifest_ejecucion.json`](resultados/manifest_ejecucion.json) registra la fecha UTC y las huellas SHA-256 del código y las entradas usadas (normalizando los saltos de línea, para que no dependan del sistema operativo).
- Las transcripciones de [`resultados/`](resultados/) son texto de ejecuciones reales; las capturas de pantalla están en [`resultados/capturas/`](resultados/capturas/) y se muestran en la sección [Demostración](#demostración).

Si se cambia la gramática, el código o los ejemplos, volver a generar la evidencia con `python -m src.verificar_entrega`.

## Limitaciones

- Solo revisa la **estructura** de las reglas: no comprueba que los sensores existan, que los tipos sean compatibles ni que los valores sean razonables para un cultivo. Por eso se aceptan, por ejemplo, el valor `0` o comparar un sensor numérico con `TRUE`.
- No admite decimales, números negativos, cadenas de texto ni comentarios.
- Se detiene en el **primer error** encontrado.
- Las cadenas largas de `AND`/`OR` y el dibujo del árbol usan ciclos, sin límite práctico. En cambio, anidar cientos de paréntesis o `NOT` puede superar el límite de recursión de Python; en ese caso el programa lo informa sin cerrarse con un error interno.
