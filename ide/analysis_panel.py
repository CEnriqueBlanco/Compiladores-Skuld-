import html
import re

from PyQt5.QtWidgets import (
    QAbstractItemView,
    QHeaderView,
    QPlainTextEdit,
    QTabWidget,
    QTextEdit,
    QStackedWidget,
    QTableWidget,
    QTableWidgetItem,
    QTreeWidget,
    QTreeWidgetItem,
)
from PyQt5.QtCore import pyqtSignal, Qt
from PyQt5.QtGui import QColor, QPalette

from ide.theme import steins_gate_theme
from ide.console_panel import ErrorHoverEventFilter, TokenHoverEventFilter


class SyntaxTreeWidget(QStackedWidget):
    line_selected = pyqtSignal(int, str)  # line number, search term

    def __init__(self, parent=None):
        super().__init__(parent)
        
        self.tree_widget = QTreeWidget()
        self.tree_widget.setHeaderHidden(True)
        self.tree_widget.setColumnCount(1)
        self.tree_widget.header().setSectionResizeMode(0, QHeaderView.Fixed)
        self.tree_widget.header().setStretchLastSection(False)
        self.tree_widget.setTextElideMode(Qt.ElideNone)
        self.tree_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.tree_widget.itemSelectionChanged.connect(self.on_selection_changed)
        
        self.text_widget = QPlainTextEdit()
        self.text_widget.setReadOnly(True)
        self.text_widget.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.text_widget.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self._error_lines: set[int] = set()
        
        self.addWidget(self.tree_widget)
        self.addWidget(self.text_widget)

        self.setCurrentWidget(self.text_widget)
        self.text_widget.setPlainText("Árbol sintáctico / salida estructurada.")
        self.refresh_theme()

    @staticmethod
    def _item_color(text: str, colors) -> str:
        """Choose a theme color for the kind of AST node displayed."""
        if "[ERROR" in text or "[Error semántico]" in text:
            return steins_gate_theme.get_error_colors().text
        if any(label in text for label in (
            "[Declaración de Variable]",
            "[Variable]",
            "[Definición de Función]",
        )):
            return colors.keywords
        if any(label in text for label in (
            "[Condicional",
            "[Bucle",
            "[Bloque de Código",
            "[Entrada",
            "[Salida",
            "[Retorno",
        )):
            return colors.accent
        if "[Asignación]" in text or "[Operador]" in text:
            return colors.operators
        if "[Constante]" in text or "[Cadena]" in text:
            return colors.numbers if "[Constante]" in text else colors.strings
        if "[Llamada" in text:
            return colors.strings
        if "[Variable / ID]" in text:
            return colors.strings
        return colors.foreground

    def _color_tree_items(self) -> None:
        colors = steins_gate_theme.get_colors()

        def color_item(item: QTreeWidgetItem) -> None:
            item.setForeground(0, QColor(self._item_color(item.text(0), colors)))
            for child_index in range(item.childCount()):
                color_item(item.child(child_index))

        for index in range(self.tree_widget.topLevelItemCount()):
            color_item(self.tree_widget.topLevelItem(index))

    def refresh_theme(self) -> None:
        colors = steins_gate_theme.get_colors()
        self.tree_widget.setStyleSheet(
            f"""
            QTreeWidget {{
                background-color: {colors.background};
                color: {colors.foreground};
                border: 1px solid {colors.border};
                selection-background-color: {colors.selection};
                selection-color: {colors.foreground};
            }}
            QTreeWidget::item:hover {{
                background-color: {colors.hover};
            }}
            """
        )
        self.text_widget.setStyleSheet(
            f"""
            QPlainTextEdit {{
                background-color: {colors.background};
                color: {colors.foreground};
                border: 1px solid {colors.border};
                selection-background-color: {colors.selection};
            }}
            """
        )
        self._color_tree_items()

    def setPlainText(self, text: str) -> None:
        """Fallback method to keep compatibility with other text-setting mechanisms if any."""
        self.set_syntax_content(text)

    @staticmethod
    def _extract_search_term(item_text: str) -> str:
        """Extract the most useful identifier/value from a tree node label to locate it in the source line."""
        # ID: varname  /  Nombre: funcname
        m = re.search(r'\bID:\s+(\w+)', item_text)
        if m:
            return m.group(1)
        m = re.search(r'\bNombre:\s+(\w+)', item_text)
        if m:
            return m.group(1)
        # Valor: 42 / Valor: 3.14 / Valor: True
        m = re.search(r'\bValor:\s+(\S+)', item_text)
        if m:
            return m.group(1)
        # Operador '+', '<=', etc.  →  '[Operador] \'*\''
        m = re.search(r"'([^']+)'", item_text)
        if m:
            return m.group(1)
        # Cadena "hello"
        m = re.search(r'"([^"]+)"', item_text)
        if m:
            return m.group(1)
        return ""

    def on_selection_changed(self) -> None:
        selected_items = self.tree_widget.selectedItems()
        if selected_items:
            item = selected_items[0]
            line_no = item.data(0, Qt.UserRole)
            if line_no is not None:
                search_term = self._extract_search_term(item.text(0))
                self.line_selected.emit(line_no, search_term)

    def set_syntax_content(self, text: str, error_text: str = "") -> None:
        self._error_lines = {
            int(match.group(1))
            for match in re.finditer(
                r"ERROR_(?:LEXICO|SINTACTICO|SEMANTICO)\((\d+),",
                error_text,
            )
        }
        error_messages: dict[int, list[str]] = {}
        for match in re.finditer(
            r"ERROR_(?:LEXICO|SINTACTICO|SEMANTICO)\((\d+),\s*\d+\):\s*(.*)",
            error_text,
        ):
            line_no = int(match.group(1))
            message = match.group(2).strip()
            message = re.sub(r"\s*->\s*'.*'\s*$", "", message)
            if message:
                error_messages.setdefault(line_no, []).append(message)
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
        parsed_items = []

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
            parsed_items.append((item, line_no, node_text))

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

        # Una línea puede corresponder a varios nodos del AST. Marca solo el
        # nodo más representativo para evitar repetir el mismo error en todo
        # el subárbol de una declaración o expresión.
        priority = (
            "[Error semántico]",
            "[Asignación]",
            "[Variable / ID]",
            "[Variable]",
            "[Operador]",
            "[Llamada",
            "[Declaración de Variable]",
        )
        selected_by_line = {}
        explicit_error_lines = {
            line_no
            for _, line_no, node_text in parsed_items
            if line_no in self._error_lines and "[Error semántico]" in node_text
        }
        for item, line_no, node_text in parsed_items:
            if line_no not in self._error_lines:
                continue
            if line_no in explicit_error_lines:
                continue
            node_priority = next(
                (len(priority) - index for index, label in enumerate(priority) if label in node_text),
                0,
            )
            current = selected_by_line.get(line_no)
            if current is None or node_priority > current[0]:
                selected_by_line[line_no] = (node_priority, item)

        for line_no, (_, item) in selected_by_line.items():
            messages = error_messages.get(line_no, [])
            if "[Error semántico]" in item.text(0):
                item.setText(0, f"[ERROR] {item.text(0)}")
            elif messages:
                details = " | ".join(dict.fromkeys(messages))
                item.setText(0, f"[ERROR: {details}] {item.text(0)}")
            else:
                item.setText(0, f"[ERROR] {item.text(0)}")

        self.tree_widget.expandAll()  # Requisito: expandir automáticamente al ejecutarse
        self.tree_widget.resizeColumnToContents(0)
        self._color_tree_items()
        self.setCurrentWidget(self.tree_widget)


