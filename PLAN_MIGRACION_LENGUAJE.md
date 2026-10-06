# Plan de migracion a palabras reservadas estandar

## Objetivo

Eliminar las palabras reservadas propias de Skuld y usar nombres convencionales de un lenguaje de programacion.

## Vocabulario final

| Uso | Palabra final |
|---|---|
| Entero | `int` |
| Decimal | `float` |
| Booleano | `bool` |
| Cadena | `string` |
| Sin retorno | `void` |
| Funcion | `function` |
| Programa principal | `main` |
| Condicional | `if` / `else` |
| Bucle | `while` |
| Bucle posterior | `do` / `until` |
| Entrada | `cin` |
| Salida | `cout` |
| Retorno | `return` |
| Valores booleanos | `true` / `false` |

## Equivalencias que se eliminaran

- `labmem` -> se elimina; las variables comienzan directamente con su tipo.
- `worldline` -> `int`.
- `divergence` y `real` -> `float`.
- `reading` -> `bool`.
- `steiner` -> `function`.
- `gate` -> `main`.
- `choice` -> `if`.
- `loop` -> `while`.
- `pulse` -> `do`.
- `sphone` -> `cin`.
- `dmail` -> `cout`.

## Orden de trabajo

1. Actualizar el lexer para reconocer solo el vocabulario final.
2. Actualizar el parser para aceptar las palabras estandar y retirar las alternativas antiguas.
3. Normalizar el analizador semantico para reportar `int`, `float` y `bool`.
4. Actualizar la tabla de simbolos y sus tamanos de tipos.
5. Convertir los ejemplos `.stn` y las pruebas del compilador.
6. Actualizar la documentacion y los comandos de prueba.
7. Ejecutar las pruebas lexica, sintactica y semantica con un caso valido y otro invalido.

## Criterio de terminado

- Un programa con palabras estandar pasa las fases lexica, sintactica y semantica.
- Las palabras eliminadas producen un error lexico y ya no se interpretan como palabras reservadas.
- Los errores semanticos se reportan usando `int`, `float` y `bool`.
- No quedan ejemplos principales usando el vocabulario eliminado.
