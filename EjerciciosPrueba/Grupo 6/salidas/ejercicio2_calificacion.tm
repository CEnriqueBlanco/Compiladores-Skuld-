; Código TM de pila generado para ejercicio2_calificacion.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
ldc 'Escribe la calificacion del examen:\\n'
outc
lda calificacion
inp
sto
lod calificacion
ldc 8.0
geq
fjp L1
lda resultado
ldc 1
sto
ujp L2
lab L1
lda resultado
ldc 0
sto
lab L2
ldc 'Aprobado=1, Reprobado=0:\\n'
outc
lod resultado
out
stp
