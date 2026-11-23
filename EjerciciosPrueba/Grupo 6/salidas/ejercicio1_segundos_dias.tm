; Código TM de pila generado para ejercicio1_segundos_dias.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
ldc 'Escribe el numero de dias:\\n'
outc
lda dias
inp
sto
lda segundos
lod dias
ldc 24
mpi
ldc 60
mpi
ldc 60
mpi
sto
ldc 'Segundos:\\n'
outc
lod segundos
out
stp
