# Instrucciones TM de Skuld

El código TM de Skuld utiliza una **máquina de pila**. Las instrucciones
trabajan con una pila de valores y con la memoria de las variables.

## Memoria y pila

- **Pila:** guarda constantes, variables y resultados temporales.
- **Memoria:** guarda los valores de las variables.
- `lda` coloca una dirección en la pila.
- `sto` guarda un valor en esa dirección.

## Carga y almacenamiento

| Instrucción | Función | Ejemplo |
|---|---|---|
| `ldc n` | Carga una constante en la pila. | `ldc 5` |
| `lod x` | Carga el valor de la variable `x`. | `lod x` |
| `lda x` | Carga la dirección de la variable `x`. | `lda x` |
| `sto` | Guarda el valor en la dirección que está en la pila. | `sto` |

Ejemplo de asignación:

```text
lda x
ldc 5
sto
```

Equivale a:

```text
x = 5;
```

## Operaciones aritméticas

Estas instrucciones toman dos valores de la pila, realizan la operación y
colocan el resultado nuevamente en la pila.

| Instrucción | Función |
|---|---|
| `adi` | Suma |
| `sbi` | Resta |
| `mpi` | Multiplicación |
| `dvi` | División |
| `mod` | Módulo o residuo |

Ejemplo:

```text
ldc 4
ldc 3
adi
```

Resultado en la pila: `7`.

## Operaciones relacionales y lógicas

El resultado de estas instrucciones es verdadero o falso.

| Instrucción | Función |
|---|---|
| `les` | Menor que (`<`) |
| `leq` | Menor o igual que (`<=`) |
| `grt` | Mayor que (`>`) |
| `geq` | Mayor o igual que (`>=`) |
| `equ` | Igual (`==`) |
| `neq` | Distinto (`!=`) |
| `and` | AND lógico |
| `orr` | OR lógico |
| `not` | Negación lógica |

Ejemplo:

```text
lod x
ldc 10
les
```

Comprueba si `x < 10`.

## Saltos y etiquetas

| Instrucción | Función |
|---|---|
| `lab L1` | Define la etiqueta `L1`. |
| `fjp L1` | Salta a `L1` si el valor de la pila es falso. |
| `ujp L1` | Salta siempre a `L1`. |

Ejemplo de un `if`:

```text
lod x
ldc 0
grt
fjp L1
ldc 'positivo'
outc
ujp L2
lab L1
ldc 'no positivo'
outc
lab L2
```

## Entrada y salida

| Instrucción | Función |
|---|---|
| `inp` | Lee un dato del usuario y lo coloca en la pila. |
| `out` | Muestra un valor numérico de la pila. |
| `outc` | Muestra una cadena de texto de la pila, respetando `\n`. |

Entrada de una variable:

```text
lda n
inp
sto
```

Equivale a:

```text
cin >> n;
```

Salida de texto:

```text
ldc 'Resultado:\n'
outc
```

La máquina no agrega saltos automáticamente. El salto ocurre únicamente si
el texto del programa contiene `\n`.

Salida de un número:

```text
lod n
out
```

## Finalización

| Instrucción | Función |
|---|---|
| `stp` | Detiene la ejecución del programa. |

Todo programa TM generado por Skuld termina con:

```text
stp
```

## Ejemplo completo

Programa fuente:

```text
int n;
cin >> n;
cout << "Doble: ";
cout << n * 2;
```

Código TM equivalente:

```text
lda n
inp
sto
ldc 'Doble: '
outc
lod n
ldc 2
mpi
out
stp
```
