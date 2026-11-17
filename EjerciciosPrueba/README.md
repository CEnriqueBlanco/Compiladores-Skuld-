# Ejercicios finales de Compiladores II

Este directorio organiza los ejercicios del archivo
`EjericiosFinalesCompisII.pdf` por grupo. Cada grupo contiene cinco
programas escritos en el lenguaje Skuld con extension `.stn`.

## Estructura

- `Grupo 1` a `Grupo 12`: contienen los ejercicios 1 a 5 de cada grupo.
- `Grupo 13`, `Grupo 14` y `Grupo 15`: se crearon porque fueron solicitados,
  pero el PDF original solamente contiene ejercicios hasta el Grupo 12. En
  esas carpetas se incluye una nota.

En cada grupo:

- El ejercicio 1 es secuencial.
- Los ejercicios 2 y 3 usan estructuras selectivas (`if` / `else`).
- Los ejercicios 4 y 5 usan estructuras repetitivas (`while`).

## Como compilar y ejecutar

Desde la raiz del proyecto:

```powershell
python skuld_compiler.py --semantico "EjerciciosPrueba/Grupo 1/ejercicio1_inverso.stn"
python skuld_compiler.py --ejecutar "EjerciciosPrueba/Grupo 1/ejercicio1_inverso.stn"
```

Tambien se puede abrir cualquier archivo `.stn` desde el IDE.

## Datos de entrada

Los programas leen los datos con `cin`. Algunos ejercicios repetitivos
terminan con un centinela:

- Llamadas telefonicas: tipo `-1`.
- Ventas: monto `-1`.
- Conteo de ceros: numero `-1`.
- Ventas del estadio: pareja `-1 -1`.
- Fabricas: primero el numero de fabricas y luego, por cada fabrica, su clave
  y las 12 producciones mensuales.
- Vinos: primero el numero de anios y luego, por cada anio, las cantidades de
  los cinco tipos de vino.
- Lluvias: 12 registros de NORTE, 12 de CENTRO y 12 de SUR, en ese orden.

Los programas usan solamente variables escalares, `if` / `else`, `while`,
`cin` y `cout`, porque el generador TM actual no soporta arreglos ni llamadas
a funciones. Para evitar el manejo de signos unarios que no esta implementado
en el generador TM, las constantes negativas se escriben como `0 - 1`.

Todos los programas fueron validados con las fases lexica, sintactica,
semantica, generacion TM y ejecucion en la maquina TM.
