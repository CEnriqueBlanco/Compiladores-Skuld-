; Código TM de pila generado para ejercicio2_aumento_categoria.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
ldc 'Escribe la categoria del trabajador (1-4):\\n'
outc
lda categoria
inp
sto
ldc 'Escribe el sueldo del trabajador:\\n'
outc
lda sueldo
inp
sto
lod categoria
ldc 1
equ
fjp L1
lda aumento
lod sueldo
ldc 0.15
mpi
sto
ujp L2
lab L1
lod categoria
ldc 2
equ
fjp L3
lda aumento
lod sueldo
ldc 0.1
mpi
sto
ujp L4
lab L3
lod categoria
ldc 3
equ
fjp L5
lda aumento
lod sueldo
ldc 0.08
mpi
sto
ujp L6
lab L5
lod categoria
ldc 4
equ
fjp L7
lda aumento
lod sueldo
ldc 0.07
mpi
sto
ujp L8
lab L7
lda aumento
ldc 0.0
sto
lab L8
lab L6
lab L4
lab L2
lda nuevo
lod sueldo
lod aumento
adi
sto
ldc 'Categoria:\\n'
outc
lod categoria
out
ldc 'Nuevo sueldo:\\n'
outc
lod nuevo
out
stp