class AnalysisPanel(QTabWidget):
    error_selected = pyqtSignal(int, int, int)  # line, column, length

    def __init__(self) -> None:
        super().__init__()

        self._tokens = self._make_rich_output("Tokens léxicos aparecerán aquí.")
        self._syntax = SyntaxTreeWidget()
        self._semantic = SyntaxTreeWidget()
        self._intermediate = self._make_output("Código intermedio (tres direcciones, etc.).")
        self._symbols = self._make_symbols_table()

        self.addTab(self._tokens, "Tokens")
        self.addTab(self._syntax, "Sintáctico")
        self.addTab(self._semantic, "Semántico")
        self.addTab(self._intermediate, "Intermedio")
        self.addTab(self._symbols, "Símbolos")

        # Connect position changes to error navigation
        self._tokens.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)
        self._syntax.text_widget.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)
        self._semantic.text_widget.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)
        self._intermediate.cursorPositionChanged.connect(self._on_text_widget_cursor_changed)

        # Install pointing hand cursor filter when hovering over error/token lines
        self._tokens_hover_filter = TokenHoverEventFilter(self._tokens)
        self._syntax_hover_filter = ErrorHoverEventFilter(self._syntax.text_widget)
        self._semantic_hover_filter = ErrorHoverEventFilter(self._semantic.text_widget)
        self._intermediate_hover_filter = ErrorHoverEventFilter(self._intermediate)
        self.refresh_theme()

    def set_tokens(self, text: str) -> None:
        self._tokens.setHtml(self._tokens_to_html(text))

    def set_syntax(self, text: str) -> None:
        self._syntax.set_syntax_content(text)

    def set_semantic(self, text: str, error_text: str = "") -> None:
        self._semantic.set_syntax_content(text, error_text)

    def set_intermediate(self, text: str) -> None:
        self._intermediate.setPlainText(text)

    def set_symbols(self, text: str) -> None:
        self._symbols.clearContents()
        if not text:
            self._symbols.setRowCount(0)
            return
        self._symbols.setColumnCount(1)
        self._symbols.setHorizontalHeaderLabels(["Símbolos"])
        lines = [line for line in text.splitlines() if line.strip()]
        self._symbols.setRowCount(len(lines))
        for row, line in enumerate(lines):
            self._symbols.setItem(row, 0, QTableWidgetItem(line))
        self._symbols.resizeColumnsToContents()

    def set_symbol_rows(self, rows: list[list[str]]) -> None:
        headers = ["Nombre", "Tipo", "Dirección/Offset", "Líneas"]
        self._symbols.setColumnCount(len(headers))
        self._symbols.setHorizontalHeaderLabels(headers)
        self._symbols.setRowCount(len(rows))
        for row_index, row_data in enumerate(rows):
            for column_index, value in enumerate(row_data):
                self._symbols.setItem(row_index, column_index, QTableWidgetItem(value))
        self._symbols.resizeColumnsToContents()
        self._symbols.horizontalHeader().setStretchLastSection(True)

    def refresh_theme(self) -> None:
        colors = steins_gate_theme.get_colors()
        self._syntax.refresh_theme()
        self._semantic.refresh_theme()
        palette = self._symbols.palette()
        palette.setColor(QPalette.Base, QColor(colors.background))
        palette.setColor(QPalette.AlternateBase, QColor(colors.panel_bg))
        palette.setColor(QPalette.Text, QColor(colors.foreground))
        palette.setColor(QPalette.Highlight, QColor(colors.selection))
        palette.setColor(QPalette.HighlightedText, QColor(colors.foreground))
        self._symbols.setPalette(palette)
        self._symbols.setStyleSheet(
            f"""
                QTableWidget, QTableWidget::viewport, QAbstractScrollArea::viewport {{
                background-color: {colors.background};
                color: {colors.foreground};
                gridline-color: {colors.border};
                selection-background-color: {colors.selection};
                selection-color: {colors.foreground};
                alternate-background-color: {colors.panel_bg};
            }}
            QTableWidget::item:hover {{
                background-color: {colors.hover};
            }}
            QHeaderView::section {{
                background-color: {colors.panel_bg};
                color: {colors.foreground};
                border: 1px solid {colors.border};
                padding: 5px 8px;
            }}
            """
        )

    def _on_text_widget_cursor_changed(self) -> None:
        widget = self.sender()
        if not isinstance(widget, (QPlainTextEdit, QTextEdit)):
            return

        cursor = widget.textCursor()
        line_text = cursor.block().text().strip()
        if not line_text:
            return

        # --- Error line navigation ---
        match = re.search(r"ERROR_(LEXICO|SINTACTICO|SEMANTICO)\((\d+),\s*(\d+)\)", line_text)
        if match:
            line_no = int(match.group(2))
            col_no = int(match.group(3))

            # Extract lexeme length if present (e.g. -> 'lexeme')
            span_len = 1
            lex_match = re.search(r" -> '(.*)'\ *$", line_text)
            if lex_match:
                span_len = max(1, len(lex_match.group(1)))

            self.error_selected.emit(line_no, col_no, span_len)
            return

        # --- Token line navigation: [TYPE:lexeme] @ line,col ---
        tok_match = re.match(r"^\[([A-Z_]+):(.*)\] @ (\d+),(\d+)$", line_text)
        if tok_match:
            lex = tok_match.group(2)
            line_no = int(tok_match.group(3))
            col_no = int(tok_match.group(4))
            span_len = max(1, len(lex))
            self.error_selected.emit(line_no, col_no, span_len)

    @staticmethod
    def _make_output(text: str) -> QPlainTextEdit:
        output = QPlainTextEdit()
        output.setReadOnly(True)
        output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        output.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        output.setPlainText(text)
        return output

    @staticmethod
    def _make_symbols_table() -> QTableWidget:
        table = QTableWidget(0, 4)
        table.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        table.setHorizontalHeaderLabels(["Nombre", "Tipo", "Dirección/Offset", "Líneas"])
        table.setEditTriggers(QAbstractItemView.NoEditTriggers)
        table.setSelectionBehavior(QAbstractItemView.SelectRows)
        table.setAlternatingRowColors(True)
        table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeToContents)
        table.horizontalHeader().setStretchLastSection(True)
        table.verticalHeader().setVisible(False)
        return table

    @staticmethod
    def _make_rich_output(text: str) -> QTextEdit:
        output = QTextEdit()
        output.setReadOnly(True)
        output.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        output.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
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
