import html
import re

from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget, QTextEdit, QStackedWidget, QTreeWidget, QTreeWidgetItem
from PyQt5.QtCore import pyqtSignal, Qt

from ide.theme import steins_gate_theme
from ide.console_panel import ErrorHoverEventFilter


class SyntaxTreeWidget(QStackedWidget):
    line_selected = pyqtSignal(int)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setColumnCount(1)
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.text_widget = QPlainTextEdit()
        self.text_widget.setReadOnly(True)
        
        self.addWidget(self.tree_widget)
        self.addWidget(self.text_widget)
        
        self.setCurrentWidget(self.text_widget)
        self.text_widget.setPlainText("Árbol sintáctico / salida estructurada.")

    def setPlainText(self, text: str) -> None:
        """Fallback method to keep compatibility with other text-setting mechanisms if any."""
        self.set_syntax_content(text)

    def on_selection_changed(self) -> None:
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            line_no = item.data(0, Qt.UserRole)
            if line_no is not None:
                self.line_selected.emit(line_no)

    def set_syntax_content(self, text: str) -> None:
        text_stripped = text.strip()
        if not text_stripped:
            self.text_widget.clear()
            self.tree_widget.clear()
            self.setCurrentWidget(self.text_widget)
            return

        # If it doesn't look like a graphical tree representation, show text
        if not any(marker in text_stripped for marker in ["├──", "└──", "│"]):
            self.text_widget.setPlainText(text)
            self.setCurrentWidget(self.text_widget)
            return

        self.tree_widget.clear()
        lines = text.splitlines()
        items_at_level = {}

        for line in lines:
            if not line.strip():
                continue

            idx = line.find('[')
            if idx == -1:
                level = 0
                node_text = line.strip(' │├└─')
                line_no = None
            else:
                level = (idx // 4) - 1
                if level < 0:
                    level = 0
                full_desc = line[idx:].strip()
                if ' @ ' in full_desc:
                    node_text, line_str = full_desc.rsplit(' @ ', 1)
                    try:
                        line_no = int(line_str.strip())
                    except ValueError:
                        line_no = None
                else:
                    node_text = full_desc
                    line_no = None

            item = QTreeWidgetItem([node_text])
            if line_no is not None:
                item.setData(0, Qt.UserRole, line_no)

            if level == 0:
                self.tree_widget.addTopLevelItem(item)
            else:
                parent_level = level - 1
                parent_item = items_at_level.get(parent_level)
                if parent_item:
                    parent_item.addChild(item)
                else:
                    self.tree_widget.addTopLevelItem(item)

            items_at_level[level] = item

        self.tree_widget.expandAll()  # Requisito: expandir automáticamente al ejecutarse
        self.setCurrentWidget(self.tree_widget)


class AnalysisPanel(QTabWidget):
    error_selected = pyqtSignal(int, int, int)  # line, column, length

    def __init__(self) -> None:
        super().__init__()

        self._tokens = self._make_rich_output("Tokens léxicos aparecerán aquí.")
        self._syntax = SyntaxTreeWidget()
        self._semantic = self._make_output("Resultados semánticos y validaciones.")
        self._intermediate = self._make_output("Código intermedio (tres direcciones, etc.).")
        self._symbols = self._make_output("Tabla de símbolos.")

        self.addTab(self._tokens, "Tokens")
        self.addTab(self._syntax, "Sintáctico")
        self.addTab(self._semantic, "Semántico")
        self.addTab(self._intermediate, "Intermedio")
        self.addTab(self._symbols, "Símbolos")

        # Connect position changes to error navigation
        self._tokens.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)
        self._syntax.text_widget.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)
        self._semantic.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)
        self._intermediate.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)
        self._symbols.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)

        # Install pointing hand cursor filter when hovering over error lines
        self._tokens_hover_filter = ErrorHoverEventFilter(self._tokens)
        self._syntax_hover_filter = ErrorHoverEventFilter(self._syntax.text_widget)
        self._semantic_hover_filter = ErrorHoverEventFilter(self._semantic)
        self._intermediate_hover_filter = ErrorHoverEventFilter(self._intermediate)
        self._symbols_hover_filter = ErrorHoverEventFilter(self._symbols)

    def set_tokens(self, text: str) -> None:
        self._tokens.setHtml(self._tokens_to_html(text))

    def set_syntax(self, text: str) -> None:
        self._syntax.set_syntax_content(text)

    def set_semantic(self, text: str) -> None:
        self._semantic.setPlainText(text)

    def set_intermediate(self, text: str) -> None:
        self._intermediate.setPlainText(text)

    def set_symbols(self, text: str) -> None:
        self._symbols.setPlainText(text)

    def _on_text_widget_cursor_changed(self) -> None:
        widget = self.sender()
        if not isinstance(widget, (QPlainTextEdit, QTextEdit)):
            return

        cursor = widget.textCursor()
        line_text = cursor.block().text().strip()
        if not line_text:
            return

        import re
        match = re.search(r"ERROR_(LEXICO|SINTACTICO|SEMANTICO)\((\d+),\s*(\d+)\)", line_text)
        if match:
            line_no = int(match.group(2))
            col_no = int(match.group(3))

            # Extract lexeme length if present (e.g. -> 'lexeme')
            span_len = 1
            lex_match = re.search(r" -> '(.*)'\s*$", line_text)
            if lex_match:
                span_len = max(1, len(lex_match.group(1)))

            self.error_selected.emit(line_no, col_no, span_len)

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
