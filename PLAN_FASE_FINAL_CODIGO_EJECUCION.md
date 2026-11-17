# Plan de trabajo restante: código intermedio y ejecución en TM

## 1. Propósito

Este documento describe lo que falta para completar el compilador Skuld a
partir de:

- el compilador actual del repositorio;
- la especificación de la entrega final
  `Entrega_Final_Proyecto_Compiladores_II_UAA.pdf`;
- el proyecto de referencia `tiny-master`.

El objetivo de la fase final es transformar un programa Skuld que ya fue
validado semánticamente en instrucciones para la **Tiny Machine (TM)** y
ejecutarlas mostrando el resultado en el panel inferior del IDE, de forma
similar a la terminal de Visual Studio.

La generación del código y su ejecución son evidencias independientes. No es
suficiente mostrar la salida del programa: también debe poder revisarse el
archivo TM que produjo el compilador.

## 2. Estado actual verificado

### Implementado

- Análisis léxico.
- Análisis sintáctico y generación del AST.
- Análisis semántico.
- Tabla de símbolos.
- AST anotado.
- Reporte y resaltado de errores.
- IDE con editor, explorador, panel de analizadores y panel inferior.
- Panel inferior con pestañas `Consola`, `Errores` y `Ejecución`.
- Acciones del IDE para `Código Intermedio` y `Ejecución`.
- Mapeo preparado en `ide/compiler_runner.py`:
  - `intermedio` → `--intermedio`
  - `ejecucion` → `--ejecutar`

### Pendiente o incompleto

- El CLI no implementa todavía `--intermedio`.
- El CLI no implementa todavía `--ejecutar`.
- No existe un generador Skuld de código de tres direcciones.
- No existe un generador Skuld de instrucciones TM.
- No existe un simulador TM integrado al proyecto.
- Las acciones del IDE para código intermedio y ejecución no tienen una
  implementación funcional detrás.
- El panel inferior ya está ubicado debajo del editor, pero falta conectarlo a
  la salida real del generador y del simulador.
- Todavía no existe una matriz de pruebas que demuestre generación y ejecución
  para cinco programas.

## 3. Flujo final esperado

```text
Archivo .stn
    |
    v
Análisis léxico
    |
    v
Análisis sintáctico -> AST
    |
    v
Análisis semántico -> AST validado + tabla de símbolos
    |
    +------------------------------+
    |                              |
    v                              v
Código intermedio .ci          Generador TM
(tres direcciones)                 |
                                   v
                              Código TM .tm
                                   |
                                   v
                              Simulador TM
                                   |
                                   v
                         Salida en Terminal/Ejecución
```

El archivo `.ci` es una salida didáctica opcional y no debe utilizarse como
entrada directa del simulador. El simulador debe recibir el archivo `.tm`
generado desde el AST validado.

## 4. Trabajo restante por etapas

### Etapa 1: definir la correspondencia del AST

Antes de copiar la estrategia de `tiny-master`, hay que documentar cómo se
representa cada construcción de Skuld en el AST actual y qué instrucción o
secuencia TM le corresponde.

Como mínimo se debe cubrir el subconjunto que realmente soporta Skuld:

- literales enteros, flotantes y booleanos;
- identificadores;
- asignaciones;
- operaciones aritméticas;
- comparaciones y operaciones lógicas;
- `if` / `else`;
- `while`;
- `do` / `until`;
- `cin`;
- `cout`;
- funciones y retornos, si el análisis semántico ya los admite.

Las construcciones no soportadas deben producir un error explícito y no
generar una salida que parezca válida.

### Etapa 2: completar las posiciones de memoria

El generador necesita convertir cada identificador en una posición de memoria.
La tabla de símbolos debe conservar, o calcular, al menos:

- nombre;
- tipo;
- ámbito;
- desplazamiento;
- clase de símbolo;
- parámetros y retorno cuando sea una función.

Se debe definir una convención estable para los registros de la TM:

