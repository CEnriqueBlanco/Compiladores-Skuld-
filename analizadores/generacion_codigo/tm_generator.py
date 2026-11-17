"""Generador de código P para la máquina de pila de Skuld."""

from __future__ import annotations

from typing import Dict, Optional

from analizadores.analisis_sintactico.skuld_parser import TreeNode
from analizadores.analisis_semantico.symbol_table import SymbolTable


class TMGenerator:
    """Genera instrucciones de pila como ldc, lod, sto, adi y fjp."""

    def __init__(self) -> None:
        self.instructions: list[str] = []
        self.symbol_table: Optional[SymbolTable] = None
        self.var_locations: Dict[tuple[str, str], int] = {}
        self.next_location = 0
        self.label_count = 0

    def _emit(self, instruction: str) -> None:
        self.instructions.append(instruction)

    def _new_label(self) -> str:
        self.label_count += 1
        return f"L{self.label_count}"

    def _setup_memory(self) -> None:
        if self.symbol_table is None:
            return
        for symbol in self.symbol_table.all_symbols:
            if not symbol.is_function:
                self.var_locations[(symbol.scope_name, symbol.name)] = self.next_location
                self.next_location += 1

    def _location(self, name: str, scope: str = "global") -> int:
        for candidate in (scope, "main", "gate", "global"):
            location = self.var_locations.get((candidate, name))
            if location is not None:
                return location
        for (candidate_scope, candidate_name), location in self.var_locations.items():
            if candidate_name == name:
                return location
        raise ValueError(f"El identificador '{name}' no tiene dirección de memoria.")

    def _variable(self, name: str, scope: str) -> str:
        self._location(name, scope)
        return name

    def generate(
        self,
        tree: TreeNode,
        symbol_table: SymbolTable,
        filename: str = "program.stn",
    ) -> str:
        self.instructions = [
            f"; Código TM de pila generado para {filename}",
            "; ldc n: cargar constante | lod x: cargar variable",
            "; lda x: cargar dirección | sto: guardar | fjp/ujp: saltos",
        ]
        self.symbol_table = symbol_table
        self.var_locations = {}
        self.next_location = 0
        self.label_count = 0
        self._setup_memory()
        self._gen(tree)
        self._emit("stp")
        return "\n".join(self.instructions) + "\n"

    def _gen(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return
        if node.nodekind == "StmtK":
            self._gen_stmt(node)
        elif node.nodekind == "ExpK":
            self._gen_exp(node)
        elif node.nodekind == "DeclK":
            self._gen_decl(node)

    def _gen_decl(self, node: TreeNode) -> None:
        if node.kind == "DeclVarK":
            for child in node.child:
                self._gen_decl(child)
        elif node.kind == "VarK" and node.child:
            scope = getattr(node, "attr_scope", "global")
            self._emit(f"lda {self._variable(node.name or '', scope)}")
            self._gen(node.child[0])
            self._emit("sto")
        elif node.kind == "FuncK":
            for child in node.child:
                self._gen(child)

    def _gen_stmt(self, node: TreeNode) -> None:
        scope = getattr(node, "attr_scope", "global")
        kind = node.kind

        if kind == "BlockK":
            for child in node.child:
                self._gen(child)
        elif kind == "AssignK":
            self._emit(f"lda {self._variable(node.name or '', scope)}")
            if node.child:
                self._gen(node.child[0])
            self._emit("sto")
        elif kind == "ReadK":
            self._emit(f"lda {self._variable(node.name or '', scope)}")
            self._emit("inp")
            self._emit("sto")
        elif kind == "WriteK":
            for child in node.child:
                if child.kind == "StringK":
                    self._emit(f"ldc {child.val!r}")
                    self._emit("outc")
                else:
                    self._gen(child)
                    self._emit("out")
        elif kind == "IfK":
            condition = node.child[0] if node.child else None
            then_branch = node.child[1] if len(node.child) > 1 else None
            else_branch = node.child[2] if len(node.child) > 2 else None
            else_label = self._new_label()
            end_label = self._new_label()
            self._gen(condition)
            self._emit(f"fjp {else_label}")
            self._gen(then_branch)
            if else_branch is not None:
                self._emit(f"ujp {end_label}")
                self._emit(f"lab {else_label}")
                self._gen(else_branch)
                self._emit(f"lab {end_label}")
            else:
                self._emit(f"lab {else_label}")
        elif kind == "WhileK":
            condition = node.child[0] if node.child else None
            body = node.child[1] if len(node.child) > 1 else None
            start_label = self._new_label()
            end_label = self._new_label()
            self._emit(f"lab {start_label}")
            self._gen(condition)
            self._emit(f"fjp {end_label}")
            self._gen(body)
            self._emit(f"ujp {start_label}")
            self._emit(f"lab {end_label}")
        elif kind in ("DoWhileK", "RepeatK"):
            body = node.child[0] if node.child else None
            condition = node.child[1] if len(node.child) > 1 else None
            start_label = self._new_label()
            self._emit(f"lab {start_label}")
            self._gen(body)
            self._gen(condition)
            self._emit(f"fjp {start_label}")
        elif kind == "ReturnK" and node.child:
            self._gen(node.child[0])

    def _gen_exp(self, node: TreeNode) -> None:
        scope = getattr(node, "attr_scope", "global")
        if node.kind == "ConstK":
            self._emit(f"ldc {node.val!r}" if isinstance(node.val, str) else f"ldc {node.val}")
        elif node.kind == "StringK":
            self._emit(f"ldc {node.val!r}")
        elif node.kind == "IdK":
            self._emit(f"lod {self._variable(node.name or '', scope)}")
        elif node.kind == "OpK":
            for child in node.child[:2]:
                self._gen(child)
            operations = {
                "+": "adi", "-": "sbi", "*": "mpi", "/": "dvi", "%": "mod",
                "<": "les", "<=": "leq", ">": "grt", ">=": "geq",
                "==": "equ", "!=": "neq", "&&": "and", "and": "and",
                "||": "orr", "or": "orr",
            }
            if node.op == "!":
                self._emit("not")
            elif node.op in operations:
                self._emit(operations[node.op])
            else:
                raise ValueError(f"Operador no soportado por la TM de pila: {node.op}")
        elif node.kind == "CallK":
            raise ValueError("Las llamadas a funciones todavía no están soportadas por la TM de pila.")
