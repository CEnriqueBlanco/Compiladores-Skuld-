; Código TM de pila generado para ejercicio1_cambio.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
ldc 'Escribe el costo del articulo:\\n'
outc
lda costo
inp
sto
ldc 'Escribe la cantidad de dinero entregada:\\n'
outc
lda pago
inp
sto
lda cambio
lod pago
lod costo
sbi
sto
ldc 'Cambio:\\n'
outc
lod cambio
out
stp