| Registro | Uso |
|---|---|
| `pc` | Contador de programa |
| `mp` | Memoria temporal |
| `gp` | Variables globales |
| `ac` | Acumulador principal |
| `ac1` | Segundo acumulador |

Esta convención sigue el modelo de `tiny-master/code.h`. La consulta del
desplazamiento debe realizarse mediante la tabla de símbolos, no mediante
posiciones inventadas por el generador.

### Etapa 3: generar código intermedio de tres direcciones

Crear un módulo independiente para producir un archivo `.ci` desde el AST
validado.

El generador debe:

1. recorrer el árbol en orden de ejecución;
2. crear temporales (`t1`, `t2`, etc.);
3. crear etiquetas para saltos (`L1`, `L2`, etc.);
4. emitir asignaciones y operaciones de tres direcciones;
5. representar claramente entradas, salidas, condiciones y retornos;
6. guardar el resultado asociado al archivo fuente actual.

Ejemplo esperado:

```text
t1 = fact * x
fact = t1
ifFalse condicion goto L1
goto L2
L1:
```

El código `.ci` sirve para inspección y explicación del proceso. No reemplaza
al código TM.

### Etapa 4: generar instrucciones TM

Crear un generador equivalente a `tiny-master/cgen.c`, adaptado a los nodos
reales del AST de Skuld.

Se necesitan rutinas separadas para:

- generar sentencias;
- generar expresiones;
- cargar constantes;
- cargar identificadores;
- almacenar resultados;
- emitir operaciones aritméticas;
- emitir comparaciones;
- emitir entrada y salida;
- emitir saltos condicionales;
- emitir saltos incondicionales;
- finalizar el programa con `HALT`.

También se necesita un emisor equivalente a `tiny-master/code.c` para:

- numerar instrucciones;
- emitir instrucciones de registros;
- emitir instrucciones registro-memoria;
- reservar posiciones para saltos;
- corregir destinos posteriormente;
- calcular desplazamientos relativos al `pc`;
- escribir el archivo `.tm`.

La generación únicamente debe ejecutarse si léxico, sintaxis y semántica
terminaron correctamente.

### Etapa 5: integrar el simulador TM

Integrar o portar el comportamiento de `tiny-master/TM.C` a un módulo
ejecutable desde Python. El simulador debe:

- leer el archivo `.tm`;
- validar el formato de cada instrucción;
- cargar la memoria de instrucciones;
- ejecutar las instrucciones;
- solicitar valores cuando encuentre `IN`;
- acumular la salida de `OUT`;
- detenerse con `HALT`;
- detectar errores de memoria, instrucciones inválidas y división entre cero;
- devolver código de salida distinto de cero cuando falle.

El simulador no debe recibir el archivo fuente `.stn` ni el archivo `.ci`.

### Etapa 6: ampliar el CLI

Agregar al CLI las fases:

```text
python skuld_compiler.py --intermedio archivo.stn
python skuld_compiler.py --tm archivo.stn
python skuld_compiler.py --ejecutar archivo.stn
```

Si se conserva el nombre reservado por el IDE, también debe aceptarse:

```text
python skuld_compiler.py --intermedio archivo.stn
python skuld_compiler.py --ejecutar archivo.stn
```

Comportamiento requerido:

- `--intermedio`: valida el programa y genera/muestra el `.ci`.
- `--tm`: valida el programa y genera/muestra el `.tm`.
- `--ejecutar`: valida, genera el `.tm`, ejecuta ese `.tm` y muestra la salida.
- Un error en cualquier fase detiene las siguientes fases.
- No se debe mostrar una salida anterior como si correspondiera a la
  compilación actual.
- Los archivos generados deben quedar junto al fuente, dentro de una carpeta
  de salidas definida y consistente.

### Etapa 7: conectar el IDE y mantener la terminal abajo

La estructura visual actual ya utiliza un `QSplitter` vertical: la zona
principal arriba y el panel `Terminal` abajo. Se debe conservar esa solución,
sin abrir una ventana separada para la ejecución.

