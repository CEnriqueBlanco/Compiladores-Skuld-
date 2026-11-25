# Skuld

Skuld es un lenguaje educativo compilado por un proyecto en Python que incluye
analizadores léxico, sintáctico y semántico, generación de código intermedio,
código para Tiny Machine y una interfaz gráfica con PyQt5.

## Contenido

- [Inicio rápido](#inicio-rápido)
- [Estructura del proyecto](#estructura-del-proyecto)
- [Archivos fuente](#archivos-fuente)
- [Programa mínimo](#programa-mínimo)
- [Tipos de datos](#tipos-de-datos)
- [Variables](#variables)
- [Entrada y salida](#entrada-y-salida)
- [Operadores](#operadores)
- [Condicionales](#condicionales)
- [Ciclos](#ciclos)
- [Funciones](#funciones)
- [Comentarios](#comentarios)
- [Precedencia de expresiones](#precedencia-de-expresiones)
- [Errores](#errores)
- [IDE](#ide)
- [Compilación desde terminal](#compilación-desde-terminal)
- [Crear ejecutable para Windows](#crear-ejecutable-para-windows)
- [Ejercicios](#ejercicios)

## Inicio rápido

Requisitos:

- Python 3.11.
- Las dependencias de `requirements.txt`.

En Windows, desde la raíz del proyecto:

```powershell
.\setup_env.ps1
.\run_ide.ps1
```

También puede abrirse manualmente:

```powershell
py -3.11 -m venv .venv311
.venv311\Scripts\activate
python -m pip install -r requirements.txt
python -m ide.main
```

## Estructura del proyecto

```text
.
├── analizadores/
│   ├── analisis_lexico/
│   ├── analisis_sintactico/
│   ├── analisis_semantico/
│   ├── codigo_intermedio/
│   └── generacion_codigo/
├── ejecucion/
├── ide/
├── EjerciciosPrueba/
├── tests/
├── skuld_compiler.py
├── requirements.txt
├── setup_env.ps1
└── run_ide.ps1
```

## Archivos fuente

Los programas de Skuld pueden guardarse con la extensión `.stn`. Las extensiones
`.txt` también pueden abrirse y compilarse desde la IDE.

Cada sentencia termina con punto y coma `;`, excepto las estructuras de control
como `if`, `while` y las definiciones de función o bloque principal.

## Programa mínimo

```text
main {
    cout << "Hola, mundo:\n";
}
```

También se admite un programa directo sin envolverlo en `main`:

```text
int numero;

cout << "Escribe un numero:\n";
cin >> numero;

cout << "El numero es:\n";
cout << numero;
```

El archivo puede contener declaraciones globales y sentencias sueltas. Para
programas organizados se recomienda usar `main { ... }`.

## Tipos de datos

| Tipo | Descripción | Ejemplo |
|---|---|---|
| `int` | Número entero | `int edad = 20;` |
| `float` | Número decimal | `float precio = 12.50;` |
| `bool` | Valor lógico | `bool activo = true;` |
| `string` | Texto | `string nombre = "Ana";` |
| `void` | Función sin valor de retorno | `function void mostrar() { }` |

Literales admitidos:

```text
10
-25
3.1416
true
false
"Hola"
"Primera linea:\nSegunda linea:"
```

## Variables

Las variables se declaran indicando primero el tipo y después el identificador:

```text
int edad;
float salario;
bool aprobado;
string mensaje;
```

Una variable puede inicializarse al declararse:

```text
int contador = 0;
float total = 0.0;
bool activo = true;
string nombre = "Skuld";
```

Varias variables pueden declararse juntas si se separan por comas:

```text
int a, b, c;
int x = 1, y = 2;
```

Los identificadores deben comenzar con una letra o `_`. Después pueden contener
letras, números o `_`.

Ejemplos válidos:

```text
total
_temporal
dato2
valorPromedio
```

## Entrada y salida

### Leer datos

Use `cin >> nombre;` para leer una variable:

```text
int edad;
cin >> edad;
```

También se acepta la forma de función:

```text
cin(edad);
```

La forma alternativa reconocida por el lexer es:

```text
sphone(edad);
```

### Escribir datos

Use `cout <<` para escribir una cadena o el valor de una variable:

```text
cout << "Introduce tu edad:\n";
cout << edad;
cout << "\n";
```

También se pueden encadenar varios elementos:

```text
cout << "Edad: " << edad << "\n";
```

La forma equivalente con función es:

```text
cout("Edad:", edad);
```

## Operadores

### Operadores aritméticos

| Operador | Acción | Ejemplo |
|---|---|---|
| `+` | Suma | `a + b` |
| `-` | Resta | `a - b` |
| `*` | Multiplicación | `a * b` |
| `/` | División | `a / b` |
| `%` | Residuo | `a % b` |
| `^` | Potencia | `base ^ exponente` |

### Comparación

| Operador | Significado |
|---|---|
| `==` | Igual a |
| `!=` | Diferente de |
| `<` | Menor que |
| `<=` | Menor o igual que |
| `>` | Mayor que |
| `>=` | Mayor o igual que |

### Operadores lógicos

Se puede escribir con símbolos o palabras:

| Símbolo | Palabra | Acción |
|---|---|---|
| `&&` | `and` | Y lógico |
| `\|\|` | `or` | O lógico |
| `!` | `not` | Negación |

Ejemplo:

```text
if (edad >= 18 && activo) {
    cout << "Puede continuar:\n";
}
```

### Asignación

| Operador | Equivalente | Ejemplo |
|---|---|---|
| `=` | Asignación | `x = 10;` |
| `+=` | `x = x + valor` | `x += 5;` |
| `-=` | `x = x - valor` | `x -= 2;` |
| `*=` | `x = x * valor` | `x *= 3;` |
| `/=` | `x = x / valor` | `x /= 2;` |
| `%=` | `x = x % valor` | `x %= 4;` |
| `++` | Incrementa en uno | `contador++;` |
| `--` | Decrementa en uno | `contador--;` |

## Condicionales

### Forma recomendada con llaves

```text
if (nota >= 8.0) {
    cout << "Aprobado:\n";
} else {
    cout << "Reprobado:\n";
}
```

Las llaves pueden omitirse en sentencias simples:

```text
if (x > 0)
    cout << "Positivo:\n";
else
    cout << "No positivo:\n";
```

También pueden usarse las palabras estructurales `then`, `end` y `else`:

```text
if (x > 0) then
    cout << "Positivo:\n";
else
    cout << "No positivo:\n";
end
```

También se reconoce `choice` como alternativa al nombre `if`:

```text
choice (valor == 1) {
    cout << "Uno:\n";
} else {
    cout << "Otro:\n";
}
```

## Ciclos

### `while`

```text
int i = 1;

while (i <= 10) {
    cout << i;
    cout << "\n";
    i++;
}
```

Forma alternativa:

```text
while i <= 10 do
    cout << i;
    i++;
end
```

### `do ... while`

```text
int numero;

do {
    cin >> numero;
} while (numero < 0);
```

### `do ... until`

```text
int opcion;

do {
    cout << "Opcion:\n";
    cin >> opcion;
} until (opcion == 0);
```

Las variantes `loop`, `pulse` y `until` forman parte de los nombres propios del
lenguaje y funcionan como alternativas del parser:

```text
loop (i <= 10) {
    i++;
}
```

## Funciones

Una función se declara con `function`, su tipo de retorno, su nombre y sus
parámetros:

```text
function int suma(int a, int b) {
    return a + b;
}
```

La función debe tener el tipo correspondiente al valor que devuelve:

```text
function float promedio(float a, float b) {
    return (a + b) / 2.0;
}

function void mostrar(int valor) {
    cout << "Valor:\n";
    cout << valor;
}
```

Una función se llama escribiendo su nombre y sus argumentos:

```text
int resultado = suma(10, 20);
mostrar(resultado);
```

La palabra `steiner` es el nombre interno reconocido para `function`:

```text
steiner int duplicar(int valor) {
    return valor * 2;
}
```

## Comentarios

### Comentario de una línea

```text
<> Esto es un comentario
```

### Comentario de varias líneas

```text
<!
Este texto no forma parte del programa.
Puede ocupar varias líneas.
!>
```

Los comentarios son ignorados por el analizador léxico.

## Precedencia de expresiones

La expresión se evalúa de mayor a menor según el siguiente orden:

1. Literales, identificadores y paréntesis.
2. Operador unitario `^`.
3. `*`, `/`, `%`.
4. `+`, `-`.
5. `<`, `<=`, `>`, `>=`, `==`, `!=`.
6. `&&` o `and`.
7. `||` o `or`.
8. Operador unitario `not` o `!`.

Se recomienda usar paréntesis cuando la intención pueda resultar ambigua:

```text
resultado = (a + b) * c;
if ((edad >= 18) && activo) {
    return true;
}
```

## Errores

Las fases reportan errores con la línea y la columna donde se encontraron:

```text
ERROR_LEXICO(linea, columna): descripcion -> 'lexema'
ERROR_SINTACTICO(linea, columna): descripcion -> 'lexema'
ERROR_SEMANTICO(linea, columna): descripcion -> 'lexema'
```

Antes de generar código, el compilador debe superar:

1. El análisis léxico.
2. El análisis sintáctico.
3. El análisis semántico.

## IDE

La interfaz permite:

- Crear, abrir y guardar archivos `.stn`.
- Abrir carpetas y navegar por el explorador.
- Cambiar entre pestañas.
- Usar análisis léxico, sintáctico y semántico.
- Consultar el AST, el AST anotado y la tabla de símbolos.
- Generar código intermedio y código Tiny Machine.
- Ejecutar programas en sesiones separadas; cancelarlas con `Ctrl+C` y cerrarlas con la X.
- Mostrar en rojo la cancelación y su tiempo transcurrido.
- Mostrar u ocultar el explorador, la terminal y los analizadores.

### Atajos

| Atajo | Acción |
|---|---|
| `Ctrl+N` | Nuevo archivo |
| `Ctrl+O` | Abrir archivo |
| `Ctrl+S` | Guardar |
| `Ctrl+Shift+S` | Guardar como |
| `Ctrl+F` | Buscar |
| `Ctrl+G` | Ir a una línea |
| `Ctrl+1` | Alternar analizadores |
| `Ctrl+2` | Alternar terminal |
| `Ctrl+3` | Alternar explorador |

## Compilación desde terminal

Ejecutar una fase léxica:

```powershell
python skuld_compiler.py --lexico "EjerciciosPrueba\Grupo 6\ejercicio5_produccion_fabricas.stn"
```

Ejecutar el análisis sintáctico:

```powershell
python skuld_compiler.py --sintactico "EjerciciosPrueba\Grupo 6\ejercicio5_produccion_fabricas.stn"
```

Ejecutar el análisis semántico:

```powershell
python skuld_compiler.py --semantico "EjerciciosPrueba\Grupo 6\ejercicio5_produccion_fabricas.stn"
```

Generar código intermedio:

```powershell
python skuld_compiler.py --intermedio "EjerciciosPrueba\Grupo 6\ejercicio5_produccion_fabricas.stn"
```

Generar código Tiny Machine:

```powershell
python skuld_compiler.py --tm "EjerciciosPrueba\Grupo 6\ejercicio5_produccion_fabricas.stn"
```

Ejecutar un programa:

```powershell
python skuld_compiler.py --ejecutar "EjerciciosPrueba\Grupo 6\ejercicio5_produccion_fabricas.stn"
```

## Crear ejecutable para Windows

Con el entorno configurado, genera un ejecutable independiente con:

```powershell
.\.venv311\Scripts\python.exe build_exe.py
```

El archivo se crea en `dist\ReadingSteiner.exe`. Se puede abrir con doble clic
y no requiere instalar Python en el equipo donde se ejecuta. La primera apertura
puede tardar unos segundos mientras se cargan los componentes de la interfaz.

## Ejercicios

Los ejercicios conservados están en `EjerciciosPrueba/`. Incluyen práctica de
operaciones aritméticas, condicionales, ciclos, acumuladores, búsqueda del
máximo o mínimo, sucesiones y cálculo de totales.

En este README se recomienda seguir este orden de aprendizaje:

1. Declarar variables e imprimir valores.
2. Leer datos con `cin >>`.
3. Usar operadores aritméticos.
4. Crear decisiones con `if` y `else`.
5. Resolver repeticiones con `while`.
6. Combinar contadores y acumuladores.
7. Crear funciones y usar valores de retorno.
8. Resolver ejercicios con ciclos anidados.
