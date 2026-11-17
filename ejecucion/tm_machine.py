"""
Simulador de la Tiny Machine (TM).
Portado fielmente de TM.C de Kenneth C. Louden (tiny-master).
"""

from typing import List, Tuple, Optional, Callable


class TMInstruction:
    def __init__(self, op: str, arg1: int, arg2: int, arg3: int):
        self.op: str = op
        self.arg1: int = arg1
        self.arg2: int = arg2
        self.arg3: int = arg3

    def __repr__(self) -> str:
        return f"{self.op} {self.arg1}, {self.arg2}, {self.arg3}"


class TMMachine:
    IADDR_SIZE = 1024
    DADDR_SIZE = 1024
    NO_REGS = 8
    PC_REG = 7

    def __init__(self):
        self.i_mem: List[TMInstruction] = [TMInstruction("HALT", 0, 0, 0) for _ in range(self.IADDR_SIZE)]
        self.d_mem: List[int] = [0] * self.DADDR_SIZE
        self.reg: List[int] = [0] * self.NO_REGS
        self.output_buffer: List[str] = []
        self.input_queue: List[int] = []

    def reset(self) -> None:
        """Reinicia el estado de la máquina."""
        self.d_mem = [0] * self.DADDR_SIZE
        self.d_mem[0] = self.DADDR_SIZE - 1  # maxaddress inicial
        self.reg = [0] * self.NO_REGS
        self.output_buffer = []

    def load_code(self, tm_code_or_file: str) -> bool:
        """
        Lee el código TM (ya sea un string o una ruta de archivo) y llena i_mem.
        Retorna True si la carga fue exitosa.
        """
        self.reset()
        lines = []
        if "\n" in tm_code_or_file or tm_code_or_file.strip().startswith("*") or (len(tm_code_or_file) > 0 and tm_code_or_file[0].isdigit()):
            lines = tm_code_or_file.splitlines()
        else:
            with open(tm_code_or_file, "r", encoding="utf-8") as f:
                lines = f.readlines()

        for line in lines:
            line = line.strip()
            if not line or line.startswith("*"):
                continue

            # Remover comentarios si empiezan por * o si hay tab/espacio con comentario
            # En CGEN/TMEmitter el comentario va tras tabulación o espacio con comentario
            if "\t" in line:
                line = line[:line.index("\t")].strip()
            elif "*" in line:
                line = line[:line.index("*")].strip()

            parts = line.split(":", 1)
            if len(parts) != 2:
                continue

            try:
                loc = int(parts[0].strip())
            except ValueError:
                continue

            rest = parts[1].strip()
            tokens = rest.split(None, 1)
            if not tokens:
                continue

            op = tokens[0].upper()
            args_str = tokens[1].strip() if len(tokens) > 1 else ""

            # Analizar argumentos
            r = s = t = d = 0
            if op in ("HALT", "IN", "OUT", "OUTC", "ADD", "SUB", "MUL", "DIV"):
                # Formato RO: r, s, t
                sub_args = [a.strip() for a in args_str.split(",") if a.strip()]
                if len(sub_args) >= 1:
                    r = int(sub_args[0])
                if len(sub_args) >= 2:
                    s = int(sub_args[1])
                if len(sub_args) >= 3:
                    t = int(sub_args[2])
                instr = TMInstruction(op, r, s, t)

            elif op in ("LD", "ST", "LDA", "LDC", "JLT", "JLE", "JGT", "JGE", "JEQ", "JNE"):
                # Formato RM / RA: r, d(s)
                sub_args = args_str.split(",", 1)
                r = int(sub_args[0].strip()) if len(sub_args) > 0 else 0
                if len(sub_args) > 1:
                    ds_part = sub_args[1].strip()
                    if "(" in ds_part and ds_part.endswith(")"):
                        d_str, s_str = ds_part[:-1].split("(")
                        d = int(d_str.strip())
                        s = int(s_str.strip())
                    else:
                        d = int(ds_part)
                        s = 0
                instr = TMInstruction(op, r, d, s)
            else:
                continue

            if 0 <= loc < self.IADDR_SIZE:
                self.i_mem[loc] = instr

        return True

    def run(
        self,
        input_data: Optional[List[int]] = None,
        input_callback: Optional[Callable[[], int]] = None,
        output_callback: Optional[Callable[[str], None]] = None,
        max_steps: int = 100000
    ) -> Tuple[bool, str, List[str]]:
        """
        Ejecuta las instrucciones en i_mem.
        Retorna (éxito, mensaje_estado, lista_salida_OUT).
        """
        self.d_mem[0] = self.DADDR_SIZE - 1
        self.output_buffer = []
        if input_data:
            self.input_queue = list(input_data)
        else:
            self.input_queue = []

        step_count = 0
        while step_count < max_steps:
            pc = self.reg[self.PC_REG]
            if not (0 <= pc < self.IADDR_SIZE):
                return False, f"Instruction Memory Fault en PC={pc}", self.output_buffer

            instr = self.i_mem[pc]
            self.reg[self.PC_REG] += 1
            step_count += 1

            op = instr.op
            r = instr.arg1
            s = instr.arg2
            t = instr.arg3

            # Instrucciones RR
            if op == "HALT":
                return True, "Halted", self.output_buffer

            elif op == "IN":
                val = 0
                if self.input_queue:
                    val = self.input_queue.pop(0)
                elif input_callback:
                    val = input_callback()
                else:
                    try:
                        val = int(input("TM IN? "))
                    except Exception:
                        val = 0
                self.reg[r] = val

            elif op == "OUT":
                out_val = self.reg[r]
                val_str = str(out_val)
                self.output_buffer.append(val_str)
                if output_callback:
                    output_callback(val_str + "\n")

            elif op == "OUTC":
                # Imprimir caracter ASCII
                char_val = chr(self.reg[r] & 0xFF)
                if self.output_buffer and not self.output_buffer[-1].endswith("\n"):
                    self.output_buffer[-1] += char_val
                else:
                    self.output_buffer.append(char_val)
                if output_callback:
                    output_callback(char_val)

            elif op == "ADD":
                self.reg[r] = self.reg[s] + self.reg[t]
            elif op == "SUB":
                self.reg[r] = self.reg[s] - self.reg[t]
            elif op == "MUL":
                self.reg[r] = self.reg[s] * self.reg[t]
            elif op == "DIV":
                if self.reg[t] == 0:
                    return False, "Division by 0", self.output_buffer
                self.reg[r] = self.reg[s] // self.reg[t]

            # Instrucciones RM / RA: s es registro base, arg2 es d (desplazamiento)
            elif op == "LD":
                d = instr.arg2
                s_reg = instr.arg3
                addr = d + self.reg[s_reg]
                if not (0 <= addr < self.DADDR_SIZE):
                    return False, f"Data Memory Fault en dirección={addr}", self.output_buffer
                self.reg[r] = self.d_mem[addr]

            elif op == "ST":
                d = instr.arg2
                s_reg = instr.arg3
                addr = d + self.reg[s_reg]
                if not (0 <= addr < self.DADDR_SIZE):
                    return False, f"Data Memory Fault en dirección={addr}", self.output_buffer
                self.d_mem[addr] = self.reg[r]

            elif op == "LDA":
                d = instr.arg2
                s_reg = instr.arg3
                self.reg[r] = d + self.reg[s_reg]

            elif op == "LDC":
                d = instr.arg2
                self.reg[r] = d

            # Saltos condicionales RA
            elif op == "JLT":
                d = instr.arg2
                s_reg = instr.arg3
                if self.reg[r] < 0:
                    self.reg[self.PC_REG] = d + self.reg[s_reg]

            elif op == "JLE":
                d = instr.arg2
                s_reg = instr.arg3
                if self.reg[r] <= 0:
                    self.reg[self.PC_REG] = d + self.reg[s_reg]

            elif op == "JGT":
                d = instr.arg2
                s_reg = instr.arg3
                if self.reg[r] > 0:
                    self.reg[self.PC_REG] = d + self.reg[s_reg]

            elif op == "JGE":
                d = instr.arg2
                s_reg = instr.arg3
                if self.reg[r] >= 0:
                    self.reg[self.PC_REG] = d + self.reg[s_reg]

            elif op == "JEQ":
                d = instr.arg2
                s_reg = instr.arg3
                if self.reg[r] == 0:
                    self.reg[self.PC_REG] = d + self.reg[s_reg]

            elif op == "JNE":
                d = instr.arg2
                s_reg = instr.arg3
                if self.reg[r] != 0:
                    self.reg[self.PC_REG] = d + self.reg[s_reg]

        return False, "Exceeded maximum step count (posible bucle infinito)", self.output_buffer
