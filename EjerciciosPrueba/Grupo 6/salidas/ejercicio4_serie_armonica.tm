; Código TM de pila generado para ejercicio4_serie_armonica.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
lda suma
ldc 0.0
sto
ldc 'Escribe el valor de N:\\n'
outc
lda n
inp
sto
lda i
ldc 1
sto
lda signo
ldc 1
sto
lab L1
lod i
lod n
leq
fjp L2
lod signo
ldc 1
equ
fjp L3
lda suma
lod suma
ldc 1.0
lod i
dvi
adi
sto
ujp L4
lab L3
lda suma
lod suma
ldc 1.0
lod i
dvi
sbi
sto
lab L4
lda signo
ldc 0
lod signo
sbi
sto
lda i
lod i
ldc 1
adi
sto
ujp L1
lab L2
ldc 'Resultado de la serie:\\n'
outc
lod suma
out
stp
