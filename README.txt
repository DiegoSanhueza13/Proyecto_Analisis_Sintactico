PROYECTO DE ANÁLISIS SINTÁCTICO — AUTOMATIZACIÓN AGRÍCOLA

Lenguaje académico de reglas de sensores y acciones. El proyecto no tiene un
nombre propio acordado. Valida sintaxis y construye un AST; no opera equipos.

REQUISITOS Y EJECUCIÓN

Python 3.10 o superior. No requiere instalar paquetes externos ni requirements.txt.
Abrir una terminal en la raíz de este repositorio y ejecutar:

  python -m src.main ejemplos/validos/01_activar.txt
  python -m src.main ejemplos/validos/05_valido.txt --tokens
  python -m src.main ejemplos/invalidos/01_falta_then.txt
  python -m unittest discover -s tests -v
  python -m src.exportar_analisis --salida resultados
  python -m src.verificar_entrega

El CLI devuelve 0 si la entrada es válida y 1 si hay errores de lectura,
léxicos o sintácticos. Las entradas son archivos UTF-8, con o sin BOM.
El AST se muestra con caracteres Unicode y las salidas del CLI usan UTF-8.
No ejecutar src/main.py directamente: los módulos usan importaciones de paquete.

LENGUAJE

  WHEN humedad < 30 AND lluvia == FALSE THEN REGAR norte POR 15 MIN Y ACTIVAR bomba;

- Programa: una o más reglas WHEN condición THEN acciones;.
- Comparación: ID REL valor. Valor: entero no negativo o TRUE/FALSE.
- Comparadores: >, <, >=, <=, ==, !=.
- Prioridad: paréntesis, NOT, AND, OR. AND/OR se asocian a la izquierda en el AST.
- Acciones: ACTIVAR ID, DESACTIVAR ID y REGAR ID POR NUM MIN.
- Y une acciones; AND une condiciones.
- Reservadas sin distinción de mayúsculas. ID: [A-Za-z_][A-Za-z0-9_]*.
- Sin cadenas, comentarios, decimales, negativos, booleanos aislados como condición
  ni identificadores como valor de comparación.
- Cero y comparaciones entre tipos incompatibles se admiten sintácticamente:
  no existe todavía una fase semántica de tipos, sensores o rangos agronómicos.

ESTRUCTURA Y APORTES

src/contratos.py          Token, constantes y errores compartidos.
src/gramatica.py          Definición central de la gramática candidata.
src/analisis_gramatica.py FIRST, FOLLOW, tabla LL(1) y conflictos.
src/exportar_analisis.py  Exportación formal a JSON y CSV.
src/agro.py              Lexer adaptado de la base del docente.
src/parser.py            Parser manual por descenso recursivo.
src/arbol.py             Nodos y representación textual del AST.
src/main.py              CLI y función analizar_texto(texto).
src/verificar_entrega.py Corpus ejecutado por API y por CLI; exporta evidencia.
tests/                   Pruebas formales, parser, AST e integración.
ejemplos/                10 válidas, 10 inválidas y 5 límite, con manifiesto.
resultados/              Resultados reproducibles y carpeta de capturas.
docs/                    Espacio reservado para la documentación final del grupo.

La base del módulo formal está en c0ce1c5 (Álvaro Valenzuela).
Lexer, parser, AST, CLI y pruebas de entradas proceden de c18d9bf (DiegoSanhueza13).
Los cambios de integración se registran después, conservando esos commits.
El grupo debe revisar y poder explicar el código, incluido el apoyo de IA usado.

EVIDENCIA Y LIMITACIONES

verificar_entrega regenera pruebas_entradas.csv, first_follow.json, tabla_ll1.csv,
conflictos.json, ast_ejemplo.txt y tres transcripciones reales del CLI.
manifest_ejecucion.json registra fecha UTC y SHA-256 del código y entradas,
normalizando CRLF a LF para que las huellas no dependan del sistema operativo.
Regenerar la evidencia después de cambiar gramática, código o ejemplos.
Las transcripciones son texto de ejecuciones reales; no son capturas de pantalla.
Las capturas reales pueden añadirse en resultados/capturas/.

Las pruebas formales incluyen gramáticas conflictivas y casos resueltos a mano.
Las pruebas de entradas incluyen posiciones de error y precedencia del AST.
Las cadenas largas de AND/OR y el dibujo del árbol usan iteración; la anidación
de paréntesis y NOT sigue sujeta al límite de recursión de Python. El CLI informa
si ese límite se excede. Se detiene en el primer error y no recupera varios.

El informe de Google Docs es independiente: esta integración no lo modifica.
Antes de la entrega, el grupo debe completar sus pendientes y verificar que
describa los archivos y comandos reales de este repositorio.
