from __future__ import annotations

from typing import List, Optional, Set, Union
from analizadores.analisis_lexico.skuld_lexer import Token, SkuldLexer, LexicalError


# =====================================================================
# CLASES DE ERRORES Y ESTRUCTURAS DEL AST (Árbol Sintáctico Abstracto)
# =====================================================================

class SyntaxError(Exception):
    """
    Clase para representar un error sintáctico.
    Registra la línea, columna y lexema del token erróneo, formateándolo
    de acuerdo a las especificaciones del IDE para resaltar la falla en rojo.
    """
    def __init__(self, line: int, column: int, description: str, token_lexeme: str = ""):
        self.line = line
        self.column = column
        self.description = description
        self.lexeme = token_lexeme
        suffix = f" -> '{token_lexeme}'" if token_lexeme else ""
        super().__init__(f"ERROR_SINTACTICO({line}, {column}): {description}{suffix}")


class TreeNode:
    """
    Estructura de Nodo para el Árbol Sintáctico Abstracto (AST).
    Mapea fielmente los conceptos de la estructura 'TreeNode' en C 
    del compilador TINY de Kenneth Louden (GLOBALS.H).
    """
    def __init__(self, nodekind: str, kind: str, lineno: int = 0):
        self.nodekind = nodekind  # Tipo de nodo general: "StmtK" (Sentencia), "ExpK" (Expresión) o "DeclK" (Declaración)
        self.kind = kind          # Sub-tipo específico: "IfK", "WhileK", "AssignK", "OpK", "ConstK", "IdK", etc.
        self.lineno = lineno      # Línea del código fuente donde se ubica el nodo para reportar fallos
        self.child: List[Optional[TreeNode]] = []  # Lista de nodos hijos (en TINY se usaba un arreglo de tamaño estático)
        self.sibling: Optional[TreeNode] = None   # Enlace a la sentencia hermana en la lista (flujo de ejecución lineal)

        # Atributos específicos de la unión en C de Louden
        self.op: Optional[str] = None          # Para OpK: guarda el operador como cadena (ej. "+", "<=", "&&")
        self.val: Optional[Union[int, float, bool, str]] = None  # Para ConstK y StringK: valor constante almacenado
        self.name: Optional[str] = None        # Para IdK, AssignK y FuncK: nombre de variable, función o bloque
        self.type: Optional[str] = None        # Para DeclVarK: tipo de dato declarado ('worldline', 'divergence', 'reading')
        self.params: List[tuple[str, str]] = []  # Para FuncK: lista de parámetros definidos como (tipo, nombre)

    def __repr__(self) -> str:
        return f"TreeNode({self.nodekind}, {self.kind}, name={self.name}, op={self.op}, val={self.val})"


# =====================================================================
# DICCIONARIO DE TRADUCCIÓN DE TOKENS PARA REPORTES AMIGABLES
# =====================================================================

TOKEN_TRANSLATIONS = {
    # Palabras clave
    "KW_STEINER": "'steiner'",
    "KW_LABMEM": "'labmem'",
    "KW_WORLDLINE": "'worldline'",
    "KW_DIVERGENCE": "'divergence'",
    "KW_READING": "'reading'",
    "KW_INT": "'int'",
    "KW_FLOAT": "'float'",
    "KW_BOOL": "'bool'",
    "KW_STRING": "'string'",
    "KW_VOID": "'void'",
    "KW_GATE": "'gate'",
    "KW_MAIN": "'main'",
    "KW_CHOICE": "'choice'",
    "KW_IF": "'if'",
    "KW_LOOP": "'loop'",
    "KW_WHILE": "'while'",
    "KW_PULSE": "'pulse'",
    "KW_DO": "'do'",
    "KW_SPHONE": "'sphone'",
    "KW_CIN": "'cin'",
    "KW_DMAIL": "'dmail'",
    "KW_COUT": "'cout'",
    "KW_RETURN": "'return'",
    "KW_TRUE": "'true'",
    "KW_FALSE": "'false'",
    "KW_THEN": "'then'",
    "KW_ELSE": "'else'",
    "KW_END": "'end'",
    "KW_SEAL": "'seal'",
    "KW_UNTIL": "'until'",
    
    # Símbolos y Operadores
    "SEMICOLON": "';'",
    "COMMA": "','",
    "LPAREN": "'('",
    "RPAREN": "')'",
    "LBRACE": "'{'",
    "RBRACE": "'}'",
    "ASSIGN": "'='",
    "PLUS_ASSIGN": "'+='",
    "MINUS_ASSIGN": "'-='",
    "TIMES_ASSIGN": "'*='",
    "DIV_ASSIGN": "'/='",
    "MOD_ASSIGN": "'%='",
    "INC": "'++'",
    "DEC": "'--'",
    "LT": "'<'",
    "GT": "'>'",
    "LTE": "'<='",
    "GTE": "'>='",
    "EQ": "'=='",
    "NEQ": "'!='",
    "PLUS": "'+'",
    "MINUS": "'-'",
    "TIMES": "'*'",
    "DIV": "'/'",
    "MOD": "'%'",
    "AND_OP": "'&&'",
    "OR_OP": "'||'",
    "NOT_OP": "'!'",
    "DOT": "'.'",
    
    # Identificadores y Literales
    "IDENTIFIER": "un identificador (nombre de variable o función)",
    "INTEGER_LITERAL": "un número entero",
    "FLOAT_LITERAL": "un número real",
    "STRING_LITERAL": "una cadena de texto",
    "ENDFILE": "el fin del archivo"
}


