# Descripcion tecnica del analisis semantico

## 1. Proposito

El analisis semantico es la tercera fase del compilador de Skuld. Recibe el
Arbol Sintactico Abstracto (AST) producido por el parser y comprueba que el
programa tenga un significado valido, mas alla de que su estructura cumpla la
gramatica.

La fase realiza simultaneamente estas tareas:

- Construye y consulta la tabla de simbolos.
- Controla los ambitos globales, de funciones y de bloques.
- Propaga y sintetiza tipos en los nodos del AST.
- Verifica declaraciones, usos de identificadores, asignaciones y retornos.
- Comprueba condiciones, operadores y argumentos de funciones.
- Evalua expresiones constantes cuando sus operandos son conocidos.
- Genera una copia anotada del AST sin modificar el AST original.
- Acumula errores semanticos con linea, columna, descripcion y lexema.

La implementacion se encuentra en
[`analizadores/analisis_semantico/semantic_analyzer.py`](D:/Compiladores-Skuld-/analizadores/analisis_semantico/semantic_analyzer.py)
y
[`analizadores/analisis_semantico/symbol_table.py`](D:/Compiladores-Skuld-/analizadores/analisis_semantico/symbol_table.py).

## 2. Posicion dentro del compilador

El flujo completo es:

```text
Archivo .stn
    |
    v
Analisis lexico
    | tokens
    v
Analisis sintactico
    | AST
    v
Analisis semantico
    | AST anotado + tabla de simbolos + errores
    v
Salida de CLI o paneles del IDE
```

La fase semantica no se ejecuta si el lexer o el parser producen errores. La
entrada de la fase es, por tanto, un AST sintacticamente valido.

Desde la CLI se ejecuta con:

```powershell
python skuld_compiler.py --semantico examples\prueba_semantica_valida.stn
```

El punto de integracion es `run_semantic` en
[`skuld_compiler.py`](D:/Compiladores-Skuld-/skuld_compiler.py). Esta funcion
crea el analizador, ejecuta `analyze(ast)`, imprime los resultados y retorna
codigo de error si se detectan errores semanticos.

## 3. Arquitectura del analizador

### 3.1 Entrada y salida

El metodo principal tiene la siguiente interfaz conceptual:

```python
annotated_ast, symbol_table, errors = analyzer.analyze(ast)
```

Antes de recorrer el arbol, `analyze`:

1. Hace una copia profunda del AST.
2. Reinicia la tabla de simbolos y la lista de errores.
3. Reinicia el tipo de retorno de la funcion actual.
4. Recorre la copia mediante `_annotate_node`.
5. Retorna la copia anotada, la tabla y todos los errores acumulados.

Esta estrategia conserva disponibles tanto el AST sintactico original como la
version enriquecida con informacion semantica.

### 3.2 Recorrido por clases de nodo

`_annotate_node` identifica cada nodo mediante `node.nodekind` y `node.kind`:

| Categoria | Construcciones procesadas |
|---|---|
| `DeclK` | Declaraciones de variables (`DeclVarK`) y funciones (`FuncK`) |
| `StmtK` | Bloques, asignaciones, `if`, `while`, `do-while`, `cin`, `cout`, `return` y llamadas como sentencia |
| `ExpK` | Literales, cadenas, identificadores, llamadas y operadores |

Los nodos no especializados se recorren recursivamente para no perder
subarboles que solo tengan funcion estructural.

## 4. Atributos semanticos del AST

Cada nodo puede recibir los siguientes atributos dinamicos:

| Atributo | Significado |
|---|---|
| `attr_type` | Tipo semantico calculado para el nodo |
| `attr_scope` | Ambito en el que se procesa el nodo |
| `attr_val` | Valor constante conocido, si puede calcularse |
| `attr_duplicate` | Marca interna para ocultar del renderizado un nodo de declaracion duplicado |

### 4.1 Atributos heredados

En una declaracion de varias variables, el tipo de la declaracion se propaga a
cada hijo `VarK`. Por ejemplo, en una declaracion equivalente a
`int a = 1, b = 2`, el tipo `int` se transmite a `a` y `b` antes de validar
sus inicializadores.

El ambito actual tambien se hereda como contexto de procesamiento para los
nodos visitados.

### 4.2 Atributos sintetizados

El tipo de una expresion se sintetiza a partir de sus hijos:

- Un literal entero sintetiza tipo entero.
- Un literal flotante sintetiza tipo flotante.
- Un literal booleano sintetiza tipo booleano.
- Una cadena sintetiza tipo `string`.
- Un identificador sintetiza el tipo registrado en la tabla.
- Una llamada sintetiza el tipo de retorno de la funcion.
- Una operacion sintetiza el tipo resultante segun sus operandos y operador.

