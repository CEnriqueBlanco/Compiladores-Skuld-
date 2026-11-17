; Código TM de pila generado para ejercicio1_inverso.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
lda a
inp
sto
lda b
inp
sto
lda c
inp
sto
lda d
inp
sto
ldc 'Orden inverso:'
outc
lod d
out
lod c
out
lod b
out
lod a
out
stp
