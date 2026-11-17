"""Intérprete de la máquina de pila usada por el código TM de Skuld."""

from __future__ import annotations

import ast
from typing import Callable, Optional


class TMMachine:
    """Ejecuta el formato de pila mostrado en la especificación del proyecto."""

    def __init__(self) -> None:
        self.code: list[tuple[str, Optional[str]]] = []
        self.labels: dict[str, int] = {}
        self.stack: list[object] = []
        self.memory: dict[object, object] = {}
        self.output_buffer: list[str] = []

    def reset(self) -> None:
        self.stack = []
        self.memory = {}
        self.output_buffer = []

    def load_code(self, tm_code_or_file: str) -> bool:
        self.reset()
        if "\n" in tm_code_or_file or tm_code_or_file.lstrip().startswith(";"):
            text = tm_code_or_file
        else:
            with open(tm_code_or_file, "r", encoding="utf-8") as code_file:
                text = code_file.read()

        self.code = []
        self.labels = {}
        for line in text.splitlines():
            line = line.strip()
            if not line or line.startswith(";"):
                continue
            parts = line.split(None, 1)
            op = parts[0].lower()
            argument = parts[1].strip() if len(parts) == 2 else None
            if op == "lab":
                if not argument:
                    raise ValueError("La instrucción lab requiere una etiqueta.")
                self.labels[argument] = len(self.code)
                continue
            self.code.append((op, argument))
        return True

    @staticmethod
    def _value(argument: Optional[str]) -> object:
        if argument is None:
            raise ValueError("Falta un operando.")
        try:
            return ast.literal_eval(argument)
        except (ValueError, SyntaxError):
            try:
                return float(argument) if "." in argument else int(argument)
            except ValueError as exc:
                raise ValueError(f"Operando inválido: {argument}") from exc

    def run(
        self,
        input_data: Optional[list[object]] = None,
        input_callback: Optional[Callable[[], object]] = None,
        output_callback: Optional[Callable[[str], None]] = None,
        max_steps: int = 100000,
    ) -> tuple[bool, str, list[str]]:
        self.output_buffer = []
        inputs = list(input_data or [])
        pc = 0
        steps = 0

        def pop_number() -> object:
            if not self.stack:
                raise ValueError("La pila está vacía.")
            return self.stack.pop()

        try:
            while pc < len(self.code) and steps < max_steps:
                op, argument = self.code[pc]
                pc += 1
                steps += 1

                if op in ("stp", "hlt", "halt"):
                    return True, "Halted", self.output_buffer
                if op == "ldc":
                    self.stack.append(self._value(argument))
                elif op == "lod":
                    key = self._address(argument)
                    self.stack.append(self.memory.get(key, 0))
                elif op == "lda":
                    self.stack.append(self._address(argument))
                elif op == "sto":
                    if argument is None:
                        value = pop_number()
                        address = pop_number()
                    else:
                        address = self._address(argument)
                        value = pop_number()
                    self.memory[address] = value
                elif op == "inp":
                    if inputs:
                        self.stack.append(inputs.pop(0))
                    elif input_callback:
                        self.stack.append(input_callback())
                    else:
                        try:
                            self.stack.append(float(input("TM IN? ")))
                        except (EOFError, ValueError):
                            self.stack.append(0)
                elif op in ("out", "outc"):
                    value = pop_number()
                    text = str(value) if op == "out" else str(value)
                    self.output_buffer.append(text)
                    if output_callback:
                        output_callback(text + ("" if op == "outc" else "\n"))
                elif op in ("adi", "sbi", "mpi", "dvi", "mod", "les", "leq", "grt", "geq", "equ", "neq", "and", "orr"):
                    right = pop_number()
                    left = pop_number()
                    if op == "adi":
                        result = left + right
                    elif op == "sbi":
                        result = left - right
                    elif op == "mpi":
                        result = left * right
                    elif op in ("dvi", "mod"):
                        if right == 0:
                            return False, "Division por cero", self.output_buffer
                        if op == "dvi":
                            result = (
                                left // right
                                if isinstance(left, int) and isinstance(right, int)
                                else left / right
                            )
                        else:
                            result = left % right
                    elif op == "les":
                        result = left < right
                    elif op == "leq":
                        result = left <= right
                    elif op == "grt":
                        result = left > right
                    elif op == "geq":
                        result = left >= right
                    elif op == "equ":
                        result = left == right
                    elif op == "neq":
                        result = left != right
                    elif op == "and":
                        result = bool(left and right)
                    else:
                        result = bool(left or right)
                    self.stack.append(result)
                elif op == "not":
                    self.stack.append(not pop_number())
                elif op == "fjp":
                    if not bool(pop_number()):
                        pc = self.labels[argument or ""]
                elif op == "ujp":
                    pc = self.labels[argument or ""]
                else:
                    return False, f"Instrucción desconocida: {op}", self.output_buffer
        except (KeyError, TypeError, ValueError, IndexError) as exc:
            return False, str(exc), self.output_buffer

        if steps >= max_steps:
            return False, "Se excedió el máximo de pasos (posible ciclo infinito)", self.output_buffer
        return False, f"El programa terminó sin stp (PC={pc})", self.output_buffer

    @staticmethod
    def _address(argument: Optional[str]) -> object:
        if argument is None:
            raise ValueError("Falta una dirección de memoria.")
        try:
            return int(argument)
        except ValueError:
            return argument
