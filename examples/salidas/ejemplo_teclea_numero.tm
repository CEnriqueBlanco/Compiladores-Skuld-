; Código TM de pila generado para ejemplo_teclea_numero.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
ldc 'Teclea un numero: '
outc
lda n
inp
sto
ldc 'El doble del numero es: '
outc
lda doble
lod n
ldc 2
mpi
sto
lod doble
out
stp
