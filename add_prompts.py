from pathlib import Path
import re

root = Path("EjerciciosPrueba")
prompts = {
    "Grupo 1/ejercicio1_inverso.stn": [
        "Escribe el primer numero:",
        "Escribe el segundo numero:",
        "Escribe el tercer numero:",
        "Escribe el cuarto numero:",
    ],
    "Grupo 1/ejercicio2_signo.stn": ["Escribe un numero entero:"],
    "Grupo 1/ejercicio3_creciente.stn": [
        "Escribe el primer numero entero:",
        "Escribe el segundo numero entero:",
        "Escribe el tercer numero entero:",
    ],
    "Grupo 1/ejercicio4_fibonacci.stn": ["Escribe el valor de N:"],
    "Grupo 1/ejercicio5_lluvias.stn": [
        "Escribe la lluvia de NORTE:",
        "Escribe la lluvia de CENTRO:",
        "Escribe la lluvia de SUR:",
    ],
    "Grupo 2/ejercicio1_promedio_alumno.stn": [
        "Escribe la matricula del alumno:",
        "Escribe la calificacion 1:",
        "Escribe la calificacion 2:",
        "Escribe la calificacion 3:",
        "Escribe la calificacion 4:",
        "Escribe la calificacion 5:",
    ],
    "Grupo 2/ejercicio2_temperatura_grillo.stn": ["Escribe el numero de sonidos por minuto:"],
    "Grupo 2/ejercicio3_impuesto_articulo.stn": ["Escribe el costo basico del articulo:"],
    "Grupo 2/ejercicio4_llamadas_telefonicas.stn": [
        "Escribe el tipo de llamada (1=Internacional, 2=Nacional, 3=Local, -1=Terminar):",
        "Escribe la duracion en minutos:",
        "Escribe el tipo de la siguiente llamada (1=Internacional, 2=Nacional, 3=Local, -1=Terminar):",
    ],
    "Grupo 2/ejercicio5_produccion_vino.stn": [
        "Escribe el numero de anios:",
        "Escribe la produccion del vino tipo 1:",
        "Escribe la produccion del vino tipo 2:",
        "Escribe la produccion del vino tipo 3:",
        "Escribe la produccion del vino tipo 4:",
        "Escribe la produccion del vino tipo 5:",
    ],
    "Grupo 3/ejercicio1_rectangulo.stn": [
        "Escribe la base del rectangulo:",
        "Escribe la altura del rectangulo:",
    ],
    "Grupo 3/ejercicio2_orden_descendente.stn": [
        "Escribe el primer numero entero:",
        "Escribe el segundo numero entero:",
        "Escribe el tercer numero entero:",
    ],
    "Grupo 3/ejercicio3_mayor_de_tres.stn": [
        "Escribe el primer numero real:",
        "Escribe el segundo numero real:",
        "Escribe el tercer numero real:",
    ],
    "Grupo 3/ejercicio4_serie_potencias.stn": ["Escribe el valor de N:"],
    "Grupo 3/ejercicio5_produccion_fabricas.stn": [
        "Escribe el numero de fabricas:",
        "Escribe la clave de la fabrica:",
        "Escribe la produccion del mes:",
    ],
    "Grupo 4/ejercicio1_dinosaurio.stn": [
        "Escribe el peso en libras:",
        "Escribe la longitud en pies:",
    ],
    "Grupo 4/ejercicio2_funcion_val.stn": [
        "Escribe el valor de NUM:",
        "Escribe el valor de V:",
    ],
    "Grupo 4/ejercicio3_pago_trabajador.stn": [
        "Escribe la categoria del trabajador:",
        "Escribe el sueldo del trabajador:",
        "Escribe las horas extras trabajadas:",
    ],
    "Grupo 4/ejercicio4_ventas_rangos.stn": [
        "Escribe el monto de la venta (-1 para terminar):",
        "Escribe el monto de la siguiente venta (-1 para terminar):",
    ],
    "Grupo 4/ejercicio5_estadio.stn": [
        "Escribe el precio de la localidad 1:",
        "Escribe el precio de la localidad 2:",
        "Escribe el precio de la localidad 3:",
        "Escribe el precio de la localidad 4:",
        "Escribe el precio de la localidad 5:",
        "Escribe la clave de la localidad (1-5, -1 para terminar):",
        "Escribe la cantidad de boletos (-1 para terminar):",
        "Escribe la clave de la siguiente venta (1-5, -1 para terminar):",
        "Escribe la cantidad de boletos de la siguiente venta (-1 para terminar):",
    ],
    "Grupo 5/ejercicio1_cilindro.stn": [
        "Escribe el radio del cilindro:",
        "Escribe la altura del cilindro:",
    ],
    "Grupo 5/ejercicio2_aumento_sueldo.stn": ["Escribe el sueldo del trabajador:"],
    "Grupo 5/ejercicio3_facultades_menores.stn": [
        "Escribe la matricula del alumno:",
        "Escribe la carrera (1=Economia, 2=Computacion, 3=Administracion, 4=Contabilidad):",
        "Escribe el semestre:",
        "Escribe el promedio:",
    ],
    "Grupo 5/ejercicio4_mayor_menor.stn": [
        "Escribe la cantidad N de numeros:",
        "Escribe el primer numero:",
        "Escribe el siguiente numero:",
    ],
    "Grupo 5/ejercicio5_produccion_vino.stn": [
        "Escribe el numero de anios:",
        "Escribe la produccion del vino tipo 1:",
        "Escribe la produccion del vino tipo 2:",
        "Escribe la produccion del vino tipo 3:",
        "Escribe la produccion del vino tipo 4:",
        "Escribe la produccion del vino tipo 5:",
    ],
    "Grupo 6/ejercicio1_segundos_dias.stn": ["Escribe el numero de dias:"],
    "Grupo 6/ejercicio2_calificacion.stn": ["Escribe la calificacion del examen:"],
    "Grupo 6/ejercicio3_costo_hospital.stn": [
        "Escribe el tipo de enfermedad (1-4):",
        "Escribe la edad del paciente:",
        "Escribe los dias de internacion:",
    ],
    "Grupo 6/ejercicio4_serie_armonica.stn": ["Escribe el valor de N:"],
    "Grupo 6/ejercicio5_produccion_fabricas.stn": [
        "Escribe el numero de fabricas:",
        "Escribe la clave de la fabrica:",
        "Escribe la produccion del mes:",
    ],
    "Grupo 7/ejercicio1_expresion_ab.stn": [
        "Escribe el valor de A:",
        "Escribe el valor de B:",
    ],
    "Grupo 7/ejercicio2_signo.stn": ["Escribe un numero entero:"],
    "Grupo 7/ejercicio3_orden_ascendente.stn": [
        "Escribe el primer numero entero:",
        "Escribe el segundo numero entero:",
        "Escribe el tercer numero entero:",
    ],
    "Grupo 7/ejercicio4_eleccion.stn": [
        "Escribe un voto (1-4, 0 para terminar):",
        "Escribe el siguiente voto (1-4, 0 para terminar):",
    ],
    "Grupo 7/ejercicio5_produccion_fabricas.stn": [
        "Escribe el numero de fabricas:",
        "Escribe la clave de la fabrica:",
        "Escribe la produccion del mes:",
    ],
    "Grupo 8/ejercicio1_cambio.stn": [
        "Escribe el costo del articulo:",
        "Escribe la cantidad de dinero entregada:",
    ],
    "Grupo 8/ejercicio2_expresion_pq.stn": [
        "Escribe el valor de P:",
        "Escribe el valor de Q:",
    ],
    "Grupo 8/ejercicio3_descuento_compra.stn": ["Escribe el monto de la compra:"],
    "Grupo 8/ejercicio4_contar_ceros.stn": [
        "Escribe un numero (-1 para terminar):",
        "Escribe el siguiente numero (-1 para terminar):",
    ],
    "Grupo 8/ejercicio5_produccion_vino.stn": [
        "Escribe el numero de anios:",
        "Escribe la produccion del vino tipo 1:",
        "Escribe la produccion del vino tipo 2:",
        "Escribe la produccion del vino tipo 3:",
        "Escribe la produccion del vino tipo 4:",
        "Escribe la produccion del vino tipo 5:",
    ],
    "Grupo 9/ejercicio1_cilindro.stn": [
        "Escribe el radio del cilindro:",
        "Escribe la altura del cilindro:",
    ],
    "Grupo 9/ejercicio2_temperatura_grillo.stn": ["Escribe el numero de sonidos por minuto:"],
    "Grupo 9/ejercicio3_impuesto_articulo.stn": ["Escribe el costo basico del articulo:"],
    "Grupo 9/ejercicio4_contar_primos.stn": ["Escribe el valor de M:"],
    "Grupo 9/ejercicio5_lluvias.stn": [
        "Escribe la lluvia de NORTE:",
        "Escribe la lluvia de CENTRO:",
        "Escribe la lluvia de SUR:",
    ],
    "Grupo 10/ejercicio1_rectangulo.stn": [
        "Escribe la base del rectangulo:",
        "Escribe la altura del rectangulo:",
    ],
    "Grupo 10/ejercicio2_aumento_categoria.stn": [
        "Escribe la categoria del trabajador (1-4):",
        "Escribe el sueldo del trabajador:",
    ],
    "Grupo 10/ejercicio3_mayor_de_tres.stn": [
        "Escribe el primer numero real:",
        "Escribe el segundo numero real:",
        "Escribe el tercer numero real:",
    ],
    "Grupo 10/ejercicio4_numeros_perfectos.stn": ["Escribe el valor de N:"],
    "Grupo 10/ejercicio5_estadio.stn": [
        "Escribe el precio de la localidad 1:",
        "Escribe el precio de la localidad 2:",
        "Escribe el precio de la localidad 3:",
        "Escribe el precio de la localidad 4:",
        "Escribe el precio de la localidad 5:",
        "Escribe la clave de la localidad (1-5, -1 para terminar):",
        "Escribe la cantidad de boletos (-1 para terminar):",
        "Escribe la clave de la siguiente venta (1-5, -1 para terminar):",
        "Escribe la cantidad de boletos de la siguiente venta (-1 para terminar):",
    ],
    "Grupo 11/ejercicio1_cambio.stn": [
        "Escribe el costo del articulo:",
        "Escribe la cantidad de dinero entregada:",
    ],
    "Grupo 11/ejercicio2_aumento_categoria.stn": [
        "Escribe la categoria del trabajador (1-4):",
        "Escribe el sueldo del trabajador:",
    ],
    "Grupo 11/ejercicio3_llamada_internacional.stn": [
        "Escribe la clave de la zona:",
        "Escribe los minutos hablados:",
    ],
    "Grupo 11/ejercicio4_sucesion_ulam.stn": ["Escribe un entero positivo:"],
    "Grupo 11/ejercicio5_lluvias.stn": [
        "Escribe la lluvia de NORTE:",
        "Escribe la lluvia de CENTRO:",
        "Escribe la lluvia de SUR:",
    ],
    "Grupo 12/ejercicio1_expresion_ab.stn": [
        "Escribe el valor de A:",
        "Escribe el valor de B:",
    ],
    "Grupo 12/ejercicio2_expresion_pq.stn": [
        "Escribe el valor de P:",
        "Escribe el valor de Q:",
    ],
    "Grupo 12/ejercicio3_descuento_compra.stn": ["Escribe el monto de la compra:"],
    "Grupo 12/ejercicio4_eleccion.stn": [
        "Escribe un voto (1-4, 0 para terminar):",
        "Escribe el siguiente voto (1-4, 0 para terminar):",
    ],
    "Grupo 12/ejercicio5_estadio.stn": [
        "Escribe el precio de la localidad 1:",
        "Escribe el precio de la localidad 2:",
        "Escribe el precio de la localidad 3:",
        "Escribe el precio de la localidad 4:",
        "Escribe el precio de la localidad 5:",
        "Escribe la clave de la localidad (1-5, -1 para terminar):",
        "Escribe la cantidad de boletos (-1 para terminar):",
        "Escribe la clave de la siguiente venta (1-5, -1 para terminar):",
        "Escribe la cantidad de boletos de la siguiente venta (-1 para terminar):",
    ],
}

files = sorted(root.glob("Grupo */ejercicio*.stn"))
assert len(files) == 60, len(files)
for path in files:
    rel = path.relative_to(root).as_posix()
    ps = prompts.get(rel)
    if ps is None:
        raise SystemExit(f"Falta lista de prompts: {rel}")
    lines = path.read_text(encoding="utf-8").splitlines()
    cin_count = sum(1 for line in lines if "cin >>" in line)
    if cin_count != len(ps):
        raise SystemExit(f"{rel}: {cin_count} cin, {len(ps)} prompts")

    out = []
    pi = 0
    for line in lines:
        if "cin >>" in line:
            indent = line[: len(line) - len(line.lstrip())]
            out.append(f'{indent}cout << "{ps[pi]}";')
            pi += 1
        out.append(line)
    text = "\n".join(out) + "\n"
    text = re.sub(
        r'cout << "([^"]*)";',
        lambda m: 'cout << "' + m.group(1) + '\\n";',
        text,
    )
    path.write_text(text, encoding="utf-8")

print("prompts y saltos de linea agregados a", len(files), "archivos")