Cuando todos los operandos de una expresion aritmetica o relacional tienen
valor conocido, tambien se conserva el resultado en `attr_val`. Esto permite
propagar valores constantes a inicializaciones, asignaciones y usos posteriores.

## 5. Normalizacion de tipos

El analizador utiliza nombres canonicos internos para mantener compatibilidad
con AST y ejemplos anteriores, pero muestra los nombres estandar en errores y
salidas:

| Nombre interno | Nombre mostrado |
|---|---|
| `worldline` | `int` |
| `divergence` | `float` |
| `reading` | `bool` |
| `string` | `string` |
| `void` | `void` |
| `unknown` | `unknown` |

La funcion `normalize_type` convierte los alias recibidos a la representacion
interna. `display_type` realiza la conversion inversa para mensajes, tabla de
simbolos y AST anotado. Los nombres estandar `int`, `float` y `bool` son
aceptados como alias de sus tipos internos.

## 6. Tabla de simbolos y ambitos

### 6.1 Estructura

La tabla implementa una cadena de ambitos lexicos:

```text
global
  |
  +-- funcion
  |     |
  |     +-- bloque
  |
  +-- main
```

Cada `Scope` contiene:

- Nombre del ambito.
- Nivel de anidamiento.
- Referencia al ambito padre.
- Diccionario de simbolos declarados localmente.

La busqueda normal comienza en el ambito actual y continua hacia los padres.
La busqueda local (`lookup_current`) solo consulta el ambito actual y se usa
para detectar duplicados.

### 6.2 Informacion almacenada por simbolo

Cada instancia de `Symbol` registra:

- Nombre del identificador.
- Tipo de dato.
- Nombre y nivel del ambito.
- Offset o direccion relativa de memoria.
- Linea de declaracion.
- Lineas de referencias y usos.
- Si representa una funcion.
- Tipos de sus parametros.
- Valor constante conocido, cuando existe.

Los offsets se calculan de forma incremental usando estos tamanos:

| Tipo | Tamano |
|---|---:|
| `int` | 4 bytes |
| `float` | 8 bytes |
| `bool` | 1 byte |
| `string` | 16 bytes (descriptor o referencia) |
| `void` | 0 bytes |

Una declaracion duplicada no se agrega por segunda vez a la tabla. Se conserva
el simbolo original y se reporta el error correspondiente.

### 6.3 Declaraciones procesadas

Al procesar una variable, el analizador:

1. Normaliza el tipo declarado.
2. Propaga el tipo a cada variable de la lista.
3. Analiza el inicializador, si existe.
4. Comprueba compatibilidad entre el tipo declarado y el inicializador.
5. Inserta el simbolo con su valor constante, si fue calculado.

Al procesar una funcion:

1. Registra la funcion en el ambito contenedor.
2. Guarda el tipo de retorno y los tipos de parametros.
3. Abre un nuevo ambito con el nombre de la funcion.
4. Inserta los parametros como simbolos locales.
5. Analiza el cuerpo con el tipo de retorno activo.
6. Restaura el tipo de retorno anterior y cierra el ambito.

## 7. Reglas de verificacion semantica

### 7.1 Identificadores y declaraciones

Se reportan errores cuando:

- Se usa una variable que no existe en el ambito actual ni en sus padres.
- Se asigna a una variable no declarada.
- Se llama a una funcion no declarada.
- Se declara dos veces el mismo identificador en un mismo ambito.
- Se repite el nombre de un parametro dentro de una funcion.

Cada referencia valida incrementa la lista de lineas almacenada en el simbolo.

### 7.2 Compatibilidad de asignaciones

Las asignaciones e inicializaciones requieren coincidencia exacta de tipos
normalizados. No se aplican conversiones implicitas:

```text
int   <- int       valido
float <- float     valido
bool  <- bool      valido
string <- string   valido
int   <- float     invalido
float <- int       invalido
int   <- bool      invalido
```

El mismo criterio se aplica a los valores retornados por funciones y a los
argumentos de llamadas.

### 7.3 Condiciones

Las condiciones de `if`, `while` y `do-while` deben sintetizar el tipo
booleano. Una expresion numerica, textual o de otro tipo produce un error.
Los subarboles de la condicion se siguen procesando para conservar todos los
diagnosticos posibles.

### 7.4 Operadores

| Operadores | Regla | Tipo resultante |
|---|---|---|
| `!`, `not` | Requieren un operando booleano | `bool` |
| `+`, `-` unarios | Requieren un operando numerico | Tipo del operando |
| `&&`, `||`, `and`, `or` | Ambos operandos deben ser booleanos | `bool` |
| `<`, `<=`, `>`, `>=` | Permiten tipos iguales o dos tipos numericos | `bool` |
| `==`, `!=` | Requieren tipos comparables; no mezclan tipos distintos | `bool` |
| `+` con `string` | Permite concatenacion si alguno de los operandos es cadena | `string` |
| `+`, `-`, `*`, `/`, `%`, `^` | Requieren operandos numericos, salvo la concatenacion indicada | `int` o `float` |