# =====================================================================
# ANALIZADOR SINTÁCTICO (PARSER) DESCENDENTE RECURSIVO
# =====================================================================

class SkuldParser:
    """
    Clase Parser encargada de validar la gramática de Skuld y C/TINY.
    Mapea de forma procedimental recursiva los métodos de PARSE.C de Louden.
    """
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens  # Lista completa de tokens generados por el analizador léxico
        self.index = 0        # Índice de lectura actual en la lista de tokens
        self.errors: List[SyntaxError] = []  # Registro de todos los errores sintácticos detectados

    def parse(self) -> TreeNode:
        """
        Punto de entrada principal para realizar el análisis sintáctico.
        Mapea el método parse() de Louden. Retorna la raíz del AST.
        """
        # Nodo raíz que encapsula todo el programa
        root = TreeNode("StmtK", "BlockK", lineno=1)
        root.name = "Programa"

        last_child = None
        # Recorrer todos los tokens hasta llegar al fin de archivo (ENDFILE)
        while not self._check("ENDFILE"):
            try:
                node = None
                # 1. Definición de función con la palabra reservada 'steiner'
                if self._check("KW_STEINER"):
                    node = self._parse_function_decl()
                # 2. Declaración de variables globales ('labmem' o tipos directos)
                elif self._check({"KW_LABMEM", "KW_WORLDLINE", "KW_DIVERGENCE", "KW_READING", "KW_INT", "KW_FLOAT", "KW_BOOL"}):
                    node = self._parse_variable_decl()
                # 3. Bloque principal del programa ('gate' de Skuld o 'main' de C)
                elif self._check({"KW_GATE", "KW_MAIN"}):
                    node = self._parse_main_block()
                # 4. Cualquier otra sentencia o expresión global suelta
                else:
                    node = self._parse_statement()

                # Si logramos analizar un nodo sintáctico válido, lo agregamos a los hijos de la raíz
                if node:
                    curr = node
                    while curr is not None:
                        nxt_sibling = curr.sibling
                        curr.sibling = None  # Desacoplar para representarlo de forma limpia en listas
                        
                        if not root.child:
                            root.child.append(curr)
                        else:
                            last_child.sibling = curr  # Mantener enlace de hermanos de forma interna
                            root.child.append(curr)
                        last_child = curr
                        curr = nxt_sibling
            except SyntaxError as e:
                # Si hay un error, lo registramos y nos sincronizamos para no congelar la compilación
                self.errors.append(e)
                self._synchronize()

        return root

    # -----------------------------------------------------------------
    # MÉTODOS DE UTILIDAD Y COMPROBACIÓN DE TOKENS
    # -----------------------------------------------------------------

    def _current_token(self) -> Token:
        """Retorna el token actual que se está analizando."""
        if self.index >= len(self.tokens):
            if self.tokens:
                last = self.tokens[-1]
                return Token("ENDFILE", "", last.line, last.column_end, last.column_end)
            return Token("ENDFILE", "", 1, 1, 1)
        return self.tokens[self.index]

    def _match(self, expected_types: Union[str, Set[str], List[str]]) -> Token:
        """
        Compara el token actual con los tipos esperados.
        Si coincide, avanza la lectura; si no, lanza un SyntaxError.
        Mapea el método match() de Louden.
        """
        if isinstance(expected_types, str):
            expected_set = {expected_types}
        else:
            expected_set = set(expected_types)

        tok = self._current_token()
        if tok.token_type in expected_set:
            self.index += 1  # Consumir el token y avanzar
            return tok
        else:
            # Traducir los tipos esperados para que sean más legibles en español
            translated_expected = [TOKEN_TRANSLATIONS.get(t_type, f"'{t_type}'") for t_type in expected_set]
            expected_str = " o ".join(translated_expected)
            
            # Traducir el tipo de token encontrado
            found_desc = TOKEN_TRANSLATIONS.get(tok.token_type, f"'{tok.token_type}'")
            
            # Evitar redundancia si la descripción traducida es exactamente igual al lexema (ej. ';' -> ';')
            lexeme_suffix = tok.lexeme
            if found_desc == f"'{tok.lexeme}'":
                lexeme_suffix = ""
            
            raise SyntaxError(
                tok.line,
                tok.column_start,
                f"Se esperaba {expected_str}, pero se encontró {found_desc}",
                lexeme_suffix
            )

    def _check(self, expected_types: Union[str, Set[str], List[str]]) -> bool:
        """Comprueba si el token actual coincide con alguno de los tipos sin consumirlo (Lookahead)."""
        if isinstance(expected_types, str):
            expected_set = {expected_types}
        else:
            expected_set = set(expected_types)
        return self._current_token().token_type in expected_set

    def _synchronize(self):
        """
        Rutina de Sincronización contra Errores de Sintaxis.
        Asegura que el parser avance y no entre en bucles infinitos en caso de fallos.
        """
        # Avanzar obligatoriamente al menos un token para garantizar progreso continuo
        self.index += 1

        sync_tokens = {
            "SEMICOLON", "RBRACE", "KW_SEAL", "KW_END", 
            "KW_LABMEM", "KW_WORLDLINE", "KW_DIVERGENCE", "KW_READING", "KW_VOID",
            "KW_INT", "KW_FLOAT", "KW_BOOL",
            "KW_CHOICE", "KW_IF", "KW_LOOP", "KW_WHILE", "KW_PULSE", "KW_DO",
            "KW_SPHONE", "KW_CIN", "KW_DMAIL", "KW_COUT", "KW_RETURN", "KW_STEINER"
        }
        while self.index < len(self.tokens):
            tok = self._current_token()
            if tok.token_type == "ENDFILE":
                break
            if tok.token_type in sync_tokens:
                # Si encontramos un punto y coma, lo consumimos para limpiar la sentencia rota
                if tok.token_type == "SEMICOLON":
                    self.index += 1
                break
            self.index += 1

    # -----------------------------------------------------------------
    # MÉTODOS DE ANÁLISIS DE DECLARACIONES
    # -----------------------------------------------------------------

    def _parse_variable_decl(self) -> TreeNode:
        """
        Analiza declaraciones de variables como:
        labmem worldline x = 5, y = 15;
        Mapea 'declaracion_variable' y soporta inicialización y comas.
        """
        first_tok = self._current_token()
        
        # Consumir la palabra clave opcional 'labmem' (de Skuld)
        has_labmem = False
        if self._check("KW_LABMEM"):
            self._match("KW_LABMEM")
            has_labmem = True

        # Consumir el tipo de dato (tanto Skuld como estándar C)
        type_tok = self._match({
            "KW_WORLDLINE", "KW_DIVERGENCE", "KW_READING", 
            "KW_INT", "KW_FLOAT", "KW_BOOL"
        })
        var_type = type_tok.lexeme

        # Crear el nodo padre para la declaración del tipo
        decl_node = TreeNode("DeclK", "DeclVarK", lineno=type_tok.line)
        decl_node.name = var_type
        decl_node.type = var_type

        # Bucle para procesar variables declaradas separadas por comas (ej. x, y, z)
        while True:
            id_tok = self._match("IDENTIFIER")
            var_name = id_tok.lexeme

            # Crear un nodo para cada variable declarada
            var_node = TreeNode("DeclK", "VarK", lineno=id_tok.line)
            var_node.name = var_name

            # Inicialización opcional: '= expresión'
            if self._check("ASSIGN"):
                self._match("ASSIGN")
                var_node.child.append(self._parse_expr())

            # Agregar var_node como hijo del nodo declaración de tipo
            decl_node.child.append(var_node)

            # Si hay una coma, continuamos declarando en el mismo bloque
            if self._check("COMMA"):
                self._match("COMMA")
            else:
                break

        # Cada línea de declaración finaliza obligatoriamente con punto y coma ';'
        self._match("SEMICOLON")
        return decl_node

    def _parse_function_decl(self) -> TreeNode:
        """
        Analiza definiciones de funciones de usuario:
        steiner worldline duplicar(worldline a) { ... }
        """
        steiner_tok = self._match("KW_STEINER")

        # Tipo de retorno de la función
        type_tok = self._match({
            "KW_WORLDLINE", "KW_DIVERGENCE", "KW_READING", "KW_VOID",
            "KW_INT", "KW_FLOAT", "KW_BOOL", "KW_STRING"
        })
        ret_type = type_tok.lexeme

        # Nombre de la función
        name_tok = self._match("IDENTIFIER")
        func_name = name_tok.lexeme

        func_node = TreeNode("DeclK", "FuncK", lineno=steiner_tok.line)
        func_node.name = func_name
        func_node.type = ret_type

        # Parámetros entre paréntesis
        self._match("LPAREN")
        params = []
        if not self._check("RPAREN"):
            while True:
                p_type_tok = self._match({
                    "KW_WORLDLINE", "KW_DIVERGENCE", "KW_READING", 
                    "KW_INT", "KW_FLOAT", "KW_BOOL", "KW_STRING", "KW_DMAIL"
                })
                p_id_tok = self._match("IDENTIFIER")
                params.append((p_type_tok.lexeme, p_id_tok.lexeme))
                if self._check("COMMA"):
                    self._match("COMMA")
                else:
                    break
        self._match("RPAREN")
        func_node.params = params

        # Cuerpo encerrado entre llaves '{'
        self._match("LBRACE")
        body = self._parse_stmt_sequence("RBRACE")
        self._match("RBRACE")
        func_node.child.append(body)

        return func_node

    def _parse_main_block(self) -> TreeNode:
        """
        Analiza el bloque principal del programa:
        gate { ... } o main() { ... }
        """
        main_tok = self._match({"KW_GATE", "KW_MAIN"})

        # Paréntesis opcionales: main()
        if self._check("LPAREN"):
            self._match("LPAREN")
            self._match("RPAREN")

        self._match("LBRACE")
        body = self._parse_stmt_sequence("RBRACE")
        self._match("RBRACE")

        main_node = TreeNode("StmtK", "BlockK", lineno=main_tok.line)
        main_node.name = main_tok.lexeme
        main_node.child.append(body)
        return main_node

    # -----------------------------------------------------------------
    # MÉTODOS DE ANÁLISIS DE SENTENCIAS (STATEMENTS)
    # -----------------------------------------------------------------

    def _parse_stmt_sequence(self, end_tokens: Union[str, Set[str]]) -> TreeNode:
        """
        Analiza y encapsula una secuencia de sentencias o declaraciones
        como un único nodo plano BlockK ('Secuencia de Sentencias').
        Mapea el método 'stmt_sequence' de Louden de forma extremadamente limpia.
        """
        if isinstance(end_tokens, str):
            end_set = {end_tokens}
        else:
            end_set = end_tokens

        block_node = TreeNode("StmtK", "BlockK", lineno=self._current_token().line)
        block_node.name = "Secuencia de Sentencias"

        # Leer sentencias de forma sucesiva hasta el fin de archivo o topar con un token de cierre
        while self.index < len(self.tokens) and not self._check("ENDFILE") and not self._check(end_set):
            try:
                # Permitir declarar variables en cualquier parte de la secuencia
                if self._check({"KW_LABMEM", "KW_WORLDLINE", "KW_DIVERGENCE", "KW_READING", "KW_INT", "KW_FLOAT", "KW_BOOL"}):
                    node = self._parse_variable_decl()
                else:
                    node = self._parse_statement()

                if node:
                    # Si el análisis retorna una lista de declaraciones (por comas), las aplanamos en los hijos del bloque
                    curr = node
                    while curr is not None:
                        nxt = curr.sibling
                        curr.sibling = None
                        block_node.child.append(curr)
                        curr = nxt
            except SyntaxError as e:
                self.errors.append(e)
                self._synchronize()

        return block_node

    def _parse_statement(self) -> Optional[TreeNode]:
        """
        Mapea y delega el análisis sintáctico al método de sentencia respectivo.
        Mapea el método 'statement' de Louden.
        """
        tok = self._current_token()

        if tok.token_type in {"KW_CHOICE", "KW_IF"}:
            return self._parse_if_stmt()
        elif tok.token_type in {"KW_LOOP", "KW_WHILE"}:
            return self._parse_while_stmt()
        elif tok.token_type in {"KW_PULSE", "KW_DO"}:
            return self._parse_do_while_stmt()
        elif tok.token_type in {"KW_SPHONE", "KW_CIN"}:
            return self._parse_read_stmt()
        elif tok.token_type in {"KW_DMAIL", "KW_COUT"}:
            return self._parse_write_stmt()
        elif tok.token_type == "KW_RETURN":
            self._match("KW_RETURN")
            node = TreeNode("StmtK", "ReturnK", lineno=tok.line)
            if not self._check("SEMICOLON"):
                node.child.append(self._parse_expr())
            self._match("SEMICOLON")
            return node
        elif tok.token_type == "SEMICOLON":
            self._match("SEMICOLON")
            return None
        elif tok.token_type == "LBRACE":
            # Soporta bloques anidados o crudos en llaves {...} como sentencias válidas
            self._match("LBRACE")
            node = self._parse_stmt_sequence("RBRACE")
            self._match("RBRACE")
            return node
        elif tok.token_type == "IDENTIFIER":
            return self._parse_id_stmt()
        else:
            raise SyntaxError(
                tok.line,
                tok.column_start,
                "Se esperaba el inicio de una sentencia (como 'if', 'choice', 'while', 'loop', 'do', 'pulse', 'cin', 'cout', 'return', '{' o un identificador de variable/función)",
                tok.lexeme
            )

    def _parse_id_stmt(self) -> TreeNode:
        """
        Analiza sentencias que inician con un identificador.
        Soporta: asignaciones directas (=), complejas (+=, -=),
        llamadas a función (duplicar(x);) y operadores incremento/decremento (x++;).
        """
        id_tok = self._match("IDENTIFIER")

        # Caso 1: Llamada a función como sentencia independiente (ej. mostrar_mensaje(x);)
        if self._check("LPAREN"):
            self._match("LPAREN")
            stmt_node = TreeNode("StmtK", "CallStmtK", lineno=id_tok.line)
            stmt_node.name = id_tok.lexeme
            if not self._check("RPAREN"):
                while True:
                    stmt_node.child.append(self._parse_expr())
                    if self._check("COMMA"):
                        self._match("COMMA")
                    else:
                        break
            self._match("RPAREN")
            self._match("SEMICOLON")
            return stmt_node

        # Caso 2: Post-incremento o decremento (ej. x++ o x--)
        elif self._check({"INC", "DEC"}):
            op_tok = self._match({"INC", "DEC"})
            self._match("SEMICOLON")

            id_node = TreeNode("ExpK", "IdK", lineno=id_tok.line)
            id_node.name = id_tok.lexeme

            stmt_node = TreeNode("StmtK", "AssignK", lineno=id_tok.line)
            stmt_node.name = id_tok.lexeme

            # Traducir x++ sintácticamente a: x = x + 1
            op_node = TreeNode("ExpK", "OpK", lineno=id_tok.line)
            op_node.op = "+" if op_tok.token_type == "INC" else "-"
            op_node.child.append(id_node)

            const_node = TreeNode("ExpK", "ConstK", lineno=id_tok.line)
            const_node.val = 1
            op_node.child.append(const_node)

            stmt_node.child.append(op_node)
            return stmt_node

        # Caso 3: Asignaciones estándar (=) o compuestas (+=, -=, *=, /=, %=)
        else:
            assign_ops = {"ASSIGN", "PLUS_ASSIGN", "MINUS_ASSIGN", "TIMES_ASSIGN", "DIV_ASSIGN", "MOD_ASSIGN"}
            op_tok = self._match(assign_ops)

            stmt_node = TreeNode("StmtK", "AssignK", lineno=id_tok.line)
            stmt_node.name = id_tok.lexeme

            expr = self._parse_expr()
            self._match("SEMICOLON")

            # Si es asignación simple (=) enlazamos la expresión directa
            if op_tok.token_type == "ASSIGN":
                stmt_node.child.append(expr)
            # Si es compuesta (ej. x += y) lo traducimos a: x = x + y
            else:
                op_map = {
                    "PLUS_ASSIGN": "+",
                    "MINUS_ASSIGN": "-",
                    "TIMES_ASSIGN": "*",
                    "DIV_ASSIGN": "/",
                    "MOD_ASSIGN": "%"
                }
                id_node = TreeNode("ExpK", "IdK", lineno=id_tok.line)
                id_node.name = id_tok.lexeme

                op_node = TreeNode("ExpK", "OpK", lineno=id_tok.line)
                op_node.op = op_map[op_tok.token_type]
                op_node.child.append(id_node)
                op_node.child.append(expr)

                stmt_node.child.append(op_node)

            return stmt_node

    def _parse_if_stmt(self) -> TreeNode:
        """
        Analiza sentencias condicionales de selección:
        Soporta 'choice (cond) { ... } else { ... }' y 'if cond then ... else ... end'
        """
        if_tok = self._match({"KW_CHOICE", "KW_IF"})

        # Paréntesis opcionales alrededor de la condición
        has_paren = False
        if self._check("LPAREN"):
            self._match("LPAREN")
            has_paren = True

        cond = self._parse_expr()

        if has_paren:
            self._match("RPAREN")

        t = TreeNode("StmtK", "IfK", lineno=if_tok.line)
        t.child.append(cond)

        # Evaluar delimitador de inicio: '{' o 'then'
        has_braces = False
        if self._check("LBRACE"):
            self._match("LBRACE")
            has_braces = True
        elif self._check("KW_THEN"):
            self._match("KW_THEN")
        else:
            self._match({"LBRACE", "KW_THEN"})

        if has_braces:
            then_branch = self._parse_stmt_sequence("RBRACE")
            self._match("RBRACE")
        else:
            then_branch = self._parse_stmt_sequence({"KW_ELSE", "KW_END", "KW_SEAL"})

        t.child.append(then_branch)

        # Rama alternativa opcional 'else'
        if self._check("KW_ELSE"):
            self._match("KW_ELSE")
            if has_braces:
                self._match("LBRACE")
                else_branch = self._parse_stmt_sequence("RBRACE")
                self._match("RBRACE")
            else:
                else_branch = self._parse_stmt_sequence({"KW_END", "KW_SEAL"})
            t.child.append(else_branch)
        else:
            t.child.append(None)

        # Si no se usaron llaves, esperar palabra clave explícita de cierre 'end' o 'seal'
        if not has_braces:
            self._match({"KW_END", "KW_SEAL"})

        return t

    def _parse_while_stmt(self) -> TreeNode:
        """
        Analiza sentencias iterativas:
        Soporta 'loop (cond) { ... }' y 'while cond do ... end'
        """
        while_tok = self._match({"KW_LOOP", "KW_WHILE"})

        has_paren = False
        if self._check("LPAREN"):
            self._match("LPAREN")
            has_paren = True

        cond = self._parse_expr()

        if has_paren:
            self._match("RPAREN")

        t = TreeNode("StmtK", "WhileK", lineno=while_tok.line)
        t.child.append(cond)

        has_braces = False
        if self._check("LBRACE"):
            self._match("LBRACE")
            has_braces = True
        elif self._check("KW_DO"):
            self._match("KW_DO")
        else:
            self._match({"LBRACE", "KW_DO"})

        if has_braces:
            body = self._parse_stmt_sequence("RBRACE")
            self._match("RBRACE")
        else:
            body = self._parse_stmt_sequence({"KW_END", "KW_SEAL"})
            self._match({"KW_END", "KW_SEAL"})

        t.child.append(body)
        return t

    def _parse_do_while_stmt(self) -> TreeNode:
        """
        Analiza sentencias do-while/do-until:
        Soporta 'pulse { ... } while (cond);' y 'do ... until cond;'
        """
        do_tok = self._match({"KW_PULSE", "KW_DO"})

        has_braces = False
        if self._check("LBRACE"):
            self._match("LBRACE")
            has_braces = True

        if has_braces:
            body = self._parse_stmt_sequence("RBRACE")
            self._match("RBRACE")
        else:
            body = self._parse_stmt_sequence({"KW_WHILE", "KW_UNTIL"})

        # Admite tanto bucle por continuidad (while) como por término (until)
        cond_tok = self._match({"KW_WHILE", "KW_UNTIL"})

        has_paren = False
        if self._check("LPAREN"):
            self._match("LPAREN")
            has_paren = True

        cond = self._parse_expr()

        if has_paren:
            self._match("RPAREN")

        if self._check("SEMICOLON"):
            self._match("SEMICOLON")

        t = TreeNode("StmtK", "DoWhileK", lineno=do_tok.line)
        t.op = cond_tok.lexeme
        t.child.append(body)
        t.child.append(cond)
        return t

    def _parse_read_stmt(self) -> TreeNode:
        """
        Analiza entrada estándar:
        Soporta 'sphone(x);' y 'cin >> x;'
        """
        read_tok = self._match({"KW_SPHONE", "KW_CIN"})

        if self._check("LPAREN"):
            self._match("LPAREN")
            id_tok = self._match("IDENTIFIER")
            self._match("RPAREN")
        else:
            # Soporte para operador flujo de entrada >> (dos tokens GT consecutivos)
            if self._check("GT"):
                self._match("GT")
                self._match("GT")
            id_tok = self._match("IDENTIFIER")

        self._match("SEMICOLON")

        t = TreeNode("StmtK", "ReadK", lineno=read_tok.line)
        t.name = id_tok.lexeme
        return t

    def _parse_write_stmt(self) -> TreeNode:
        """
        Analiza salida estándar:
        Soporta 'dmail("x", y);' y 'cout << x << y;' con expresiones compuestas
        """
        write_tok = self._match({"KW_DMAIL", "KW_COUT"})

        t = TreeNode("StmtK", "WriteK", lineno=write_tok.line)

        # 1. Estilo función: dmail(arg1, arg2);
        if self._check("LPAREN"):
            self._match("LPAREN")
            while True:
                t.child.append(self._parse_expr())

                if self._check("COMMA"):
                    self._match("COMMA")
                elif self._check("LT"):
                    self._match("LT")
                    self._match("LT")
                else:
                    break
            self._match("RPAREN")
        # 2. Estilo flujo: cout << arg1 << arg2;
        else:
            while True:
                # Consumir operador flujo salida << (dos tokens LT consecutivos)
                self._match("LT")
                self._match("LT")

                t.child.append(self._parse_expr())

                if self._check("LT") and self.index + 1 < len(self.tokens) and self.tokens[self.index + 1].token_type == "LT":
                    continue
                else:
                    break

        self._match("SEMICOLON")
        return t

    # -----------------------------------------------------------------
    # MÉTODOS DE ANÁLISIS DE EXPRESIONES (PRECAUCIÓN DE PRECEDENCIA)
    # -----------------------------------------------------------------

    def _parse_expr(self) -> TreeNode:
        """
        Nivel 1: Expresiones relacionales
        expresion -> expresion_simple [ rel_op expresion_simple ]
        """
        t = self._parse_expr_simple()

        rel_ops = {"LT", "GT", "LTE", "GTE", "EQ", "NEQ"}
        if self._check(rel_ops):
            # Si el token es '<' (LT) y el siguiente también es '<' (LT), no es un operador relacional,
            # sino que es parte del operador de flujo '<<' de cout/dmail.
            is_stream_op = False
            if self._check("LT") and self.index + 1 < len(self.tokens) and self.tokens[self.index + 1].token_type == "LT":
                is_stream_op = True

            if not is_stream_op:
                op_tok = self._match(rel_ops)
                p = TreeNode("ExpK", "OpK", lineno=op_tok.line)
                p.op = op_tok.lexeme
                p.child.append(t)
                p.child.append(self._parse_expr_simple())
                t = p
        return t

    def _parse_expr_simple(self) -> TreeNode:
        """
        Nivel 2: Expresiones aditivas y operadores lógicos aditivos (or)
        expresion_simple -> termino [ suma_op termino ]*
        """
        t = self._parse_term()

        sum_ops = {"PLUS", "MINUS", "OR_OP"}
        while self._check(sum_ops):
            op_tok = self._match(sum_ops)
            p = TreeNode("ExpK", "OpK", lineno=op_tok.line)
            p.op = op_tok.lexeme
            p.child.append(t)
            p.child.append(self._parse_term())
            t = p
        return t

    def _parse_term(self) -> TreeNode:
        """
        Nivel 3: Expresiones multiplicativas y lógicas multiplicativas (and)
        termino -> factor [ mult_op factor ]*
        """
        t = self._parse_factor()

        mult_ops = {"TIMES", "DIV", "MOD", "AND_OP"}
        while self._check(mult_ops):
            op_tok = self._match(mult_ops)
            p = TreeNode("ExpK", "OpK", lineno=op_tok.line)
            p.op = op_tok.lexeme
            p.child.append(t)
            p.child.append(self._parse_factor())
            t = p
        return t

    def _parse_factor(self) -> TreeNode:
        """
        Nivel 4: Exponentes/Potencia (^)
        factor -> componente [ pot_op componente ]*
        """
        t = self._parse_componente()
        
        # Reconocer el símbolo de potencia si el token es un punto que guarda el lexema '^'
        while self._check("DOT") and self._current_token().lexeme == "^":
            op_tok = self._match("DOT")
            p = TreeNode("ExpK", "OpK", lineno=op_tok.line)
            p.op = "^"
            p.child.append(t)
            p.child.append(self._parse_componente())
            t = p
        return t

    def _parse_componente(self) -> TreeNode:
        """
        Nivel 5: Terminales y operadores unarios
        componente -> ( expr ) | número | id | bool | un_op componente
        """
        tok = self._current_token()

        # Expresiones entre paréntesis
        if tok.token_type == "LPAREN":
            self._match("LPAREN")
            t = self._parse_expr()
            self._match("RPAREN")
            return t
        # Literales enteros
        elif tok.token_type == "INTEGER_LITERAL":
            self._match("INTEGER_LITERAL")
            t = TreeNode("ExpK", "ConstK", lineno=tok.line)
            t.val = int(tok.lexeme)
            return t
        # Literales flotantes
        elif tok.token_type == "FLOAT_LITERAL":
            self._match("FLOAT_LITERAL")
            t = TreeNode("ExpK", "ConstK", lineno=tok.line)
            t.val = float(tok.lexeme)
            return t
        # Literales booleanos
        elif tok.token_type in {"KW_TRUE", "KW_FALSE"}:
            self._match({"KW_TRUE", "KW_FALSE"})
            t = TreeNode("ExpK", "ConstK", lineno=tok.line)
            t.val = (tok.token_type == "KW_TRUE")
            return t
        # Literales de cadena
        elif tok.token_type == "STRING_LITERAL":
            self._match("STRING_LITERAL")
            t = TreeNode("ExpK", "StringK", lineno=tok.line)
            t.val = tok.lexeme.strip('"')
            return t
        # Operadores unarios (!, -, +)
        elif tok.token_type in {"NOT_OP", "MINUS", "PLUS"}:
            op_tok = self._match({"NOT_OP", "MINUS", "PLUS"})
            t = TreeNode("ExpK", "OpK", lineno=op_tok.line)
            t.op = op_tok.lexeme
            t.child.append(self._parse_componente())
            return t
        # Identificadores (variables y llamadas a función dentro de una expresión)
        elif tok.token_type == "IDENTIFIER":
            id_tok = self._match("IDENTIFIER")

            # Si es seguido por paréntesis, se evalúa como llamada a función en una expresión
            if self._check("LPAREN"):
                self._match("LPAREN")
                t = TreeNode("ExpK", "CallK", lineno=id_tok.line)
                t.name = id_tok.lexeme
                if not self._check("RPAREN"):
                    while True:
                        t.child.append(self._parse_expr())
                        if self._check("COMMA"):
                            self._match("COMMA")
                        else:
                            break
                self._match("RPAREN")
                return t
            else:
                t = TreeNode("ExpK", "IdK", lineno=id_tok.line)
                t.name = id_tok.lexeme
                return t
        else:
            raise SyntaxError(
                tok.line,
                tok.column_start,
                "Se esperaba un identificador, un valor constante (entero, real, booleano, cadena), un operador unario ('!', '-', '+') o un paréntesis de apertura '('",
                tok.lexeme
            )


