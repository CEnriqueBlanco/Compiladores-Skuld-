"""
Generador de Código Intermedio de Tres Direcciones (3AC) para Skuld.
Produce sentencias con variables temporales (t1, t2...) y etiquetas (L1, L2...).
"""

from typing import List, Optional
from analizadores.analisis_sintactico.skuld_parser import TreeNode
from analizadores.analisis_semantico.symbol_table import SymbolTable


class IntermediateCodeGenerator:
    def __init__(self):
        self.temp_count = 0
        self.label_count = 0
        self.instructions: List[str] = []

    def new_temp(self) -> str:
        self.temp_count += 1
        return f"t{self.temp_count}"

    def new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def emit(self, instr: str) -> None:
        self.instructions.append(instr)

    @staticmethod
    def _format_string(value: object) -> str:
        return "'" + str(value).replace("'", "\\'") + "'"

    def generate(self, tree: TreeNode, symbol_table: Optional[SymbolTable] = None) -> str:
        self.temp_count = 0
        self.label_count = 0
        self.instructions = []
        self._gen(tree)
        return "\n".join(self.instructions) + "\n"

    def _gen(self, node: Optional[TreeNode]) -> Optional[str]:
        if node is None:
            return None

        if node.nodekind == "StmtK":
            return self._gen_stmt(node)
        elif node.nodekind == "ExpK":
            return self._gen_exp(node)
        elif node.nodekind == "DeclK":
            return self._gen_decl(node)
        return None

    def _gen_decl(self, node: TreeNode) -> None:
        if node.kind == "DeclVarK":
            for c in node.child:
                self._gen_decl(c)
        elif node.kind == "VarK":
            if node.child:
                val = self._gen(node.child[0])
                if val:
                    self.emit(f"{node.name} = {val}")
        elif node.kind == "FuncK":
            self.emit(f"function {node.name}:")
            for c in node.child:
                self._gen(c)

    def _gen_stmt(self, node: TreeNode) -> None:
        if node.kind == "BlockK":
            for c in node.child:
                self._gen(c)

        elif node.kind == "AssignK":
            val = self._gen(node.child[0]) if node.child else ""
            self.emit(f"{node.name} = {val}")

        elif node.kind == "ReadK":
            self.emit(f"read {node.name}")

        elif node.kind == "WriteK":
            for c in node.child:
                val = self._gen(c)
                self.emit(f"write {val}")

        elif node.kind == "IfK":
            p_cond = node.child[0] if len(node.child) > 0 else None
            p_then = node.child[1] if len(node.child) > 1 else None
            p_else = node.child[2] if len(node.child) > 2 else None

            cond_val = self._gen(p_cond)
            label_else = self.new_label()
            label_end = self.new_label()

            if p_else:
                self.emit(f"ifFalse {cond_val} goto {label_else}")
                self._gen(p_then)
                self.emit(f"goto {label_end}")
                self.emit(f"{label_else}:")
                self._gen(p_else)
                self.emit(f"{label_end}:")
            else:
                self.emit(f"ifFalse {cond_val} goto {label_end}")
                self._gen(p_then)
                self.emit(f"{label_end}:")

        elif node.kind == "WhileK":
            p_cond = node.child[0] if len(node.child) > 0 else None
            p_body = node.child[1] if len(node.child) > 1 else None

            label_start = self.new_label()
            label_end = self.new_label()

            self.emit(f"{label_start}:")
            cond_val = self._gen(p_cond)
            self.emit(f"ifFalse {cond_val} goto {label_end}")
            self._gen(p_body)
            self.emit(f"goto {label_start}")
            self.emit(f"{label_end}:")

        elif node.kind in ("DoWhileK", "RepeatK"):
            p_body = node.child[0] if len(node.child) > 0 else None
            p_cond = node.child[1] if len(node.child) > 1 else None

            label_start = self.new_label()
            self.emit(f"{label_start}:")
            self._gen(p_body)
            cond_val = self._gen(p_cond)
            # Repeat until cond => repetir mientras sea falso
            self.emit(f"ifFalse {cond_val} goto {label_start}")

        elif node.kind == "ReturnK":
            if node.child:
                val = self._gen(node.child[0])
                self.emit(f"return {val}")
            else:
                self.emit("return")

    def _gen_exp(self, node: TreeNode) -> str:
        if node.kind == "ConstK":
            return str(node.val)
        elif node.kind == "IdK":
            return node.name or ""
        elif node.kind == "StringK":
            return self._format_string(node.val)
        elif node.kind == "OpK":
            p1 = self._gen(node.child[0]) if len(node.child) > 0 else ""
            p2 = self._gen(node.child[1]) if len(node.child) > 1 else ""
            t = self.new_temp()
            self.emit(f"{t} = {p1} {node.op} {p2}")
            return t
        elif node.kind == "CallK":
            args = []
            for c in node.child:
                arg_val = self._gen(c)
                args.append(arg_val)
            t = self.new_temp()
            self.emit(f"{t} = call {node.name}({', '.join(str(a) for a in args)})")
            return t
        return ""
