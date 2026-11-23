; Código TM de pila generado para ejercicio5_produccion_fabricas.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
lda mayor_total
ldc 0.0
ldc 1.0
sbi
sto
lda mayor_clave
ldc 0
sto
ldc 'PRODUCCION ANUAL DE FABRICAS\\n'
outc
ldc 'Escribe el numero de fabricas:\\n'
outc
lda n
inp
sto
lda i
ldc 1
sto
lab L1
lod i
lod n
leq
fjp L2
ldc 'Fabrica numero:\\n'
outc
lod i
out
ldc '\\n'
outc
ldc 'Escribe la clave de esta fabrica:\\n'
outc
lda clave
inp
sto
lda total
ldc 0.0
sto
lda julio
ldc 0.0
sto
lda mes
ldc 1
sto
lab L3
lod mes
ldc 12
leq
fjp L4
lod mes
ldc 1
equ
fjp L5
ldc 'Produccion de enero:\\n'
outc
lab L5
lod mes
ldc 2
equ
fjp L7
ldc 'Produccion de febrero:\\n'
outc
lab L7
lod mes
ldc 3
equ
fjp L9
ldc 'Produccion de marzo:\\n'
outc
lab L9
lod mes
ldc 4
equ
fjp L11
ldc 'Produccion de abril:\\n'
outc
lab L11
lod mes
ldc 5
equ
fjp L13
ldc 'Produccion de mayo:\\n'
outc
lab L13
lod mes
ldc 6
equ
fjp L15
ldc 'Produccion de junio:\\n'
outc
lab L15
lod mes
ldc 7
equ
fjp L17
ldc 'Produccion de julio:\\n'
outc
lab L17
lod mes
ldc 8
equ
fjp L19
ldc 'Produccion de agosto:\\n'
outc
lab L19
lod mes
ldc 9
equ
fjp L21
ldc 'Produccion de septiembre:\\n'
outc
lab L21
lod mes
ldc 10
equ
fjp L23
ldc 'Produccion de octubre:\\n'
outc
lab L23
lod mes
ldc 11
equ
fjp L25
ldc 'Produccion de noviembre:\\n'
outc
lab L25
lod mes
ldc 12
equ
fjp L27
ldc 'Produccion de diciembre:\\n'
outc
lab L27
lda produccion
inp
sto
lda total
lod total
lod produccion
adi
sto
lod mes
ldc 7
equ
fjp L29
lda julio
lod produccion
sto
lab L29
lda mes
lod mes
ldc 1
adi
sto
ujp L3
lab L4
ldc 'Resultado de la fabrica:\\n'
outc
lod clave
out
ldc '\\n'
outc
ldc 'Produccion total anual:\\n'
outc
lod total
out
ldc '\\n'
outc
lod total
lod mayor_total
grt
fjp L31
lda mayor_total
lod total
sto
lda mayor_clave
lod clave
sto
lab L31
lod julio
ldc 3000000.0
grt
fjp L33
ldc 'Fabrica con julio mayor a 3000000:\\n'
outc
lod clave
out
lab L33
lda i
lod i
ldc 1
adi
sto
ujp L1
lab L2
ldc 'Fabrica con mayor produccion anual:\\n'
outc
lod mayor_clave
out
ldc '\\n'
outc
ldc 'Total producido:\\n'
outc
lod mayor_total
out
stp
