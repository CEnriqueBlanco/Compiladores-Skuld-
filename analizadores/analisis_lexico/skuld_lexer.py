from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass(frozen=True)
class Token:
    token_type: str
    lexeme: str
    line: int
    column_start: int
    column_end: int


class LexicalError(Exception):
    def __init__(self, line: int, column: int, description: str, lexeme: str = "") -> None:
        self.line = line
        self.column = column
        self.description = description
        self.lexeme = lexeme
        suffix = f" -> '{lexeme}'" if lexeme else ""
        super().__init__(f"ERROR_LEXICO({line}, {column}): {description}{suffix}")


KEYWORDS: Dict[str, str] = {
    # Skuld
    "labmem": "KW_LABMEM",
    "worldline": "KW_WORLDLINE",
    "divergence": "KW_DIVERGENCE",
    "dmail": "KW_DMAIL",
    "sphone": "KW_SPHONE",
    "reading": "KW_READING",
    "choice": "KW_CHOICE",
    "else": "KW_ELSE",
    "fork": "KW_FORK",
    "path": "KW_PATH",
    "gate": "KW_GATE",
    "loop": "KW_LOOP",
    "pulse": "KW_PULSE",
    "seal": "KW_SEAL",
    "shift": "KW_SHIFT",
    "jump": "KW_JUMP",
    "return": "KW_RETURN",
    "steiner": "KW_STEINER",
    "void": "KW_VOID",
    "true": "KW_TRUE",
    "false": "KW_FALSE",
    # Basico / aliases tradicionales
    "int": "KW_INT",
    "float": "KW_FLOAT",
    "string": "KW_STRING",
    "bool": "KW_BOOL",
    "if": "KW_IF",
    "then": "KW_THEN",
    "switch": "KW_SWITCH",
    "case": "KW_CASE",
    "main": "KW_MAIN",
    "while": "KW_WHILE",
    "do": "KW_DO",
    "end": "KW_END",
    "until": "KW_UNTIL",
    "cin": "KW_CIN",
    "cout": "KW_COUT",
    "read": "KW_READ",
    "write": "KW_WRITE",
}

WORD_LOGIC_TO_OPERATOR: Dict[str, str] = {
    "and": "AND_OP",
    "or": "OR_OP",
    "not": "NOT_OP",
}

MULTI_CHAR_OPERATORS: Dict[str, str] = {
    "==": "EQ",
    "!=": "NEQ",
    "<=": "LTE",
    ">=": "GTE",
    "++": "INC",
    "--": "DEC",
    "+=": "PLUS_ASSIGN",
    "-=": "MINUS_ASSIGN",
    "*=": "TIMES_ASSIGN",
    "/=": "DIV_ASSIGN",
    "%=": "MOD_ASSIGN",
    "&&": "AND_OP",
    "||": "OR_OP",
}

SINGLE_CHAR_TOKENS: Dict[str, str] = {
    "=": "ASSIGN",
    "+": "PLUS",
    "-": "MINUS",
    "*": "TIMES",
    "/": "DIV",
    "%": "MOD",
    "<": "LT",
    ">": "GT",
    "!": "NOT_OP",
    "(": "LPAREN",
    ")": "RPAREN",
    "{": "LBRACE",
    "}": "RBRACE",
    "[": "LBRACKET",
    "]": "RBRACKET",
    ";": "SEMICOLON",
    ",": "COMMA",
    ".": "DOT",
    ":": "COLON",
}

VALID_ESCAPES = {'"', "\\", "n", "r", "t"}


