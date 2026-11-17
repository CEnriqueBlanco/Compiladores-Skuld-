"""
Módulo de utilidades para emisión de instrucciones de la Tiny Machine (TM).
Adaptado fielmente de code.h y code.c de Kenneth C. Louden (tiny-master).
"""

from typing import List, Optional


class TMEmitter:
    # Convención estándar de registros de la Tiny Machine (code.h)
    AC = 0    # Acumulador principal
    AC1 = 1   # Segundo acumulador
    GP = 5    # Global pointer (puntero a datos globales/variables)
    MP = 6    # Memory pointer (puntero al tope de memoria para temporales/pila)
    PC = 7    # Program counter (contador de programa)

    def __init__(self, trace_code: bool = True):
        self.trace_code = trace_code
        self.emit_loc: int = 0
        self.high_emit_loc: int = 0
        # Lista de líneas de código TM generadas
        self.instructions: List[str] = []
        # Mapa de ubicación -> instrucción para backpatching
        self.code_map: dict[int, str] = {}

    def emit_comment(self, comment: str) -> None:
        """Emite una línea de comentario si trace_code está activado."""
        if self.trace_code:
            self.instructions.append(f"* {comment}")

    def emit_ro(self, op: str, r: int, s: int, t: int, comment: str = "") -> None:
        """
        Emite una instrucción Register-Only (RO).
        Formato: i: OP r, s, t
        """
        comment_str = f"\t{comment}" if (self.trace_code and comment) else ""
        line = f"{self.emit_loc:3d}:  {op:5s}  {r},{s},{t} {comment_str}".rstrip()
        self.code_map[self.emit_loc] = line
        self.emit_loc += 1
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_rm(self, op: str, r: int, d: int, s: int, comment: str = "") -> None:
        """
        Emite una instrucción Register-to-Memory (RM / RA).
        Formato: i: OP r, d(s)
        """
        comment_str = f"\t{comment}" if (self.trace_code and comment) else ""
        line = f"{self.emit_loc:3d}:  {op:5s}  {r},{d}({s}) {comment_str}".rstrip()
        self.code_map[self.emit_loc] = line
        self.emit_loc += 1
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def emit_skip(self, how_many: int) -> int:
        """
        Reserva 'how_many' posiciones de instrucción para backpatch posterior.
        Retorna la posición antes del salto.
        """
        loc = self.emit_loc
        self.emit_loc += how_many
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc
        return loc

    def emit_backup(self, loc: int) -> None:
        """Retrocede a una posición previamente reservada."""
        if loc > self.high_emit_loc:
            self.emit_comment("BUG in emit_backup")
        self.emit_loc = loc

    def emit_restore(self) -> None:
        """Restaura la posición de emisión al valor más alto alcanzado."""
        self.emit_loc = self.high_emit_loc

    def emit_rm_abs(self, op: str, r: int, a: int, comment: str = "") -> None:
        """
        Convierte una dirección absoluta a un desplazamiento relativo al PC.
        offset = a - (emit_loc + 1)
        """
        offset = a - (self.emit_loc + 1)
        comment_str = f"\t{comment}" if (self.trace_code and comment) else ""
        line = f"{self.emit_loc:3d}:  {op:5s}  {r},{offset}({self.PC}) {comment_str}".rstrip()
        self.code_map[self.emit_loc] = line
        self.emit_loc += 1
        if self.high_emit_loc < self.emit_loc:
            self.high_emit_loc = self.emit_loc

    def get_code(self) -> str:
        """Compila y retorna el código TM ordenado y completo."""
        lines = []
        # Agrupamos comentarios e instrucciones en orden
        # Si hubo backpatching, code_map tiene las instrucciones por índice
        for i in range(self.high_emit_loc):
            if i in self.code_map:
                lines.append(self.code_map[i])
            else:
                lines.append(f"{i:3d}:  STP  0,0,0 \t* unfilled slot")
        return "\n".join(lines) + "\n"
