import html
import re

from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget, QTextEdit

from ide.theme import steins_gate_theme


class AnalysisPanel(QTabWidget):
    def __init__(self) -> None:
        super().__init__()

        self._tokens = self._make_rich_output("Tokens léxicos aparecerán aquí.")
        self._syntax = self._make_output("Árbol sintáctico / salida estructurada.")
        self._semantic = self._make_output("Resultados semánticos y validaciones.")
        self._intermediate = self._make_output("Código intermedio (tres direcciones, etc.).")
        self._symbols = self._make_output("Tabla de símbolos.")

        self.addTab(self._tokens, "Tokens")
        self.addTab(self._syntax, "Sintáctico")
        self.addTab(self._semantic, "Semántico")
        self.addTab(self._intermediate, "Intermedio")
        self.addTab(self._symbols, "Símbolos")

    def set_tokens(self, text: str) -> None:
        self._tokens.setHtml(self._tokens_to_html(text))

    def set_syntax(self, text: str) -> None:
        self._syntax.setPlainText(text)

    def set_semantic(self, text: str) -> None:
        self._semantic.setPlainText(text)

    def set_intermediate(self, text: str) -> None:
        self._intermediate.setPlainText(text)

    def set_symbols(self, text: str) -> None:
        self._symbols.setPlainText(text)

    @staticmethod
    def _make_output(text: str) -> QPlainTextEdit:
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setPlainText(text)
        return output

    @staticmethod
    def _make_rich_output(text: str) -> QTextEdit:
        output = QTextEdit()
        output.setReadOnly(True)
        output.setPlainText(text)
        return output

    def _tokens_to_html(self, text: str) -> str:
        colors = steins_gate_theme.get_colors()
        base_color = colors.foreground

        color_map = {
            "KW_": colors.keywords,
            "STRING_LITERAL": colors.strings,
            "INTEGER_LITERAL": colors.numbers,
            "FLOAT_LITERAL": colors.numbers,
            "ASSIGN": colors.operators,
            "PLUS": colors.operators,
            "MINUS": colors.operators,
            "TIMES": colors.operators,
            "DIV": colors.operators,
            "MOD": colors.operators,
            "EQ": colors.operators,
            "NEQ": colors.operators,
            "LT": colors.operators,
            "LTE": colors.operators,
            "GT": colors.operators,
            "GTE": colors.operators,
            "INC": colors.operators,
            "DEC": colors.operators,
            "PLUS_ASSIGN": colors.operators,
            "MINUS_ASSIGN": colors.operators,
            "TIMES_ASSIGN": colors.operators,
            "DIV_ASSIGN": colors.operators,
            "MOD_ASSIGN": colors.operators,
            "AND_OP": colors.operators,
            "OR_OP": colors.operators,
            "NOT_OP": colors.operators,
            "LPAREN": colors.operators,
            "RPAREN": colors.operators,
            "LBRACE": colors.operators,
            "RBRACE": colors.operators,
            "LBRACKET": colors.operators,
            "RBRACKET": colors.operators,
            "SEMICOLON": colors.operators,
            "COMMA": colors.operators,
            "DOT": colors.operators,
            "COLON": colors.operators,
        }

        row_re = re.compile(r"^\[(?P<ttype>[A-Z_]+):(?P<lex>.*)\] @ (?P<pos>.+)$")
        rendered_lines: list[str] = []

        for line in text.splitlines():
            match = row_re.match(line)
            if not match:
                rendered_lines.append(html.escape(line))
                continue

            ttype = match.group("ttype")
            lex = match.group("lex")
            pos = match.group("pos")

            color = color_map.get(ttype)
            if color is None and ttype.startswith("KW_"):
                color = colors.keywords
            if color is None and ttype == "IDENTIFIER":
                color = colors.foreground
            if color is None:
                color = base_color

            rendered_lines.append(
                "["
                f"<span style='color:{html.escape(color)}'>{html.escape(ttype)}</span>"
                ":"
                f"<span style='color:{html.escape(color)}'>{html.escape(lex)}</span>"
                "] @ "
                f"<span style='color:{html.escape(colors.comments)}'>{html.escape(pos)}</span>"
            )

        return (
            f"<div style='font-family: Consolas, monospace; color: {html.escape(base_color)};'>"
            + "<br/>".join(rendered_lines)
            + "</div>"
        )