class SkuldLexer:
    def __init__(self, source_code: str) -> None:
        self.source = source_code
        self.length = len(source_code)
        self.index = 0
        self.line = 1
        self.column = 1

    def tokenize(self) -> List[Token]:
        tokens: List[Token] = []
        while True:
            token = self.next_token()
            tokens.append(token)
            if token.token_type == "ENDFILE":
                break
        return tokens

    def next_token(self) -> Token:
        self._skip_whitespace_and_comments()
        if self._is_at_end():
            return Token("ENDFILE", "", self.line, self.column, self.column)

        ch = self._current_char()
        start_line = self.line
        start_col = self.column

        if ch == '"':
            return self._scan_string(start_line, start_col)

        if ch.isdigit() or (ch == "." and self._peek_char() and self._peek_char().isdigit()):
            return self._scan_number(start_line, start_col)

        if ch.isalpha() or ch == "_":
            return self._scan_identifier_or_keyword(start_line, start_col)

        two_chars = ch + (self._peek_char() or "")
        if two_chars in MULTI_CHAR_OPERATORS:
            self._advance()
            self._advance()
            token_type = MULTI_CHAR_OPERATORS[two_chars]
            return Token(token_type, two_chars, start_line, start_col, self.column - 1)

        if ch in SINGLE_CHAR_TOKENS:
            self._advance()
            token_type = SINGLE_CHAR_TOKENS[ch]
            return Token(token_type, ch, start_line, start_col, self.column - 1)

        self._advance()
        raise LexicalError(start_line, start_col, "Caracter no reconocido", ch)

    def _scan_identifier_or_keyword(self, start_line: int, start_col: int) -> Token:
        lexeme = self._consume_while(lambda c: c.isalnum() or c == "_")

        if lexeme in WORD_LOGIC_TO_OPERATOR:
            token_type = WORD_LOGIC_TO_OPERATOR[lexeme]
        elif lexeme in KEYWORDS:
            token_type = KEYWORDS[lexeme]
        else:
            token_type = "IDENTIFIER"

        return Token(token_type, lexeme, start_line, start_col, self.column - 1)

    def _scan_number(self, start_line: int, start_col: int) -> Token:
        lexeme = ""
        is_float = False

        if self._current_char() == ".":
            is_float = True
            lexeme += self._advance() or ""
            fractional = self._consume_while(str.isdigit)
            if not fractional:
                raise LexicalError(start_line, start_col, "Numero mal formado", lexeme)
            lexeme += fractional
        else:
            integer_part = self._consume_while(str.isdigit)
            lexeme += integer_part

            if len(integer_part) > 1 and integer_part[0] == "0":
                raise LexicalError(start_line, start_col, "Numero mal formado (cero a la izquierda)", integer_part)

            if self._current_char() == ".":
                is_float = True
                lexeme += self._advance() or ""
                fractional = self._consume_while(str.isdigit)
                if not fractional:
                    raise LexicalError(start_line, start_col, "Numero mal formado", lexeme)
                lexeme += fractional

        if self._current_char() in ("e", "E"):
            is_float = True
            lexeme += self._advance() or ""
            if self._current_char() in ("+", "-"):
                lexeme += self._advance() or ""
            exp_digits = self._consume_while(str.isdigit)
            if not exp_digits:
                raise LexicalError(start_line, start_col, "Numero mal formado", lexeme)
            lexeme += exp_digits

        if self._current_char() == ".":
            bad_lexeme = lexeme + "."
            self._advance()
            raise LexicalError(start_line, start_col, "Numero mal formado", bad_lexeme)

        if self._current_char().isalpha() or self._current_char() == "_":
            suffix = self._consume_while(lambda c: c.isalnum() or c == "_")
            raise LexicalError(start_line, start_col, "Identificador mal formado", lexeme + suffix)

        token_type = "FLOAT_LITERAL" if is_float else "INTEGER_LITERAL"
        return Token(token_type, lexeme, start_line, start_col, self.column - 1)

    def _scan_string(self, start_line: int, start_col: int) -> Token:
        lexeme = self._advance() or ""
        while not self._is_at_end():
            ch = self._current_char()
            if ch == '"':
                lexeme += self._advance() or ""
                return Token("STRING_LITERAL", lexeme, start_line, start_col, self.column - 1)

            if ch == "\\":
                lexeme += self._advance() or ""
                if self._is_at_end():
                    raise LexicalError(start_line, start_col, "Cadena no terminada", lexeme)
                esc = self._current_char()
                if esc not in VALID_ESCAPES:
                    bad = lexeme + esc
                    self._advance()
                    raise LexicalError(start_line, start_col, "Secuencia de escape invalida", bad)
                lexeme += self._advance() or ""
                continue

            if ch in ("\n", "\r"):
                raise LexicalError(start_line, start_col, "Cadena no terminada", lexeme)

            lexeme += self._advance() or ""

        raise LexicalError(start_line, start_col, "Cadena no terminada", lexeme)

    def _skip_whitespace_and_comments(self) -> None:
        while not self._is_at_end():
            ch = self._current_char()

            if ch in (" ", "\t", "\n", "\r"):
                self._advance()
                continue

            next_ch = self._peek_char()

            if ch == "/" and next_ch == "/":
                self._advance()
                self._advance()
                while not self._is_at_end() and self._current_char() not in ("\n", "\r"):
                    self._advance()
                continue

            if ch == "<" and next_ch == ">":
                self._advance()
                self._advance()
                while not self._is_at_end() and self._current_char() not in ("\n", "\r"):
                    self._advance()
                continue

            if ch == "<" and next_ch not in ("=", ">") and self._is_line_comment_start():
                start_line = self.line
                start_col = self.column
                self._advance()
                while not self._is_at_end() and self._current_char() != ">":
                    self._advance()
                if self._is_at_end():
                    raise LexicalError(start_line, start_col, "Comentario entre < > no terminado", "<")
                self._advance()
                continue

            if ch == "/" and next_ch == "*":
                start_line = self.line
                start_col = self.column
                self._advance()
                self._advance()
                while not self._is_at_end():
                    if self._current_char() == "*" and self._peek_char() == "/":
                        self._advance()
                        self._advance()
                        break
                    self._advance()
                else:
                    raise LexicalError(start_line, start_col, "Comentario de bloque no terminado", "/*")
                continue

            break

    def _consume_while(self, predicate) -> str:
        chars: List[str] = []
        while not self._is_at_end() and predicate(self._current_char()):
            chars.append(self._advance() or "")
        return "".join(chars)

    def _is_at_end(self) -> bool:
        return self.index >= self.length

    def _is_line_comment_start(self) -> bool:
        # Permite comentarios <...> cuando el '<' aparece al inicio logico de linea.
        i = self.index - 1
        while i >= 0 and self.source[i] not in ("\n", "\r"):
            if self.source[i] not in (" ", "\t"):
                return False
            i -= 1
        return True

    def _current_char(self) -> str:
        if self._is_at_end():
            return ""
        return self.source[self.index]

    def _peek_char(self) -> Optional[str]:
        if self.index + 1 >= self.length:
            return None
        return self.source[self.index + 1]

    def _advance(self) -> Optional[str]:
        if self._is_at_end():
            return None

        ch = self.source[self.index]
        self.index += 1

        if ch == "\n":
            self.line += 1
            self.column = 1
        else:
            self.column += 1

        return ch


def tokenize(source_code: str) -> List[Token]:
    lexer = SkuldLexer(source_code)
    return lexer.tokenize()


def tokenize_file(file_path: str, encoding: str = "utf-8") -> List[Token]:
    with open(file_path, "r", encoding=encoding) as f:
        return tokenize(f.read())


if __name__ == "__main__":
    example = """
    <> El Psy Kongroo
    labmem worldline x = 10;
    choice (x > 0 and x < 20) {
        dmail(\"Hola\");
    }
    """

    try:
        for t in tokenize(example):
            print(f"[{t.token_type}:{t.lexeme!r}] @ {t.line}:{t.column_start}-{t.column_end}")
    except LexicalError as err:
        print(err)
