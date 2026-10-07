from __future__ import annotations

import copy
from typing import Any, List, Optional, Union
from analizadores.analisis_sintactico.skuld_parser import TreeNode
from .symbol_table import SymbolTable, Symbol


# =====================================================================
# CLASE DE ERROR SEMÁNTICO CON FORMATO UNIFICADO
# =====================================================================

class SemanticError(Exception):
    """
    Representa un error detectado durante el análisis semántico.
    Formato estandarizado para coincidir con las expectativas del IDE y CLI:
    ERROR_SEMANTICO(linea, columna): <descripción> -> '<lexema>'
    """
    def __init__(self, line: int, column: int, description: str, lexeme: str = ""):
        self.line = line
        self.column = column
        self.description = description
        self.lexeme = lexeme
        suffix = f" -> '{lexeme}'" if lexeme else ""
        super().__init__(f"ERROR_SEMANTICO({line}, {column}): {description}{suffix}")

    def __str__(self) -> str:
        suffix = f" -> '{self.lexeme}'" if self.lexeme else ""
        return f"ERROR_SEMANTICO({self.line}, {self.column}): {self.description}{suffix}"


# =====================================================================
# MAPEO Y NORMALIZACIÓN DE TIPOS DEL LENGUAJE
# =====================================================================

TYPE_NORMALIZATION = {
    # Tipos Skuld <-> Estándar
    "worldline": "worldline",
    "int": "worldline",
    "divergence": "divergence",
    "float": "divergence",
    "real": "divergence",
    "reading": "reading",
    "bool": "reading",
    "string": "string",
    "void": "void",
    "unknown": "unknown",
}


def normalize_type(t: Optional[str]) -> str:
    """Normaliza alias de tipos ('int' -> 'worldline', 'float' -> 'divergence', etc.)."""
    if not t:
        return "unknown"
    return TYPE_NORMALIZATION.get(t.lower(), t.lower())


DISPLAY_TYPES = {
    "worldline": "int",
    "divergence": "float",
    "reading": "bool",
}


def display_type(t: Optional[str]) -> str:
    """Convierte tipos internos a los nombres visibles del lenguaje."""
    normalized = normalize_type(t)
    return DISPLAY_TYPES.get(normalized, normalized)


# =====================================================================
# ANALIZADOR SEMÁNTICO Y RECORREDOR DEL AST
# =====================================================================

