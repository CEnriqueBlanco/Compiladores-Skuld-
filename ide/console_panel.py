import re

from PyQt5.QtCore import QEvent, QObject, Qt, pyqtSignal
from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget

from ide.theme import steins_gate_theme


class ErrorHoverEventFilter(QObject):
    def __init__(self, parent_widget) -> None:
        super().__init__(parent_widget)
        self.widget = parent_widget
        self.widget.setMouseTracking(True)
        self.widget.viewport().setMouseTracking(True)
        self.widget.viewport().installEventFilter(self)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.MouseMove:
            pos = event.pos()
            cursor = self.widget.cursorForPosition(pos)
            line_text = cursor.block().text().strip()
            
            import re
            if re.search(r"ERROR_(LEXICO|SINTACTICO|SEMANTICO)\((\d+),\s*(\d+)\)", line_text):
                self.widget.viewport().setCursor(Qt.PointingHandCursor)
            else:
                self.widget.viewport().setCursor(Qt.IBeamCursor)
        return super().eventFilter(obj, event)


class TokenHoverEventFilter(QObject):
    """Shows a pointing-hand cursor when hovering over any token line."""

    TOKEN_RE = re.compile(r"^\s*\[[A-Z_]+:.*\] @ \d+,\d+")

    def __init__(self, parent_widget) -> None:
        super().__init__(parent_widget)
        self.widget = parent_widget
        self.widget.setMouseTracking(True)
        self.widget.viewport().setMouseTracking(True)
        self.widget.viewport().installEventFilter(self)

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.MouseMove:
            pos = event.pos()
            cursor = self.widget.cursorForPosition(pos)
            line_text = cursor.block().text().strip()
            if self.TOKEN_RE.match(line_text):
                self.widget.viewport().setCursor(Qt.PointingHandCursor)
            else:
                self.widget.viewport().setCursor(Qt.IBeamCursor)
        return super().eventFilter(obj, event)


class ConsolePanel(QTabWidget):
    error_selected = pyqtSignal(int, int, int)  # line, column, length

    def __init__(self) -> None:
        super().__init__()

        self._console = self._make_output("Bienvenido a Reading Steiner IDE\nEl Psy Kongroo\nListo para compilar...")
        self._errors = self._make_output("Errores léxicos, sintácticos y semánticos aparecerán aquí.")
        self._execution = self._make_output("Salida de ejecución del programa compilado.")

        self.addTab(self._console, "Consola")
        self.addTab(self._errors, "Errores")
        self.addTab(self._execution, "Ejecución")
        self.refresh_theme()

        self._errors.cursorPositionChanged.connect(self._on_errors_cursor_changed)
        self._errors_hover_filter = ErrorHoverEventFilter(self._errors)

    def append_console(self, text: str) -> None:
        self._console.appendPlainText(text)

    def append_errors(self, text: str) -> None:
        self._errors.appendPlainText(text)

    def append_execution(self, text: str) -> None:
        self._execution.appendPlainText(text)

    def clear_all(self) -> None:
        self._console.clear()
        self._errors.clear()
        self._execution.clear()

    def refresh_theme(self) -> None:
        colors = steins_gate_theme.get_colors()
        error_colors = steins_gate_theme.get_error_colors()

        self._errors.setStyleSheet(
            f"QPlainTextEdit {{"
            f"background-color: {colors.background};"
            f"color: {error_colors.text};"
            f"border: 1px solid {error_colors.border};"
            f"selection-background-color: {colors.selection};"
            f"}}"
        )

    def _on_errors_cursor_changed(self) -> None:
        cursor = self._errors.textCursor()
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
