import unittest

from analizadores.analisis_lexico.skuld_lexer import tokenize_file_with_recovery
from analizadores.analisis_sintactico.skuld_parser import SkuldParser
from analizadores.analisis_semantico.semantic_analyzer import SemanticAnalyzer
from analizadores.generacion_codigo.tm_generator import TMGenerator
from ejecucion.tm_machine import TMMachine


def compile_and_run(file_path: str, inputs: list[object]) -> list[str]:
    tokens, lex_errors = tokenize_file_with_recovery(file_path)
    assert not lex_errors, f"Lex errors: {lex_errors}"

    parser = SkuldParser(tokens)
    ast = parser.parse()
    assert not parser.errors, f"Syntax errors: {parser.errors}"

    annotated_ast, symbol_table, semantic_errors = SemanticAnalyzer().analyze(ast)
    assert not semantic_errors, f"Semantic errors: {semantic_errors}"

    tm_code = TMGenerator().generate(annotated_ast, symbol_table, file_path)
    assert tm_code

    machine = TMMachine()
    machine.load_code(tm_code)
    success, status, outputs = machine.run(input_data=inputs)
    assert success, f"Execution failed: {status}"
    return outputs


class TestEjerciciosGrupo6(unittest.TestCase):
    base = "EjerciciosPrueba/Grupo 6"

    def test_segundos_por_dias(self):
        outputs = compile_and_run(f"{self.base}/ejercicio1_segundos_dias.stn", [2])
        self.assertIn("172800", outputs)

    def test_calificacion_aprobada(self):
        outputs = compile_and_run(f"{self.base}/ejercicio2_calificacion.stn", [8])
        self.assertIn("1", outputs)

    def test_calificacion_reprobada(self):
        outputs = compile_and_run(f"{self.base}/ejercicio2_calificacion.stn", [7])
        self.assertIn("0", outputs)

    def test_costo_hospital(self):
        outputs = compile_and_run(
            f"{self.base}/ejercicio3_costo_hospital.stn",
            [1, 20, 2],
        )
        self.assertIn("55.00000000000001", outputs)

    def test_serie_armonica(self):
        outputs = compile_and_run(f"{self.base}/ejercicio4_serie_armonica.stn", [2])
        self.assertTrue(outputs)

    def test_codigo_tm_grupo6(self):
        file_path = f"{self.base}/ejercicio5_produccion_fabricas.stn"
        tokens, lex_errors = tokenize_file_with_recovery(file_path)
        self.assertFalse(lex_errors)

        parser = SkuldParser(tokens)
        ast = parser.parse()
        self.assertFalse(parser.errors)

        annotated_ast, symbol_table, semantic_errors = SemanticAnalyzer().analyze(ast)
        self.assertFalse(semantic_errors)

        code = TMGenerator().generate(annotated_ast, symbol_table, file_path)
        self.assertIn("Produccion de enero", code)
        self.assertIn("Produccion de julio", code)


if __name__ == "__main__":
    unittest.main()
