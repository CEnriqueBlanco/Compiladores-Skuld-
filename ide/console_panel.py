import re
from PyQt5.QtCore import QEvent, QObject, Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QColor, QFont, QTextCursor
from PyQt5.QtWidgets import QPlainTextEdit, QTabWidget

from ide.theme import steins_gate_theme


class InteractiveTerminalWidget(QPlainTextEdit):
    """
    Terminal interactiva directa en el área de texto (como una consola en C / Linux / Windows).
    - El cursor parpadea directamente en la última línea cuando se espera un dato.
    - Se elimina cualquier barra, recuadro inferior o etiqueta 'TM IN'.
    - Al presionar Enter, se envía la línea ingresada al programa.
    """
    input_submitted = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setReadOnly(True)
        self.setLineWrapMode(QPlainTextEdit.WidgetWidth)
        self.setCursorWidth(2)
        font = QFont("Consolas", 10)
        font.setStyleHint(QFont.Monospace)
        self.setFont(font)

        self._waiting_input = False
        self._prompt_pos = 0

    def enable_input(self) -> None:
        """Activa el modo de captura interactiva con cursor parpadeando directamente."""
        self._waiting_input = True
        self.setReadOnly(False)
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText("> ")
        self.setTextCursor(cursor)
        self._prompt_pos = self.textCursor().position()
        self.ensureCursorVisible()
        self.setFocus()

    def disable_input(self) -> None:
        """Desactiva la entrada y vuelve a sólo lectura."""
        self._waiting_input = False
        self.setReadOnly(True)

    def focusOutEvent(self, event) -> None:
        super().focusOutEvent(event)
        if self._waiting_input:
            QTimer.singleShot(0, self._restore_input_focus)

    def _restore_input_focus(self) -> None:
        if self._waiting_input:
            self.setFocus(Qt.OtherFocusReason)
            self.ensureCursorVisible()

    def mousePressEvent(self, event) -> None:
        if self._waiting_input:
            self.moveCursor(QTextCursor.End)
            self.ensureCursorVisible()
            return
        super().mousePressEvent(event)

    def append_text(self, text: str) -> None:
        """Añade texto como salida de la máquina."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        self.insertPlainText(text + "\n")
        self.ensureCursorVisible()

    def write_stream(self, text: str) -> None:
        """Escribe caracteres continuos en tiempo real (para mensajes como 'Teclea un numero: ')."""
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)
        self.insertPlainText(text)
        self.ensureCursorVisible()

    def set_text(self, text: str) -> None:
        self.setPlainText(text)
        self.ensureCursorVisible()

    def keyPressEvent(self, event):
        if not self._waiting_input:
            # Si no estamos esperando entrada, ignorar teclas de escritura
            if event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Backspace, Qt.Key_Delete):
                return
            super().keyPressEvent(event)
            return

        cursor = self.textCursor()
        # Si presiona Enter / Return
        if event.key() in (Qt.Key_Return, Qt.Key_Enter):
            full_text = self.toPlainText()
            user_input = full_text[self._prompt_pos:]
            self.disable_input()
            cursor.movePosition(QTextCursor.End)
            cursor.insertText("\n")
            self.setTextCursor(cursor)
            self.input_submitted.emit(user_input)
            return

        # Evitar borrar texto anterior al prompt
        if event.key() == Qt.Key_Backspace:
            if cursor.position() <= self._prompt_pos:
                return

        if event.key() in (Qt.Key_Left, Qt.Key_Up):
            if cursor.position() <= self._prompt_pos:
                return

        super().keyPressEvent(event)


class ErrorHoverEventFilter(QObject):
    def __init__(self, parent_widget) -> None:
        super().__init__(parent_widget)
        self.widget = parent_widget
        self.widget.setMouseTracking(True)
        self.widget.viewport().setMouseTracking(True)
        self.widget.viewport().installEventFilter(self)
        self._last_cursor_shape = None

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.MouseMove:
            pos = event.pos()
            cursor = self.widget.cursorForPosition(pos)
            line_text = cursor.block().text().strip()

            cursor_shape = (
                Qt.PointingHandCursor
                if re.search(r"ERROR_(LEXICO|SINTACTICO|SEMANTICO)\((\d+),\s*(\d+)\)", line_text)
                else Qt.IBeamCursor
            )
            if cursor_shape != self._last_cursor_shape:
                self.widget.viewport().setCursor(cursor_shape)
                self._last_cursor_shape = cursor_shape
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
        self._last_cursor_shape = None

    def eventFilter(self, obj, event) -> bool:
        if event.type() == QEvent.MouseMove:
            pos = event.pos()
            cursor = self.widget.cursorForPosition(pos)
            line_text = cursor.block().text().strip()
            cursor_shape = (
                Qt.PointingHandCursor
                if self.TOKEN_RE.match(line_text)
                else Qt.IBeamCursor
            )
            if cursor_shape != self._last_cursor_shape:
                self.widget.viewport().setCursor(cursor_shape)
                self._last_cursor_shape = cursor_shape
        return super().eventFilter(obj, event)


class ConsolePanel(QTabWidget):
    error_selected = pyqtSignal(int, int, int)  # line, column, length

    def __init__(self) -> None:
        super().__init__()

        self._console = self._make_output("Bienvenido a Reading Steiner IDE\nEl Psy Kongroo\nListo para compilar...")
        self._errors = self._make_output("Errores léxicos, sintácticos y semánticos aparecerán aquí.")
        self._execution = InteractiveTerminalWidget()

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
        self._execution.append_text(text)

    def set_execution(self, text: str) -> None:
        """Muestra el resultado completo de la última ejecución."""
        self._execution.set_text(text)
        self.setCurrentWidget(self._execution)

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
        self._execution.setStyleSheet(
            f"QPlainTextEdit {{"
            f"background-color: {colors.background};"
            f"color: {colors.foreground};"
            f"border: none;"
            f"selection-background-color: {colors.selection};"
            f"}}"
        )

    def _on_errors_cursor_changed(self) -> None:
        cursor = self._errors.textCursor()
        line_text = cursor.block().text().strip()
        if not line_text:
            return

        match = re.search(r"ERROR_(LEXICO|SINTACTICO|SEMANTICO)\((\d+),\s*(\d+)\)", line_text)
        if match:
            line_no = int(match.group(2))
            col_no = int(match.group(3))

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
