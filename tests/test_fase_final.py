import unittest
from analizadores.analisis_lexico.skuld_lexer import tokenize_file_with_recovery
from analizadores.analisis_sintactico.skuld_parser import SkuldParser
from analizadores.analisis_semantico.semantic_analyzer import SemanticAnalyzer
from analizadores.codigo_intermedio.generator import IntermediateCodeGenerator
from analizadores.generacion_codigo.tm_generator import TMGenerator
from ejecucion.tm_machine import TMMachine


def compile_and_run(file_path: str, inputs: list[int]) -> list[str]:
    tokens, lex_errs = tokenize_file_with_recovery(file_path)
    assert not lex_errs, f"Lex errors: {lex_errs}"
    ast = SkuldParser(tokens).parse()
    ann_ast, symtab, sem_errs = SemanticAnalyzer().analyze(ast)
    assert not sem_errs, f"Semantic errors: {sem_errs}"
    
    ci = IntermediateCodeGenerator().generate(ann_ast, symtab)
    assert len(ci) > 0, "Empty CI"

    tm_code = TMGenerator().generate(ann_ast, symtab, file_path)
    assert len(tm_code) > 0, "Empty TM code"

    machine = TMMachine()
    machine.load_code(tm_code)
    success, status, outputs = machine.run(input_data=inputs)
    assert success, f"Execution failed: {status}"
    return outputs


class TestCompiladorSkuldFaseFinal(unittest.TestCase):
    def test_factorial(self):
        # 5! = 120
        out = compile_and_run("Ejemplosv2/factorial_tiny.stn", [5])
        self.assertEqual(out, ["120"])

    def test_ejercicio1_inverso(self):
        # Invertir 10, 20, 30, 40 -> 40, 30, 20, 10
        out = compile_and_run("examples/ejercicio1_inverso.stn", [10, 20, 30, 40])
        self.assertEqual(out, ["40", "30", "20", "10"])

    def test_ejercicio2_signo_positivo(self):
        out = compile_and_run("examples/ejercicio2_signo.stn", [45])
        self.assertEqual(out, ["0"])

    def test_ejercicio2_signo_negativo(self):
        out = compile_and_run("examples/ejercicio2_signo.stn", [-7])
        self.assertEqual(out, ["1"])

    def test_ejercicio2_signo_nulo(self):
        out = compile_and_run("examples/ejercicio2_signo.stn", [0])
        self.assertEqual(out, ["2"])

    def test_ejercicio3_creciente(self):
        # 1, 5, 9 -> 1
        out = compile_and_run("examples/ejercicio3_creciente.stn", [1, 5, 9])
        self.assertEqual(out, ["1"])
        # 5, 2, 9 -> 0
        out = compile_and_run("examples/ejercicio3_creciente.stn", [5, 2, 9])
        self.assertEqual(out, ["0"])

    def test_ejercicio4_fibonacci(self):
        # Fibonacci(7) = 13 (0, 1, 1, 2, 3, 5, 8, 13)
        out = compile_and_run("examples/ejercicio4_fibonacci.stn", [7])
        self.assertEqual(out, ["13"])
        # Fibonacci(0) = 0
        out = compile_and_run("examples/ejercicio4_fibonacci.stn", [0])
        self.assertEqual(out, ["0"])

    def test_ejercicio5_ulam(self):
        # ULAM para 6: 6, 3, 10, 5, 16, 8, 4, 2, 1
        out = compile_and_run("examples/ejercicio5_ulam.stn", [6])
        self.assertEqual(out, ["6", "3", "10", "5", "16", "8", "4", "2", "1"])

    def test_codigo_tm_usa_instrucciones_de_pila(self):
        tokens, lex_errs = tokenize_file_with_recovery("examples/ejemplo_teclea_numero.stn")
        self.assertFalse(lex_errs)
        ast = SkuldParser(tokens).parse()
        ann_ast, symtab, sem_errs = SemanticAnalyzer().analyze(ast)
        self.assertFalse(sem_errs)

        code = TMGenerator().generate(ann_ast, symtab)

        self.assertIn("lda n", code)
        self.assertIn("lod n", code)
        self.assertIn("mpi", code)
        self.assertNotIn("LD     ", code)


if __name__ == "__main__":
    unittest.main()