# =====================================================================
# RENDERIZADO VISUAL DEL AST (FOLDER-TREE RENDERER)
# =====================================================================

def print_tree_graphical(node: Optional[TreeNode], prefix: str = "", is_last: bool = True) -> str:
    """
    Función de renderizado gráfico premium y estético en formato jerárquico tipo carpeta.
    Traduce recursivamente los nodos del AST utilizando caracteres UTF-8.
    """
    if node is None:
        return ""

    # Caso especial pedagógico: omitir la impresión del nodo intermedio 'Secuencia de Sentencias'
    # para evitar sobrecargar visualmente el árbol y mantenerlo limpio y conciso.
    if node.nodekind == "StmtK" and node.kind == "BlockK" and node.name == "Secuencia de Sentencias":
        result = ""
        children = [c for c in node.child if c is not None]
        for i, child in enumerate(children):
            result += print_tree_graphical(child, prefix, is_last and (i == len(children) - 1))
        return result

    # Generar la descripción estéticamente formateada según el tipo de nodo
    desc = ""
    if node.nodekind == "DeclK":
        if node.kind == "DeclVarK":
            desc = f"[Declaración de Variable] Tipo: {node.type}"
        elif node.kind == "VarK":
            init_suffix = " (Inicializada)" if node.child else ""
            desc = f"[Variable] ID: {node.name}{init_suffix}"
        elif node.kind == "FuncK":
            params_str = ", ".join(f"{t} {n}" for t, n in node.params)
            desc = f"[Definición de Función] Tipo: {node.type}, Nombre: {node.name}({params_str})"
    elif node.nodekind == "StmtK":
        if node.kind == "IfK":
            desc = "[Condicional / choice (if)]"
        elif node.kind == "WhileK":
            desc = "[Bucle / loop (while)]"
        elif node.kind == "DoWhileK":
            desc = f"[Bucle / pulse (do-{node.op or 'while'})]"
        elif node.kind == "AssignK":
            desc = f"[Asignación] ID: {node.name}"
        elif node.kind == "ReadK":
            desc = f"[Entrada / sphone (cin)] ID: {node.name}"
        elif node.kind == "WriteK":
            desc = "[Salida / dmail (cout)]"
        elif node.kind == "ReturnK":
            desc = "[Retorno / return]"
        elif node.kind == "BlockK":
            desc = f"[Bloque de Código / {node.name or '{...}'}]"
        elif node.kind == "CallStmtK":
            desc = f"[Llamada a Función] Nombre: {node.name}"
    elif node.nodekind == "ExpK":
        if node.kind == "OpK":
            desc = f"[Operador] '{node.op}'"
        elif node.kind == "ConstK":
            desc = f"[Constante] Valor: {node.val}"
        elif node.kind == "IdK":
            desc = f"[Variable / ID] Nombre: {node.name}"
        elif node.kind == "StringK":
            desc = f"[Cadena] \"{node.val}\""
        elif node.kind == "CallK":
            desc = f"[Llamada a Función en Expresión] Nombre: {node.name}"

    # Construir la estructura visual utilizando caracteres tipo carpeta
    marker = "└── " if is_last else "├── "
    result = f"{prefix}{marker}{desc} @ {node.lineno}\n"

    next_prefix = prefix + ("    " if is_last else "│   ")

    # Filtrar nodos hijos nulos
    children = [c for c in node.child if c is not None]
    
    # Agregar etiquetas informativas a los bloques lógicos de sentencias de control
    if node.kind == "IfK":
        labels = ["Condición", "Rama Entonces", "Rama Sino"]
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
        labels = ["Condición", "Cuerpo del Bucle"]
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
        labels = ["Cuerpo del Bucle", "Condición"]
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

    # Imprimir recursivamente cada uno de los hijos estructurados
    for i, child in enumerate(children):
        result += print_tree_graphical(child, next_prefix, i == len(children) - 1)

    return result