El panel inferior debe funcionar así:

- **Consola:** mensajes de fases, archivos guardados y tiempos.
- **Errores:** errores léxicos, sintácticos, semánticos, de generación o de
  ejecución.
- **Ejecución:** entradas solicitadas, salida producida y estado final.

El panel de analizadores debe distinguir claramente:

- `Código TM`: instrucciones numeradas, registros, operandos y saltos;
- `Código intermedio (tres direcciones)`: temporales y etiquetas.

Al ejecutar desde el IDE:

1. guardar el archivo activo;
2. ejecutar léxico, sintaxis y semántica;
3. detenerse si existe algún error;
4. generar el `.ci` y el `.tm`;
5. mostrar el código correspondiente al fuente actual;
6. ejecutar el `.tm`;
7. colocar la salida en la pestaña `Ejecución` del panel inferior;
8. mostrar el tiempo y los errores sin ocultarlos.

### Etapa 8: pruebas de aceptación

Preparar al menos cinco programas, incluyendo casos con:

1. asignaciones y operaciones aritméticas;
2. entrada y salida;
3. una condición `if` / `else`;
4. un ciclo;
5. una combinación de expresiones y control de flujo.

Para cada programa se debe registrar:

| Evidencia | Resultado esperado |
|---|---|
| AST validado | No hay errores semánticos |
| Tabla de símbolos | Tiene posiciones de memoria consistentes |
| `.ci` | Tiene temporales y etiquetas correctos |
| `.tm` | Tiene instrucciones TM numeradas y válidas |
| Ejecución | Produce el resultado esperado |
| IDE | Muestra el código y la salida del mismo archivo fuente |

También se deben probar errores de:

- variable no declarada;
- tipos incompatibles;
- división entre cero;
- instrucción TM inválida;
- entrada no numérica cuando corresponda;
- construcciones todavía no soportadas.

## 5. Archivos que se deberán crear o modificar

Los nombres son una propuesta; deben ajustarse a las convenciones existentes
si ya hay módulos equivalentes.

```text
analizadores/
├── codigo_intermedio/
│   ├── __init__.py
│   └── generator.py
└── generacion_codigo/
    ├── __init__.py
    ├── tm_emitter.py
    └── tm_generator.py

ejecucion/
├── __init__.py
└── tm_machine.py
```

Además, será necesario modificar:

- `skuld_compiler.py`;
- `ide/compiler_runner.py`;
- `ide/analysis_panel.py`;
- `ide/main_window_sections/workspace_flow.py`;
- pruebas del compilador y del IDE;
- `README.md`, para documentar instalación, comandos, archivos generados y
  limitaciones.

## 6. Criterios para considerar terminada la fase

La fase estará terminada cuando:

- un programa Skuld semánticamente válido produzca un `.tm` real;
- el `.tm` pueda abrirse y revisarse desde el IDE;
- el `.tm` se ejecute en el simulador TM;
- `IN` solicite datos y `OUT` muestre resultados;
- la salida aparezca en la pestaña `Ejecución` del terminal inferior;
- una compilación nueva nunca reutilice silenciosamente la salida de otra;
- los errores impidan generar o ejecutar código inválido;
- los cinco programas de prueba pasen generación y ejecución;
- el README y la entrega indiquen claramente qué construcciones están
  soportadas y cuáles no.

## 7. Referencias de la implementación de `tiny-master`

| Archivo | Qué se debe tomar como referencia |
|---|---|
| `CGEN.C` | Recorrido del árbol y traducción de sentencias/expresiones |
| `CODE.C` | Emisión de instrucciones y corrección de saltos |
| `CODE.H` | Convención de registros de la TM |
| `TM.C` | Carga, validación y ejecución de instrucciones |
| `MAIN.C` | Orden de fases y escritura del archivo `.tm` |

La referencia no debe copiarse sin adaptación: el AST, los tipos, la tabla de
símbolos y las construcciones de Skuld son los que determinan la generación
final.
