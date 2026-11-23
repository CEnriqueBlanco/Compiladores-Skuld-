; Código TM de pila generado para ejercicio1_promedio_alumno.stn
; ldc n: cargar constante | lod x: cargar variable
; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos
lda suma
ldc 0.0
sto
lda promedio
ldc 0.0
sto
ldc 'Escribe la matricula del alumno:\\n'
outc
lda matricula
inp
sto
ldc 'Escribe la calificacion 1:\\n'
outc
lda c1
inp
sto
ldc 'Escribe la calificacion 2:\\n'
outc
lda c2
inp
sto
ldc 'Escribe la calificacion 3:\\n'
outc
lda c3
inp
sto
ldc 'Escribe la calificacion 4:\\n'
outc
lda c4
inp
sto
ldc 'Escribe la calificacion 5:\\n'
outc
lda c5
inp
sto
lda suma
lod c1
lod c2
adi
lod c3
adi
lod c4
adi
lod c5
adi
sto
lda promedio
lod suma
ldc 5.0
dvi
sto
ldc 'Matricula:\\n'
outc
lod matricula
out
ldc '\\n'
outc
ldc 'Promedio:\\n'
outc
lod promedio
out
stp
