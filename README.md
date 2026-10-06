# Skuld Compiler & IDE

Compilador educativo e IDE para el lenguaje Skuld. El proyecto está
desarrollado en Python y separa la interfaz gráfica de las fases del
compilador.

## Equipo

- Alan Gael Gallardo Jiménez
- Carlos Enrique Blanco Ortiz

## Tecnologías

- Python 3.11 o posterior
- PyQt5 para la interfaz gráfica
- PyInstaller para generar ejecutables opcionalmente

## Instalación y ejecución

Cada integrante debe instalar sus dependencias en su propio entorno virtual.
Los entornos virtuales y sus archivos generados no forman parte del
repositorio.

### Windows

La forma recomendada es:

```powershell
.\setup_env.ps1
.\run_ide.ps1
```

La instalación manual equivalente es:

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\activate
python -m pip install -r requirements.txt
python -m ide.main
```

También se puede ejecutar el compilador directamente:

```powershell
python skuld_compiler.py --lexico examples\prueba_estandar.stn
python skuld_compiler.py --sintactico examples\prueba_estandar.stn
python skuld_compiler.py --semantico examples\prueba_estandar.stn
```

## Arquitectura

```text
Código fuente (.stn)
        |
        v
Analizador léxico -> tokens
        |
        v
Analizador sintáctico -> AST
        |
        v
Analizador semántico -> AST anotado + tabla de símbolos + errores
        |
        v