Una operacion numerica produce `float` si alguno de sus operandos es flotante;
en caso contrario produce `int`. Las expresiones con tipos desconocidos
mantienen `unknown` para evitar diagnosticos secundarios engañosos.

### 7.5 Llamadas a funciones

En cada llamada se comprueba:

1. Que la funcion exista.
2. Que la cantidad de argumentos coincida.
3. Que cada argumento sea compatible con el parametro correspondiente.

Una llamada valida sintetiza como tipo el retorno declarado por la funcion.

### 7.6 Retornos

Dentro de una funcion, el tipo de la expresion de `return` se compara con el
tipo de retorno activo. Se informa una incompatibilidad si ambos tipos son
conocidos y no coinciden. Las expresiones sin retorno se consideran `void`.

## 8. Evaluacion constante

El analizador realiza constant folding limitado durante el recorrido:

- Operaciones aritmeticas entre valores numericos conocidos.
- Comparaciones entre literales o valores constantes conocidos.
- Operaciones logicas entre booleanos conocidos.
- Negacion booleana.
- Concatenacion de cadenas conocidas.

La division y el modulo entre cero no provocan una excepcion del compilador:
la evaluacion constante se omite y el valor queda desconocido. El tipo de la
expresion continua disponible para las comprobaciones de compatibilidad.

## 9. Errores y recuperacion semantica

Los errores se representan con `SemanticError` y se acumulan en una lista. El
formato de salida es:

```text
ERROR_SEMANTICO(linea, columna): descripcion -> 'lexema'
```

El analizador evita duplicar exactamente el mismo mensaje para la misma linea,
descripcion y lexema. Ademas, usa `unknown` como tipo de propagacion cuando
una expresion depende de un identificador no declarado; esto permite continuar
el recorrido sin generar una cascada de errores derivados.

Entre los errores contemplados estan:

- Identificador o funcion no declarados.
- Declaracion duplicada.
- Parametro duplicado.
- Asignacion o inicializacion incompatible.
- Retorno incompatible.
- Cantidad incorrecta de argumentos.
- Tipo incorrecto de argumento.
- Condicion no booleana.
- Uso de operador con operandos incompatibles.
- Comparacion entre tipos no comparables.

## 10. AST anotado y evidencias

`print_annotated_tree` renderiza el AST con informacion de:

- Jerarquia de nodos.
- Tipo sintetizado.
- Ambito.
- Valor constante conocido.

Durante `--semantico`, el compilador imprime y guarda:

```text
<directorio del fuente>\ast\<nombre>.ast_annotated.txt
<directorio del fuente>\ast\<nombre>.symbols.txt
```

El primer archivo contiene el AST anotado. El segundo contiene la tabla de
simbolos con nombre, tipo visible, offset y lineas de aparicion. Estos archivos
sirven como evidencia de la fase y como insumo para la visualizacion del IDE.

## 11. Criterios de validacion

Una ejecucion semantica se considera correcta cuando:

- Un programa valido genera AST anotado y tabla de simbolos sin errores.
- Las variables y funciones se resuelven respetando el anidamiento de ambitos.
- Las incompatibilidades de tipos se reportan con tipos visibles (`int`,
  `float`, `bool`, `string`).
- Los errores no impiden analizar el resto del AST.
- Los archivos de evidencia se generan junto al fuente.

Casos de referencia:

- Valido: [`examples/prueba_semantica_valida.stn`](D:/Compiladores-Skuld-/examples/prueba_semantica_valida.stn)
- Invalido: [`examples/prueba_semantica_errores.stn`](D:/Compiladores-Skuld-/examples/prueba_semantica_errores.stn)
- Evidencia anotada: [`examples/ast/`](D:/Compiladores-Skuld-/examples/ast/)

## 12. Relacion con la migracion del vocabulario

El plan de migracion del lenguaje define `int`, `float` y `bool` como
vocabulario publico. El analizador ya acepta esos nombres y los muestra en sus
mensajes mediante la capa de normalizacion. Internamente aun conserva los
identificadores historicos `worldline`, `divergence` y `reading` para
compatibilidad con estructuras y ejemplos existentes.

Si se completa la migracion del lexer y del parser, la capa semantica debe
mantener una sola representacion canonica o actualizar de forma coordinada el
mapa `TYPE_NORMALIZATION`, la tabla `TYPE_SIZES` y las pruebas. La salida
visible debe continuar usando los nombres estandar definidos en
[`PLAN_MIGRACION_LENGUAJE.md`](D:/Compiladores-Skuld-/PLAN_MIGRACION_LENGUAJE.md).