class SemanticAnalyzer:
    """
    Analizador Semántico de Skuld.
    Recorre el AST, gestiona la Tabla de Símbolos, asigna/propaga atributos
    (heredados y sintetizados), verifica compatibilidad de tipos y registra errores.
    """
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors: List[SemanticError] = []
        self.current_function_return_type: Optional[str] = None

    def analyze(self, ast: TreeNode) -> tuple[TreeNode, SymbolTable, List[SemanticError]]:
        """
        Punto de entrada principal.
        Crea una copia profunda del AST para generar el AST Anotado sin alterar el original.
        Retorna (annotated_ast, symbol_table, errors).
        """
        # Copia profunda para preservar el AST sintáctico original intacto
        annotated_ast = copy.deepcopy(ast)
        self.symbol_table = SymbolTable()
        self.errors = []
        self.current_function_return_type = None

        self._annotate_node(annotated_ast)
        return annotated_ast, self.symbol_table, self.errors

    def _report_error(self, line: int, column: int, description: str, lexeme: str = "") -> None:
        """Registra un error semántico garantizando no duplicar exactamente el mismo mensaje en la misma línea."""
        err = SemanticError(line, column, description, lexeme)
        for existing in self.errors:
            if existing.line == line and existing.description == description and existing.lexeme == lexeme:
                return
        self.errors.append(err)

    # -----------------------------------------------------------------
    # RECORRIDO Y ANOTACIÓN RECURSIVA
    # -----------------------------------------------------------------

    def _annotate_node(self, node: Optional[TreeNode]) -> None:
        if node is None:
            return

        # Inicializar atributos semánticos dinámicos en el nodo anotado si no existen
        if not hasattr(node, "attr_type"):
            node.attr_type = None
        if not hasattr(node, "attr_scope"):
            node.attr_scope = self.symbol_table.current_scope.name
        if not hasattr(node, "attr_val"):
            node.attr_val = None

        kind = node.kind
        nodekind = node.nodekind

        # 1. Declaraciones
        if nodekind == "DeclK":
            if kind == "DeclVarK":
                self._handle_decl_var(node)
                return
            elif kind == "FuncK":
                self._handle_func_decl(node)
                return

        # 2. Sentencias
        elif nodekind == "StmtK":
            if kind == "BlockK":
                self._handle_block(node)
                return
            elif kind == "AssignK":
                self._handle_assign(node)
                return
            elif kind == "IfK":
                self._handle_if(node)
                return
            elif kind == "WhileK":
                self._handle_while(node)
                return
            elif kind == "DoWhileK":
                self._handle_do_while(node)
                return
            elif kind == "ReadK":
                self._handle_read(node)
                return
            elif kind == "WriteK":
                self._handle_write(node)
                return
            elif kind == "ReturnK":
                self._handle_return(node)
                return
            elif kind == "CallStmtK":
                self._handle_call_stmt(node)
                return

        # 3. Expresiones
        elif nodekind == "ExpK":
            self._handle_expression(node)
            return

        # Recorrido general por defecto para nodos estructurales no capturados
        for child in node.child:
            self._annotate_node(child)

    # -----------------------------------------------------------------
    # MANEJO DE DECLARACIONES (ATRIBUTOS HEREDADOS)
    # -----------------------------------------------------------------

    def _handle_decl_var(self, node: TreeNode) -> None:
        """
        Procesa declaraciones de variables.
        Aplica el concepto de ATRIBUTO HEREDADO:
        El tipo base definido en DeclVarK (ej. 'worldline') se hereda hacia
        cada variable de su lista de hijos (VarK).
        """
        declared_type = normalize_type(node.type or node.name)
        node.attr_type = declared_type
        node.attr_scope = self.symbol_table.current_scope.name

        for var_node in node.child:
            if var_node is None or var_node.kind != "VarK":
                continue

            var_name = var_node.name or ""
            var_node.attr_scope = self.symbol_table.current_scope.name
            # Propagación heredada del tipo hacia la variable
            var_node.attr_type = declared_type

            # Verificar si tiene inicialización
            const_val = None
            if var_node.child:
                init_expr = var_node.child[0]
                self._annotate_node(init_expr)
                expr_type = normalize_type(getattr(init_expr, "attr_type", None))
                const_val = getattr(init_expr, "attr_val", None)

                # Verificación de compatibilidad en la inicialización
                if expr_type != "unknown":
                    if not self._is_assignment_compatible(declared_type, expr_type):
                        self._report_error(
                            var_node.lineno, 1,
                            f"Incompatibilidad de tipos en inicialización de '{var_name}': no se puede asignar '{display_type(expr_type)}' a '{display_type(declared_type)}'",
                            var_name
                        )

            # Intentar insertar en la tabla de símbolos del ámbito actual
            success, existing_sym = self.symbol_table.insert(
                name=var_name,
                data_type=declared_type,
                line=var_node.lineno,
                constant_val=const_val
            )

            if not success:
                # Error semántico: Duplicidad de identificador en el mismo ámbito
                self._report_error(
                    var_node.lineno, 1,
                    f"Duplicidad de declaraciones: la variable '{var_name}' ya fue declarada previamente en el ámbito '{self.symbol_table.current_scope.name}' (línea {existing_sym.declaration_line})",
                    var_name
                )

    def _handle_func_decl(self, node: TreeNode) -> None:
        """
        Procesa declaración de función (steiner).
        Crea un nuevo ámbito para los parámetros y cuerpo,
        e inserta la función en el ámbito global/contenedor.
        """
        func_name = node.name or ""
        ret_type = normalize_type(node.type)
        node.attr_type = ret_type
        node.attr_scope = self.symbol_table.current_scope.name

        param_types = [normalize_type(t) for t, _ in node.params]

        # Insertar función en el ámbito actual
        success, existing_sym = self.symbol_table.insert(
            name=func_name,
            data_type=ret_type,
            line=node.lineno,
            is_function=True,
            param_types=param_types
        )
        if not success:
            self._report_error(
                node.lineno, 1,
                f"Duplicidad de identificadores: la función '{func_name}' ya ha sido declarada previamente en este ámbito",
                func_name
            )

        # Entrar al nuevo ámbito de la función
        self.symbol_table.enter_scope(func_name)
        prev_func_ret = self.current_function_return_type
        self.current_function_return_type = ret_type

        # Registrar parámetros como variables del ámbito local de la función
        for p_type_str, p_name in node.params:
            p_norm_type = normalize_type(p_type_str)
            p_success, _ = self.symbol_table.insert(
                name=p_name,
                data_type=p_norm_type,
                line=node.lineno
            )
            if not p_success:
                self._report_error(
                    node.lineno, 1,
                    f"Duplicidad de parámetro: '{p_name}' ya está definido en la función '{func_name}'",
                    p_name
                )

        # Procesar los hijos (cuerpo de la función)
        for child in node.child:
            self._annotate_node(child)

        # Restaurar estado y salir del ámbito
        self.current_function_return_type = prev_func_ret
        self.symbol_table.exit_scope()

    # -----------------------------------------------------------------
    # MANEJO DE SENTENCIAS Y BLOQUES
    # -----------------------------------------------------------------

    def _handle_block(self, node: TreeNode) -> None:
        block_name = node.name or "block"
        is_named_scope = block_name in {"Programa", "gate", "main"} or block_name.startswith("Bloque")

        if is_named_scope and block_name != "Programa":
            self.symbol_table.enter_scope(block_name)

        node.attr_scope = self.symbol_table.current_scope.name
        for child in node.child:
            self._annotate_node(child)

        if is_named_scope and block_name != "Programa":
            self.symbol_table.exit_scope()

    def _handle_assign(self, node: TreeNode) -> None:
        var_name = node.name or ""
        node.attr_scope = self.symbol_table.current_scope.name

        # Buscar variable en la tabla de símbolos
        sym = self.symbol_table.lookup(var_name)
        if sym is None:
            self._report_error(
                node.lineno, 1,
                f"Uso de variable no declarada: '{var_name}' no ha sido declarada en ningún ámbito accesible",
                var_name
            )
            target_type = "unknown"
        else:
            sym.add_reference(node.lineno)
            target_type = sym.data_type

        node.attr_type = target_type

        # Evaluar la expresión asignada (hijo 0)
        if node.child:
            expr_node = node.child[0]
            self._annotate_node(expr_node)
            expr_type = normalize_type(getattr(expr_node, "attr_type", "unknown"))

            if target_type != "unknown" and expr_type != "unknown":
                if not self._is_assignment_compatible(target_type, expr_type):
                    self._report_error(
                        node.lineno, 1,
                        f"Incompatibilidad de tipos en asignación: no se puede asignar tipo '{display_type(expr_type)}' a variable '{var_name}' de tipo '{display_type(target_type)}'",
                        var_name
                    )

    def _handle_if(self, node: TreeNode) -> None:
        node.attr_scope = self.symbol_table.current_scope.name

        # En if, el hijo 0 es la condición (o bloque Condition)
        if len(node.child) > 0 and node.child[0] is not None:
            cond_node = node.child[0]
            self._annotate_node(cond_node)
            cond_type = normalize_type(getattr(cond_node, "attr_type", "unknown"))
            if cond_type != "unknown" and cond_type != "reading":
                self._report_error(
                    node.lineno, 1,
                    f"Tipo incorrecto en condición de 'if': se requiere una expresión booleana ('bool'), pero se obtuvo '{display_type(cond_type)}'",
                    "if"
                )

        # Procesar rama then (hijo 1) y else (hijo 2)
        if len(node.child) > 1 and node.child[1] is not None:
            self._annotate_node(node.child[1])
        if len(node.child) > 2 and node.child[2] is not None:
            self._annotate_node(node.child[2])

    def _handle_while(self, node: TreeNode) -> None:
        node.attr_scope = self.symbol_table.current_scope.name

        # Condición
        if len(node.child) > 0 and node.child[0] is not None:
            cond_node = node.child[0]
            self._annotate_node(cond_node)
            cond_type = normalize_type(getattr(cond_node, "attr_type", "unknown"))
            if cond_type != "unknown" and cond_type != "reading":
                self._report_error(
                    node.lineno, 1,
                    f"Tipo incorrecto en condición de 'while': se requiere una expresión booleana ('bool'), pero se obtuvo '{display_type(cond_type)}'",
                    "while"
                )

        # Cuerpo del bucle
        if len(node.child) > 1 and node.child[1] is not None:
            self._annotate_node(node.child[1])

    def _handle_do_while(self, node: TreeNode) -> None:
        node.attr_scope = self.symbol_table.current_scope.name

        # En do-while: hijo 0 es cuerpo, hijo 1 es condición
        if len(node.child) > 0 and node.child[0] is not None:
            self._annotate_node(node.child[0])

        if len(node.child) > 1 and node.child[1] is not None:
            cond_node = node.child[1]
            self._annotate_node(cond_node)
            cond_type = normalize_type(getattr(cond_node, "attr_type", "unknown"))
            if cond_type != "unknown" and cond_type != "reading":
                self._report_error(
                    node.lineno, 1,
                    f"Tipo incorrecto en condición de 'do-while': se requiere una expresión booleana ('bool'), pero se obtuvo '{display_type(cond_type)}'",
                    "do"
                )

    def _handle_read(self, node: TreeNode) -> None:
        var_name = node.name or ""
        node.attr_scope = self.symbol_table.current_scope.name

        sym = self.symbol_table.lookup(var_name)
        if sym is None:
            self._report_error(
                node.lineno, 1,
                f"Uso de variable no declarada en lectura: '{var_name}' no ha sido declarada",
                var_name
            )
            node.attr_type = "unknown"
        else:
            sym.add_reference(node.lineno)
            node.attr_type = sym.data_type

    def _handle_write(self, node: TreeNode) -> None:
        node.attr_scope = self.symbol_table.current_scope.name
        for child in node.child:
            self._annotate_node(child)

    def _handle_return(self, node: TreeNode) -> None:
        node.attr_scope = self.symbol_table.current_scope.name
        expr_type = "void"

        if node.child:
            expr_node = node.child[0]
            self._annotate_node(expr_node)
            expr_type = normalize_type(getattr(expr_node, "attr_type", "unknown"))

        node.attr_type = expr_type

        # Validar concordancia con el tipo de retorno de la función actual
        if self.current_function_return_type is not None:
            expected = self.current_function_return_type
            if expected != "unknown" and expr_type != "unknown":
                if not self._is_assignment_compatible(expected, expr_type):
                    self._report_error(
                        node.lineno, 1,
                        f"Incompatibilidad de tipo en sentencia 'return': se esperaba '{display_type(expected)}', pero se retornó '{display_type(expr_type)}'",
                        "return"
                    )

    def _handle_call_stmt(self, node: TreeNode) -> None:
        func_name = node.name or ""
        node.attr_scope = self.symbol_table.current_scope.name

        sym = self.symbol_table.lookup(func_name)
        if sym is None:
            self._report_error(
                node.lineno, 1,
                f"Llamada a función no declarada: '{func_name}' no ha sido declarada",
                func_name
            )
            node.attr_type = "unknown"
        else:
            sym.add_reference(node.lineno)
            node.attr_type = sym.data_type
            self._verify_call_arguments(node, sym)

    # -----------------------------------------------------------------
    # EVALUACIÓN DE EXPRESIONES (ATRIBUTOS SINTETIZADOS Y TIPADO)
    # -----------------------------------------------------------------

    def _handle_expression(self, node: TreeNode) -> None:
        """
        Calcula y sintetiza tipos y valores constantes en expresiones.
        Aplica el concepto de ATRIBUTO SINTETIZADO:
        El tipo de la expresión se obtiene a partir de los tipos de sus subárboles hijos.
        """
        node.attr_scope = self.symbol_table.current_scope.name
        kind = node.kind

        # 1. Constantes literales
        if kind == "ConstK":
            val = node.val
            if isinstance(val, bool):
                node.attr_type = "reading"
            elif isinstance(val, int):
                node.attr_type = "worldline"
            elif isinstance(val, float):
                node.attr_type = "divergence"
            else:
                node.attr_type = "worldline"
            node.attr_val = val
            return

        # 2. Cadenas literales
        elif kind == "StringK":
            node.attr_type = "string"
            node.attr_val = str(node.val)
            return

        # 3. Identificadores (uso de variables)
        elif kind == "IdK":
            var_name = node.name or ""
            if var_name == "<error>":
                node.attr_type = "unknown"
                return

            sym = self.symbol_table.lookup(var_name)
            if sym is None:
                self._report_error(
                    node.lineno, 1,
                    f"Uso de variable o identificador no declarado: '{var_name}'",
                    var_name
                )
                node.attr_type = "unknown"
            else:
                sym.add_reference(node.lineno)
                node.attr_type = sym.data_type
                node.attr_val = sym.constant_val
            return

        # 4. Llamada a función dentro de una expresión
        elif kind == "CallK":
            func_name = node.name or ""
            sym = self.symbol_table.lookup(func_name)
            if sym is None:
                self._report_error(
                    node.lineno, 1,
                    f"Llamada a función no declarada en expresión: '{func_name}'",
                    func_name
                )
                node.attr_type = "unknown"
            else:
                sym.add_reference(node.lineno)
                node.attr_type = sym.data_type
                self._verify_call_arguments(node, sym)
            return

        # 5. Operaciones (OpK)
        elif kind == "OpK":
            self._handle_op_node(node)
            return

    def _handle_op_node(self, node: TreeNode) -> None:
        """Determina el tipo y valor de un nodo operador aritmético, relacional o lógico."""
        op = node.op or ""

        # Procesar todos los operandos hijos primero
        for child in node.child:
            self._annotate_node(child)

        # Operación unaria: 1 solo hijo (!, -, +)
        if len(node.child) == 1:
            child = node.child[0]
            c_type = normalize_type(getattr(child, "attr_type", "unknown"))
            c_val = getattr(child, "attr_val", None)

            if op == "!":
                if c_type != "unknown" and c_type != "reading":
                    self._report_error(
                        node.lineno, 1,
                        f"Uso indebido de operador '!': el operando debe ser booleano ('bool'), se obtuvo '{display_type(c_type)}'",
                        op
                    )
                node.attr_type = "reading"
                if c_val is not None and isinstance(c_val, bool):
                    node.attr_val = not c_val
            elif op in {"-", "+"}:
                if c_type != "unknown" and c_type not in {"worldline", "divergence"}:
                    self._report_error(
                        node.lineno, 1,
                        f"Uso indebido de operador unario '{op}': el operando debe ser numérico, se obtuvo '{display_type(c_type)}'",
                        op
                    )
                node.attr_type = c_type
                if c_val is not None and isinstance(c_val, (int, float)):
                    node.attr_val = -c_val if op == "-" else +c_val
            else:
                node.attr_type = c_type
            return

        # Operación binaria: 2 operandos
        if len(node.child) >= 2:
            left = node.child[0]
            right = node.child[1]
            l_type = normalize_type(getattr(left, "attr_type", "unknown"))
            r_type = normalize_type(getattr(right, "attr_type", "unknown"))
            l_val = getattr(left, "attr_val", None)
            r_val = getattr(right, "attr_val", None)

            # Caso A: Operadores lógicos (&&, ||)
            if op in {"&&", "||", "and", "or"}:
                if l_type != "unknown" and l_type != "reading":
                    self._report_error(
                        node.lineno, 1,
                        f"Uso indebido de operador lógico '{op}': el operando izquierdo debe ser 'bool', pero es '{display_type(l_type)}'",
                        op
                    )
                if r_type != "unknown" and r_type != "reading":
                    self._report_error(
                        node.lineno, 1,
                        f"Uso indebido de operador lógico '{op}': el operando derecho debe ser 'bool', pero es '{display_type(r_type)}'",
                        op
                    )
                node.attr_type = "reading"
                if l_val is not None and r_val is not None and isinstance(l_val, bool) and isinstance(r_val, bool):
                    node.attr_val = (l_val and r_val) if op in {"&&", "and"} else (l_val or r_val)
                return

            # Caso B: Operadores relacionales (<, <=, >, >=, ==, !=)
            if op in {"<", "<=", ">", ">=", "==", "!="}:
                if l_type != "unknown" and r_type != "unknown":
                    if not self._are_comparable_types(l_type, r_type, op):
                        self._report_error(
                            node.lineno, 1,
                            f"Incompatibilidad de tipos en comparación '{op}': no se pueden comparar operandos de tipo '{display_type(l_type)}' y '{display_type(r_type)}'",
                            op
                        )
                node.attr_type = "reading"
                if l_val is not None and r_val is not None:
                    node.attr_val = self._eval_const_relop(op, l_val, r_val)
                return

            # Caso C: Operadores aritméticos (+, -, *, /, %, ^)
            if op in {"+", "-", "*", "/", "%", "^"}:
                # Soporte especial para concatenación de strings con '+'
                if op == "+" and (l_type == "string" or r_type == "string"):
                    node.attr_type = "string"
                    if l_val is not None and r_val is not None:
                        node.attr_val = f"{l_val}{r_val}"
                    return

                # Operación aritmética puramente numérica
                if l_type != "unknown" and l_type not in {"worldline", "divergence"}:
                    self._report_error(
                        node.lineno, 1,
                        f"Uso indebido de operador aritmético '{op}': el operando izquierdo no es numérico ('{display_type(l_type)}')",
                        op
                    )
                if r_type != "unknown" and r_type not in {"worldline", "divergence"}:
                    self._report_error(
                        node.lineno, 1,
                        f"Uso indebido de operador aritmético '{op}': el operando derecho no es numérico ('{display_type(r_type)}')",
                        op
                    )

                # Regla de promoción aritmética de Skuld:
                # worldline op divergence -> divergence
                # divergence op worldline -> divergence
                # divergence op divergence -> divergence
                # worldline op worldline -> worldline (o divergence si es división real '/')
                if l_type == "divergence" or r_type == "divergence":
                    res_type = "divergence"
                elif l_type == "worldline" and r_type == "worldline":
                    res_type = "worldline"
                else:
                    res_type = "unknown"

                node.attr_type = res_type

                # Constant folding (evaluación constante en tiempo de compilación si ambos valores son conocidos)
                if l_val is not None and r_val is not None and isinstance(l_val, (int, float)) and isinstance(r_val, (int, float)):
                    node.attr_val = self._eval_const_arith(op, l_val, r_val, res_type)
                return

        # Fallback para cualquier otro caso
        node.attr_type = "unknown"

    def _verify_call_arguments(self, node: TreeNode, sym: Symbol) -> None:
        """Verifica concordancia de cantidad y tipos de argumentos en llamadas a funciones."""
        args = [c for c in node.child if c is not None]
        for arg in args:
            self._annotate_node(arg)

        if len(args) != len(sym.param_types):
            self._report_error(
                node.lineno, 1,
                f"Número de argumentos incorrecto en llamada a '{sym.name}': se esperaban {len(sym.param_types)}, pero se recibieron {len(args)}",
                sym.name
            )
            return

        for i, (arg_node, expected_param_type) in enumerate(zip(args, sym.param_types)):
            arg_type = normalize_type(getattr(arg_node, "attr_type", "unknown"))
            expected_norm = normalize_type(expected_param_type)
            if arg_type != "unknown" and not self._is_assignment_compatible(expected_norm, arg_type):
                self._report_error(
                    node.lineno, 1,
                    f"Tipo de argumento incorrecto en parámetro #{i+1} de '{sym.name}': se esperaba '{display_type(expected_norm)}', pero se recibió '{display_type(arg_type)}'",
                    sym.name
                )

    # -----------------------------------------------------------------
    # COMPATIBILIDAD Y CONVERSIONES DE TIPOS
    # -----------------------------------------------------------------

    @staticmethod
    def _is_assignment_compatible(target: str, source: str) -> bool:
        """
        Reglas de compatibilidad para asignaciones e inicializaciones:
        - Tipos idénticos siempre son compatibles.
        - Conversión/promoción permitida: divergence (float) acepta worldline (int).
        - Conversión prohibida / Incompatibilidad: worldline NO acepta divergence (pérdida de precisión).
        - reading (bool) no acepta ni puede ser asignado a tipos numéricos.
        """
        target = normalize_type(target)
        source = normalize_type(source)

        if target == source:
            return True

        # Promoción implícita: float = int
        if target == "divergence" and source == "worldline":
            return True

        # Concatenación o conversión a string permitida en salidas/mensajes
        if target == "string":
            return True

        return False

    @staticmethod
    def _are_comparable_types(t1: str, t2: str, op: str) -> bool:
        """Comprueba si dos tipos pueden compararse con operadores relacionales."""
        t1 = normalize_type(t1)
        t2 = normalize_type(t2)

        if t1 == t2:
            return True

        # Tipos numéricos entre sí (worldline y divergence) son comparables
        if t1 in {"worldline", "divergence"} and t2 in {"worldline", "divergence"}:
            return True

        # Igualdad o desigualdad estricta
        if op in {"==", "!="}:
            return False

        return False

    @staticmethod
    def _eval_const_relop(op: str, l: Any, r: Any) -> Optional[bool]:
        """Evalúa una expresión relacional entre literales constantes."""
        try:
            if op == "<": return l < r
            if op == "<=": return l <= r
            if op == ">": return l > r
            if op == ">=": return l >= r
            if op == "==": return l == r
            if op == "!=": return l != r
        except Exception:
            return None
        return None

    @staticmethod
    def _eval_const_arith(op: str, l: Any, r: Any, res_type: str) -> Optional[Union[int, float]]:
        """Evalúa operaciones aritméticas constantes de forma segura evitando división por cero."""
        try:
            val = None
            if op == "+": val = l + r
            elif op == "-": val = l - r
            elif op == "*": val = l * r
            elif op == "/":
                if r == 0: return None
                val = l / r
            elif op == "%":
                if r == 0: return None
                val = l % r
            elif op == "^":
                val = l ** r

            if val is not None:
                return float(val) if res_type == "divergence" else int(val)
        except Exception:
            return None
        return None


