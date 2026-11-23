; Código TM de pila generado para ejercicio3_costo_hospital.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
ldc 'Escribe el tipo de enfermedad (1-4):\\n'
outc
lda tipo
inp
sto
ldc 'Escribe la edad del paciente:\\n'
outc
lda edad
inp
sto
ldc 'Escribe los dias de internacion:\\n'
outc
lda dias
inp
sto
lod tipo
ldc 1
equ
fjp L1
lda costo_dia
ldc 25.0
sto
ujp L2
lab L1
lod tipo
ldc 2
equ
fjp L3
lda costo_dia
ldc 16.0
sto
ujp L4
lab L3
lod tipo
ldc 3
equ
fjp L5
lda costo_dia
ldc 20.0
sto
ujp L6
lab L5
lod tipo
ldc 4
equ
fjp L7
lda costo_dia
ldc 32.0
sto
ujp L8
lab L7
lda costo_dia
ldc 0.0
sto
lab L8
lab L6
lab L4
lab L2
lda total
lod costo_dia
lod dias
mpi
sto
lod edad
ldc 14
geq
lod edad
ldc 22
leq
and
fjp L9
lda total
lod total
ldc 1.1
mpi
sto
lab L9
ldc 'Costo total del paciente:\\n'
outc
lod total
out
stp
