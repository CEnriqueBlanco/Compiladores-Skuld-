"""
Generador de código para la máquina Tiny Machine (TM).
Adaptado a la estructura del AST anotado y Tabla de Símbolos del compilador Skuld.
"""

from typing import Optional, Dict
from analizadores.analisis_sintactico.skuld_parser import TreeNode
from analizadores.analisis_semantico.symbol_table import SymbolTable, Symbol
from analizadores.generacion_codigo.tm_emitter import TMEmitter


class TMGenerator:
    def __init__(self, trace_code: bool = True):
        self.emitter = TMEmitter(trace_code=trace_code)
        self.tmp_offset = 0
        self.symbol_table: Optional[SymbolTable] = None
        self.var_loc_map: Dict[str, int] = {}

    def _setup_memory_locations(self) -> None:
        """
        Asigna una ubicación de memoria por variable (offset secuencial 0, 1, 2... para TM).
        """
        if not self.symbol_table:
            return

        next_loc = 0
        for sym in self.symbol_table.all_symbols:
            if not sym.is_function:
                # Si no está aún mapeado con ubicación TM
                key = (sym.scope_name, sym.name)
                if key not in self.var_loc_map:
                    self.var_loc_map[key] = next_loc
                    next_loc += 1

    def _get_var_loc(self, name: str, scope: str = "global") -> int:
        """Obtiene la dirección de memoria TM asignada para una variable."""
        # Primero buscar en scope actual
        if (scope, name) in self.var_loc_map:
            return self.var_loc_map[(scope, name)]
        # Luego en main
        if ("main", name) in self.var_loc_map:
            return self.var_loc_map[("main", name)]
        # Luego en global
        if ("global", name) in self.var_loc_map:
            return self.var_loc_map[("global", name)]
        # Fallback: buscar por sólo nombre
        for (sc, n), loc in self.var_loc_map.items():
            if n == name:
                return loc

        # Si no existía, asignar una nueva
        new_loc = len(self.var_loc_map)
        self.var_loc_map[(scope, name)] = new_loc
        return new_loc

    def generate(self, tree: TreeNode, symbol_table: SymbolTable, filename: str = "program.stn") -> str:
        """Punto de entrada principal para generar el código TM."""
        self.symbol_table = symbol_table
        self.emitter = TMEmitter(trace_code=True)
        self.tmp_offset = 0
        self.var_loc_map = {}

        self._setup_memory_locations()

        self.emitter.emit_comment("==================================================")
        self.emitter.emit_comment("Skuld Compiler to TM Code Generation")
        self.emitter.emit_comment(f"File: {filename}")
        self.emitter.emit_comment("==================================================")

        # Preludio estándar
        self.emitter.emit_comment("Standard prelude:")
        self.emitter.emit_rm("LD", TMEmitter.MP, 0, TMEmitter.AC, "load maxaddress from location 0")
        self.emitter.emit_rm("ST", TMEmitter.AC, 0, TMEmitter.AC, "clear location 0")
        self.emitter.emit_comment("End of standard prelude.")

        # Recorrer el árbol
        self._cgen(tree)

        # Finalizar ejecución
        self.emitter.emit_comment("End of execution:")
        self.emitter.emit_ro("HALT", 0, 0, 0, "Fin del programa")

        return self.emitter.get_code()

    def _cgen(self, node: Optional[TreeNode]) -> None:
        """Recorrido recursivo del AST para generación de código."""
        if node is None:
            return

        if node.nodekind == "StmtK":
            self._gen_stmt(node)
        elif node.nodekind == "ExpK":
            self._gen_exp(node)
        elif node.nodekind == "DeclK":
            self._gen_decl(node)

    def _gen_decl(self, node: TreeNode) -> None:
        """Generación de declaraciones."""
        scope = getattr(node, "attr_scope", "global")
        if node.kind == "DeclVarK":
            for c in node.child:
                self._gen_decl(c)
        elif node.kind == "VarK":
            # Si tiene inicialización (primer hijo)
            if node.child:
                self._cgen(node.child[0])
                loc = self._get_var_loc(node.name, scope)
                self.emitter.emit_rm("ST", TMEmitter.AC, loc, TMEmitter.GP, f"assign: init {node.name}")
        elif node.kind == "FuncK":
            # Por el momento funciones como inline o cuerpo directo si es llamado
            for c in node.child:
                self._cgen(c)

    def _gen_stmt(self, node: TreeNode) -> None:
        """Generación de sentencias."""
        scope = getattr(node, "attr_scope", "global")

        if node.kind == "BlockK":
            # Recorrer todos los hijos secuencialmente
            for c in node.child:
                self._cgen(c)

        elif node.kind == "AssignK":
            self.emitter.emit_comment(f"-> assign to {node.name}")
            if node.child:
                self._cgen(node.child[0])
            loc = self._get_var_loc(node.name, scope)
            self.emitter.emit_rm("ST", TMEmitter.AC, loc, TMEmitter.GP, f"assign: store to {node.name}")
            self.emitter.emit_comment("<- assign")

        elif node.kind == "ReadK":
            # cin / sphone
            self.emitter.emit_ro("IN", TMEmitter.AC, 0, 0, f"read integer for {node.name}")
            loc = self._get_var_loc(node.name, scope)
            self.emitter.emit_rm("ST", TMEmitter.AC, loc, TMEmitter.GP, f"read: store to {node.name}")

        elif node.kind == "WriteK":
            # cout / dmail
            self.emitter.emit_comment("-> cout")
            for c in node.child:
                if c.kind == "StringK":
                    # Emitir comentarios y caracteres con OUTC si es cadena
                    text = str(c.val)
                    self.emitter.emit_comment(f"print string: {text}")
                    for ch in text:
                        ascii_code = ord(ch)
                        self.emitter.emit_rm("LDC", TMEmitter.AC, ascii_code, 0, f"char '{ch}'")
                        self.emitter.emit_ro("OUTC", TMEmitter.AC, 0, 0, "write char")
                elif c.kind == "OpK" and c.op == "+" and any(sub.kind == "StringK" for sub in c.child if sub):
                    # Concatenación con string (ej: "Resultado: " + x)
                    for sub in c.child:
                        if sub.kind == "StringK":
                            for ch in str(sub.val):
                                self.emitter.emit_rm("LDC", TMEmitter.AC, ord(ch), 0, f"char '{ch}'")
                                self.emitter.emit_ro("OUTC", TMEmitter.AC, 0, 0, "write char")
                        else:
                            self._cgen(sub)
                            self.emitter.emit_ro("OUT", TMEmitter.AC, 0, 0, "write ac")
                else:
                    self._cgen(c)
                    self.emitter.emit_ro("OUT", TMEmitter.AC, 0, 0, "write ac")
            self.emitter.emit_comment("<- cout")

        elif node.kind == "IfK":
            self.emitter.emit_comment("-> if")
            # En Skuld AST: child[0] = condición (o BlockK Condition), child[1] = then, child[2] = else (opcional)
            p_cond = node.child[0] if len(node.child) > 0 else None
            p_then = node.child[1] if len(node.child) > 1 else None
            p_else = node.child[2] if len(node.child) > 2 else None

            # 1. Evaluar condición en AC
            self._cgen(p_cond)

            # 2. Reservar salto si es falso (AC == 0)
            saved_loc1 = self.emitter.emit_skip(1)
            self.emitter.emit_comment("if: jump to else/end if condition false")

            # 3. Generar cuerpo Then
            if p_then:
                self._cgen(p_then)

            if p_else:
                saved_loc2 = self.emitter.emit_skip(1)
                self.emitter.emit_comment("if: jump to end belongs here")

                # Backpatch de saved_loc1 (salto a else)
                cur_loc = self.emitter.emit_skip(0)
                self.emitter.emit_backup(saved_loc1)
                self.emitter.emit_rm_abs("JEQ", TMEmitter.AC, cur_loc, "if: jmp to else")
                self.emitter.emit_restore()

                # Generar cuerpo Else
                self._cgen(p_else)

                # Backpatch de saved_loc2 (salto incondicional al final)
                cur_loc2 = self.emitter.emit_skip(0)
                self.emitter.emit_backup(saved_loc2)
                self.emitter.emit_rm_abs("LDA", TMEmitter.PC, cur_loc2, "jmp to end")
                self.emitter.emit_restore()
            else:
                # No hay else: saltar directo al final
                cur_loc = self.emitter.emit_skip(0)
                self.emitter.emit_backup(saved_loc1)
                self.emitter.emit_rm_abs("JEQ", TMEmitter.AC, cur_loc, "if: jmp to end")
                self.emitter.emit_restore()

            self.emitter.emit_comment("<- if")

        elif node.kind == "WhileK":
            self.emitter.emit_comment("-> while")
            p_cond = node.child[0] if len(node.child) > 0 else None
            p_body = node.child[1] if len(node.child) > 1 else None

            start_loc = self.emitter.emit_skip(0)
            self.emitter.emit_comment("while: test starts here")

            # Evaluar condición
            self._cgen(p_cond)

            # Salto al fin si es falso
            jump_exit_loc = self.emitter.emit_skip(1)
            self.emitter.emit_comment("while: jmp to end if false")

            # Cuerpo
            if p_body:
                self._cgen(p_body)

            # Salto incondicional al inicio
            self.emitter.emit_rm_abs("LDA", TMEmitter.PC, start_loc, "while: jmp back to test")

            # Backpatch del salto de salida
            end_loc = self.emitter.emit_skip(0)
            self.emitter.emit_backup(jump_exit_loc)
            self.emitter.emit_rm_abs("JEQ", TMEmitter.AC, end_loc, "while: exit loop")
            self.emitter.emit_restore()

            self.emitter.emit_comment("<- while")

        elif node.kind in ("DoWhileK", "RepeatK"):
            self.emitter.emit_comment("-> do-until / repeat")
            # En DoWhileK / do-until de Skuld: child[0] = cuerpo, child[1] = condición
            p_body = node.child[0] if len(node.child) > 0 else None
            p_cond = node.child[1] if len(node.child) > 1 else None

            start_loc = self.emitter.emit_skip(0)
            self.emitter.emit_comment("repeat/do: body starts here")

            if p_body:
                self._cgen(p_body)

            if p_cond:
                self._cgen(p_cond)

            # Si es until (repetir hasta que sea verdadero => repetir MIENTRAS sea falso):
            # Salta al inicio si AC == 0 (condición falsa)
            self.emitter.emit_rm_abs("JEQ", TMEmitter.AC, start_loc, "do-until: jmp back if false")
            self.emitter.emit_comment("<- do-until")

        elif node.kind == "ReturnK":
            if node.child:
                self._cgen(node.child[0])

    def _gen_exp(self, node: TreeNode) -> None:
        """Generación de expresiones."""
        scope = getattr(node, "attr_scope", "global")

        if node.kind == "ConstK":
            # Cargar constante en AC
            val = node.val
            if isinstance(val, bool):
                int_val = 1 if val else 0
            elif isinstance(val, (int, float)):
                int_val = int(val)
            else:
                int_val = 0
            self.emitter.emit_rm("LDC", TMEmitter.AC, int_val, 0, f"load const {int_val}")

        elif node.kind == "IdK":
            loc = self._get_var_loc(node.name, scope)
            self.emitter.emit_rm("LD", TMEmitter.AC, loc, TMEmitter.GP, f"load id {node.name}")

        elif node.kind == "StringK":
            # Cadenas en TM: TM no soporta strings; cargamos 0 en AC
            self.emitter.emit_comment(f"string literal: {node.val}")
            self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "string (ignored in TM)")

        elif node.kind == "OpK":
            self.emitter.emit_comment(f"-> Op {node.op}")
            p1 = node.child[0] if len(node.child) > 0 else None
            p2 = node.child[1] if len(node.child) > 1 else None

            # Si un operando es StringK y el operador es '+', solo evaluamos el otro operando
            if p1 and p1.kind == "StringK":
                self._cgen(p2)
                return
            if p2 and p2.kind == "StringK":
                self._cgen(p1)
                return

            # 1. Evaluar hijo izquierdo -> resultado en AC
            self._cgen(p1)
            # 2. Push hijo izquierdo a memoria temporal (mp)
            self.emitter.emit_rm("ST", TMEmitter.AC, self.tmp_offset, TMEmitter.MP, "op: push left")
            self.tmp_offset -= 1

            # 3. Evaluar hijo derecho -> resultado en AC
            self._cgen(p2)

            # 4. Pop hijo izquierdo a AC1
            self.tmp_offset += 1
            self.emitter.emit_rm("LD", TMEmitter.AC1, self.tmp_offset, TMEmitter.MP, "op: load left")

            # 5. Ejecutar la operación (AC1 op AC) -> resultado en AC
            op = node.op
            if op == "+":
                self.emitter.emit_ro("ADD", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op +")
            elif op == "-":
                self.emitter.emit_ro("SUB", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op -")
            elif op == "*":
                self.emitter.emit_ro("MUL", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op *")
            elif op == "/":
                self.emitter.emit_ro("DIV", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op /")
            elif op == "<":
                # AC1 < AC  =>  AC1 - AC < 0
                self.emitter.emit_ro("SUB", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op <")
                self.emitter.emit_rm("JLT", TMEmitter.AC, 2, TMEmitter.PC, "br if true")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "false case")
                self.emitter.emit_rm("LDA", TMEmitter.PC, 1, TMEmitter.PC, "unconditional jmp")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 1, 0, "true case")
            elif op == "<=":
                # AC1 <= AC => AC1 - AC <= 0
                self.emitter.emit_ro("SUB", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op <=")
                self.emitter.emit_rm("JLE", TMEmitter.AC, 2, TMEmitter.PC, "br if true")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "false case")
                self.emitter.emit_rm("LDA", TMEmitter.PC, 1, TMEmitter.PC, "unconditional jmp")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 1, 0, "true case")
            elif op == ">":
                # AC1 > AC => AC1 - AC > 0
                self.emitter.emit_ro("SUB", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op >")
                self.emitter.emit_rm("JGT", TMEmitter.AC, 2, TMEmitter.PC, "br if true")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "false case")
                self.emitter.emit_rm("LDA", TMEmitter.PC, 1, TMEmitter.PC, "unconditional jmp")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 1, 0, "true case")
            elif op == ">=":
                # AC1 >= AC => AC1 - AC >= 0
                self.emitter.emit_ro("SUB", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op >=")
                self.emitter.emit_rm("JGE", TMEmitter.AC, 2, TMEmitter.PC, "br if true")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "false case")
                self.emitter.emit_rm("LDA", TMEmitter.PC, 1, TMEmitter.PC, "unconditional jmp")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 1, 0, "true case")
            elif op == "==":
                self.emitter.emit_ro("SUB", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op ==")
                self.emitter.emit_rm("JEQ", TMEmitter.AC, 2, TMEmitter.PC, "br if true")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "false case")
                self.emitter.emit_rm("LDA", TMEmitter.PC, 1, TMEmitter.PC, "unconditional jmp")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 1, 0, "true case")
            elif op == "!=":
                self.emitter.emit_ro("SUB", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op !=")
                self.emitter.emit_rm("JNE", TMEmitter.AC, 2, TMEmitter.PC, "br if true")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "false case")
                self.emitter.emit_rm("LDA", TMEmitter.PC, 1, TMEmitter.PC, "unconditional jmp")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 1, 0, "true case")
            elif op in ("&&", "and"):
                self.emitter.emit_ro("MUL", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op and")
            elif op in ("||", "or"):
                self.emitter.emit_ro("ADD", TMEmitter.AC, TMEmitter.AC1, TMEmitter.AC, "op or")
                self.emitter.emit_rm("JGT", TMEmitter.AC, 2, TMEmitter.PC, "br if > 0")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 0, 0, "false case")
                self.emitter.emit_rm("LDA", TMEmitter.PC, 1, TMEmitter.PC, "unconditional jmp")
                self.emitter.emit_rm("LDC", TMEmitter.AC, 1, 0, "true case")

            self.emitter.emit_comment(f"<- Op {node.op}")

        elif node.kind == "CallK":
            # Manejo básico de llamadas
            for arg in node.child:
                self._cgen(arg)