# =====================================================================
# RENDERIZADO VISUAL DEL AST ANOTADO (CON TIPOS, ATRIBUTOS Y VALORES)
# =====================================================================

def print_annotated_tree(node: Optional[TreeNode], prefix: str = "", is_last: bool = True) -> str:
    """
    Función de renderizado gráfico de alta calidad para el AST Anotado.
    Muestra jerarquía de carpetas con anotaciones de tipo, ámbito y valor constante.
    """
    if node is None:
        return ""

    # Omitir nodo intermedio 'Secuencia de Sentencias'
    if node.nodekind == "StmtK" and node.kind == "BlockK" and (node.name == "Secuencia de Sentencias" or node.name == "Statement Sequence"):
        result = ""
        children = [c for c in node.child if c is not None]
        for i, child in enumerate(children):
            result += print_annotated_tree(child, prefix, is_last and (i == len(children) - 1))
        return result

    display_name = node.name or ""
    if display_name == "Condición": display_name = "Condition"
    elif display_name == "Rama Entonces": display_name = "Then"
    elif display_name == "Rama Sino": display_name = "Else "
    elif display_name == "Cuerpo del Bucle": display_name = "Loop"

    # Preparar sufijos de atributos semánticos
    attr_type = getattr(node, "attr_type", None)
    attr_val = getattr(node, "attr_val", None)
    attr_scope = getattr(node, "attr_scope", None)

    annotations = []
    if attr_type and attr_type != "unknown":
        annotations.append(f"tipo: {display_type(attr_type)}")
    if attr_val is not None:
        annotations.append(f"val: {attr_val}")
    if attr_scope and node.nodekind in {"DeclK", "StmtK"}:
        annotations.append(f"ámbito: {attr_scope}")

    annot_str = f" {{{', '.join(annotations)}}}" if annotations else ""

    # Generar descripción base según tipo de nodo
    desc = ""
    if node.nodekind == "DeclK":
        if node.kind == "DeclVarK":
            desc = f"[Declaración de Variable] Tipo: {display_type(node.type)}{annot_str}"
        elif node.kind == "VarK":
            init_suffix = " (Inicializada)" if node.child else ""
            desc = f"[Variable] ID: {display_name}{init_suffix}{annot_str}"
        elif node.kind == "FuncK":
            params_str = ", ".join(f"{display_type(t)} {n}" for t, n in node.params)
            desc = f"[Definición de Función] Tipo: {display_type(node.type)}, Nombre: {display_name}({params_str}){annot_str}"
    elif node.nodekind == "StmtK":
        if node.kind == "IfK":
            desc = f"[Condicional / if]{annot_str}"
        elif node.kind == "WhileK":
            desc = f"[Bucle / while]{annot_str}"
        elif node.kind == "DoWhileK":
            desc = f"[Bucle / do-{node.op or 'while'}]{annot_str}"
        elif node.kind == "AssignK":
            desc = f"[Asignación] ID: {display_name}{annot_str}"
        elif node.kind == "ReadK":
            desc = f"[Entrada / cin] ID: {display_name}{annot_str}"
        elif node.kind == "WriteK":
            desc = f"[Salida / cout]{annot_str}"
        elif node.kind == "ReturnK":
            desc = f"[Retorno / return]{annot_str}"
        elif node.kind == "BlockK":
            desc = f"[Bloque de Código / {display_name or '{...}'}]{annot_str}"
        elif node.kind == "CallStmtK":
            desc = f"[Llamada a Función] Nombre: {display_name}{annot_str}"
    elif node.nodekind == "ExpK":
        if node.kind == "OpK":
            desc = f"[Operador] '{node.op}'{annot_str}"
        elif node.kind == "ConstK":
            desc = f"[Constante] Valor: {node.val}{annot_str}"
        elif node.kind == "IdK":
            desc = f"[Variable / ID] Nombre: {display_name}{annot_str}"
        elif node.kind == "StringK":
            desc = f"[Cadena] \"{node.val}\"{annot_str}"
        elif node.kind == "CallK":
            desc = f"[Llamada a Función en Expresión] Nombre: {display_name}{annot_str}"

    marker = "└── " if is_last else "├── "
    result = f"{prefix}{marker}{desc} @ {node.lineno}\n"

    next_prefix = prefix + ("    " if is_last else "│   ")
    children = [c for c in node.child if c is not None]

    if node.kind == "IfK":
        labels = ["Condition", "Then", "Else"]
        labeled_children = []
        for idx, child in enumerate(children):
            if idx < len(labels):
                lbl_node = TreeNode("StmtK", "BlockK", lineno=node.lineno)
                lbl_node.name = labels[idx]
                lbl_node.child.append(child)
                labeled_children.append(lbl_node)
            else:
                labeled_children.append(child)
        children = labeled_children
    elif node.kind == "WhileK":
        labels = ["Condition", "Loop"]
        labeled_children = []
        for idx, child in enumerate(children):
            if idx < len(labels):
                lbl_node = TreeNode("StmtK", "BlockK", lineno=node.lineno)
                lbl_node.name = labels[idx]
                lbl_node.child.append(child)
                labeled_children.append(lbl_node)
            else:
                labeled_children.append(child)
        children = labeled_children
    elif node.kind == "DoWhileK":
        labels = ["Loop", "Condition"]
        labeled_children = []
        for idx, child in enumerate(children):
            if idx < len(labels):
                lbl_node = TreeNode("StmtK", "BlockK", lineno=node.lineno)
                lbl_node.name = labels[idx]
                lbl_node.child.append(child)
                labeled_children.append(lbl_node)
            else:
                labeled_children.append(child)
        children = labeled_children

    rendered_children = [c for c in children if not (c.nodekind == "ExpK" and c.name == "<error>")]
    for i, child in enumerate(rendered_children):
        result += print_annotated_tree(child, next_prefix, i == len(rendered_children) - 1)

    return result