IDE / salida de consola
```

El IDE puede usar el compilador externo definido en `SKULD_COMPILER_CMD`.
Si la variable no existe, utiliza automáticamente `skuld_compiler.py` ubicado
en la raíz del proyecto.

```powershell
$env:SKULD_COMPILER_CMD="C:\ruta\a\tu\compilador.exe"
```

## Lenguaje Skuld soportado

### Tipos y palabras reservadas

| Categoría | Elementos |
|---|---|
| Tipos | `int`, `float`, `bool`, `string`, `void` |
| Estructura | `function`, `main`, `return` |
| Control | `if`, `else`, `while`, `do`, `until` |
| Entrada y salida | `cin`, `cout` |
| Booleanos | `true`, `false` |
| Operadores lógicos por palabra | `and`, `or`, `not` |

También se reconocen los operadores simbólicos `&&`, `||` y `!`.

### Declaraciones y funciones

Las variables pueden declararse con o sin inicialización:

```text
int edad = 20;
float temperatura = 36.5;
bool activo = true;
string mensaje = "Hola";
```

Las funciones tienen tipo de retorno, nombre, parámetros y un bloque:

```text
function bool es_mayor(int valor, int limite) {
    return valor > limite;
}
```

El programa principal se escribe con `main`:

```text
main {
    bool mayor = es_mayor(edad, 18);
    cout("Resultado");
}
```

### Sentencias y expresiones

El parser reconoce:

- Asignaciones simples y compuestas: `=`, `+=`, `-=`, `*=`, `/=`, `%=`.
- Incremento y decremento: `++` y `--`.
- Operaciones aritméticas: `+`, `-`, `*`, `/`, `%`.
- Comparaciones: `<`, `<=`, `>`, `>=`, `==`, `!=`.
- Operaciones lógicas: `&&`, `||`, `!`, `and`, `or`, `not`.
- Condicionales `if` / `else`.
- Ciclos `while`.
- Ciclos `do` / `until`.
- Entrada mediante `cin`.
- Salida mediante `cout`.
- Llamadas a funciones y valores de retorno.
- Literales enteros, flotantes, booleanos y cadenas.
- Comentarios ignorados por el lexer.

Un programa completo de ejemplo se encuentra en
[`examples/prueba_estandar.stn`](D:/Compiladores-Skuld-/examples/prueba_estandar.stn).

## Funcionamiento del compilador

### 1. Análisis léxico

`SkuldLexer` recorre el código fuente y genera tokens con:

- Tipo de token.
- Lexema original.
- Línea.
- Columna inicial y final.

Reconoce identificadores, palabras reservadas, literales numéricos y de
cadena, operadores y delimitadores. El lexer también puede recuperarse de
errores y continuar para reportar más de un problema.

Los errores léxicos se muestran con este formato:

```text
ERROR_LEXICO(linea, columna): descripción -> 'lexema'
```

### 2. Análisis sintáctico

`SkuldParser` es un parser descendente recursivo. Consume los tokens y
construye un Árbol Sintáctico Abstracto (AST) con nodos para:

- Declaraciones de variables y funciones.
- Bloques y programa principal.
- Asignaciones.
- Condicionales y ciclos.
- Entrada, salida y retornos.
- Literales, identificadores, llamadas y operaciones.

Los errores sintácticos se acumulan y el parser intenta sincronizarse para
continuar el análisis:

```text
ERROR_SINTACTICO(linea, columna): descripción -> 'lexema'
```

La fase guarda el árbol textual en una carpeta `ast` junto al archivo fuente:

```text
examples/ast/prueba_estandar.ast.txt
```

La CLI también acepta como entrada un archivo que ya tenga el formato de
tokens producido por el análisis léxico.

### 3. Análisis semántico

`SemanticAnalyzer` conserva el AST original, crea una copia anotada y realiza:

- Registro y búsqueda de variables y funciones.
- Manejo de ámbitos anidados.
- Detección de identificadores no declarados.
- Detección de declaraciones duplicadas.
- Verificación de tipos en declaraciones y asignaciones.
- Verificación de tipos en operaciones aritméticas, relacionales y lógicas.
- Verificación de condiciones booleanas en `if`, `while` y `do`.
- Verificación de argumentos y valores de retorno.
- Propagación de atributos de tipo, ámbito y valor constante.

Los nombres visibles de tipos son `int`, `float`, `bool`, `string` y `void`.
Internamente se normalizan algunos tipos para mantener compatibilidad con la
implementación anterior.

La fase produce:

```text
examples/ast/prueba_estandar.ast_annotated.txt
examples/ast/prueba_estandar.symbols.txt
```

Los errores semánticos usan el formato:

```text
ERROR_SEMANTICO(linea, columna): descripción -> 'lexema'
```

## Tabla de símbolos

La tabla de símbolos mantiene la información de variables y funciones
encontradas durante el análisis. Cada entrada puede incluir:

- Nombre.
- Tipo.
- Clase de símbolo.
- Ámbito.
- Línea de declaración.
- Parámetros y tipo de retorno cuando corresponde.
- Valor constante cuando puede determinarse.

La tabla puede consultarse desde la salida de la CLI o desde la pestaña
**Símbolos** del IDE.

## Interfaz gráfica

El IDE permite:

### Archivos y edición

- Crear archivos nuevos.
- Abrir archivos individuales.
- Abrir carpetas y navegar en el explorador.
- Guardar y usar **Guardar como**.
- Cerrar pestañas.
- Arrastrar archivos al explorador o al editor.
- Detectar cambios externos y recargar archivos.
- Autoguardado configurable.
- Fuente, tamaño, zoom y tema configurables.

### Paneles

- Editor con numeración de líneas.
- Resaltado de sintaxis.
- Explorador de archivos.
- Panel de analizadores.
- Terminal y consola.
- Lista de errores.
- Resultado léxico.
- Resultado sintáctico.
- AST anotado del análisis semántico.
- Tabla de símbolos.

Los errores reportados por las fases se pueden seleccionar para saltar a la
línea correspondiente del editor y se resaltan visualmente.

### Atajos

| Atajo | Acción |
|---|---|
| `Ctrl+N` | Nuevo archivo |
| `Ctrl+O` | Abrir archivo |
| `Ctrl+S` | Guardar |
| `Ctrl+Shift+S` | Guardar como |
| `Ctrl+F` | Buscar |
| `Ctrl+G` | Ir a una línea |
| `Ctrl+1` | Mostrar u ocultar analizadores |
| `Ctrl+2` | Mostrar u ocultar terminal |
| `Ctrl+3` | Mostrar u ocultar explorador |

## Fases disponibles y pendientes

Actualmente están implementadas y conectadas:

- Análisis léxico.
- Análisis sintáctico.
- Análisis semántico.
- Visualización del AST y del AST anotado.
- Tabla de símbolos.
- Reporte y resaltado de errores.

La interfaz ya reserva acciones para **Código intermedio** y **Ejecución**,
pero esas fases todavía no están implementadas en el compilador actual. No
deben considerarse funcionalidad terminada.

## Estructura del proyecto

```text
.
├── analizadores/
│   ├── analisis_lexico/
│   │   └── skuld_lexer.py
│   ├── analisis_sintactico/
│   │   └── skuld_parser.py
│   └── analisis_semantico/
│       ├── semantic_analyzer.py
│       └── symbol_table.py
├── ide/
│   ├── main.py
│   ├── main_window.py
│   ├── compiler_runner.py
│   ├── code_editor.py
│   ├── analysis_panel.py
│   └── console_panel.py
├── examples/
├── skuld_compiler.py
├── requirements.txt
├── setup_env.ps1
└── run_ide.ps1
```

## Archivos generados

Los siguientes archivos son temporales o específicos de cada instalación y
están excluidos por `.gitignore`:

- `venv/`, `.venv/`, `.venv311/`.
- `__pycache__/` y `*.pyc`.
- `.pytest_cache/`.
- `build/`, `dist/`.
- `*.dist-info/`, `*.egg-info/`, `*.whl` y `*.egg`.
- Resultados de análisis generados dentro de carpetas `ast/`; estos archivos
  pueden conservarse como evidencia de las fases ejecutadas.

Cada integrante debe ejecutar la instalación localmente; no se deben subir
entornos virtuales ni paquetes instalados al repositorio.
