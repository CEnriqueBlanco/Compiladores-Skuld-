from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QColor, QPainter, QTextCharFormat, QTextCursor, QTextFormat
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit, QWidget, QCompleter

from ide.skuld_syntax_highlighter import SkuldSyntaxHighlighter
from ide.theme import steins_gate_theme

COMPLETION_KEYWORDS = [
    "and", "bool", "case", "choice", "cin", "cout", "divergence", "dmail", "do",
    "else", "end", "false", "float", "fork", "gate", "if", "int", "jump",
    "labmem", "loop", "main", "not", "or", "path", "pulse", "read", "reading",
    "real", "return", "seal", "shift", "sphone", "steiner", "string", "switch",
    "then", "true", "until", "void", "while", "worldline", "write"
]


class LineNumberArea(QWidget):
    def __init__(self, editor: "CodeEditor") -> None:
        super().__init__(editor)
        self.editor = editor

    def sizeHint(self) -> QSize:  # type: ignore[override]
        return QSize(self.editor.line_number_area_width(), 0)

    def paintEvent(self, event) -> None:  # type: ignore[override]
        self.editor.line_number_area_paint_event(event)


class CodeEditor(QPlainTextEdit):
    def __init__(self) -> None:
        super().__init__()
        self._line_number_area = LineNumberArea(self)
        self._search_selections: list[QTextEdit.ExtraSelection] = []
        self._error_selections: list[QTextEdit.ExtraSelection] = []
        self._syntax_highlighter = SkuldSyntaxHighlighter(self.document())
        self._selection_lexical_callback = None

        self.blockCountChanged.connect(self.update_line_number_area_width)
        self.updateRequest.connect(self.update_line_number_area)
        self.cursorPositionChanged.connect(self.highlight_current_line)

        self.update_line_number_area_width(0)
        self.highlight_current_line()
        self.setLineWrapMode(QPlainTextEdit.NoWrap)

        # Configurar Autocompletado (QCompleter)
        self._completer = QCompleter(COMPLETION_KEYWORDS, self)
        self._completer.setWidget(self)
        self._completer.setCompletionMode(QCompleter.PopupCompletion)
        self._completer.setCaseSensitivity(Qt.CaseInsensitive)
        self._completer.activated.connect(self.insert_completion)

        popup = self._completer.popup()
        popup.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def text_under_cursor(self) -> str:
        tc = self.textCursor()
        block_text = tc.block().text()
        pos_in_block = tc.positionInBlock()
        
        start = pos_in_block
        while start > 0 and (block_text[start - 1].isalnum() or block_text[start - 1] == '_'):
            start -= 1
        return block_text[start:pos_in_block]

    def insert_completion(self, completion: str) -> None:
        if self._completer.widget() is not self:
            return
        tc = self.textCursor()
        prefix = self._completer.completionPrefix()
        tc.movePosition(QTextCursor.Left, QTextCursor.KeepAnchor, len(prefix))
        tc.insertText(completion)
        self.setTextCursor(tc)

    def keyPressEvent(self, event) -> None:  # type: ignore[override]
        if self._completer and self._completer.popup().isVisible():
            if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab, Qt.Key_Escape):
                if event.key() in (Qt.Key_Enter, Qt.Key_Return, Qt.Key_Tab):
                    current_index = self._completer.popup().currentIndex()
                    completion_text = ""
                    if current_index.isValid():
                        completion_text = self._completer.popup().model().data(current_index, Qt.DisplayRole)
                    if not completion_text:
                        completion_text = self._completer.currentCompletion()
                    
                    if completion_text:
                        self.insert_completion(completion_text)
                    self._completer.popup().hide()
                    event.accept()
                    return
                elif event.key() == Qt.Key_Escape:
                    self._completer.popup().hide()
                    event.accept()
                    return

        super().keyPressEvent(event)

        if not self._completer:
            return

        has_modifier = (event.modifiers() != Qt.NoModifier) and (event.modifiers() != Qt.ShiftModifier)
        if has_modifier:
            self._completer.popup().hide()
            return

        completion_prefix = self.text_under_cursor()

        if not completion_prefix or not event.text():
            self._completer.popup().hide()
            return

        last_char = event.text()[-1]
        if not (last_char.isalnum() or last_char == '_'):
            self._completer.popup().hide()
            return

        self._completer.setCompletionPrefix(completion_prefix)
        cr = self.cursorRect()
        popup_width = self._completer.popup().sizeHintForColumn(0) + self._completer.popup().verticalScrollBar().sizeHint().width()
        cr.setWidth(max(150, popup_width))
        self._completer.complete(cr)

        # Seleccionar automáticamente la primera opción de la lista filtrada
        first_index = self._completer.completionModel().index(0, 0)
        if first_index.isValid():
            self._completer.popup().setCurrentIndex(first_index)

    def line_number_area_width(self) -> int:
        digits = max(1, len(str(self.blockCount())))
        space = 6 + self.fontMetrics().horizontalAdvance("9") * digits
        return space

    def update_line_number_area_width(self, _block_count: int) -> None:
        self.setViewportMargins(self.line_number_area_width(), 0, 0, 0)

    def update_line_number_area(self, rect: QRect, dy: int) -> None:
        if dy:
            self._line_number_area.scroll(0, dy)
        else:
            self._line_number_area.update(0, rect.y(), self._line_number_area.width(), rect.height())

        if rect.contains(self.viewport().rect()):
            self.update_line_number_area_width(0)

    def resizeEvent(self, event) -> None:  # type: ignore[override]
        super().resizeEvent(event)
        cr = self.contentsRect()
        self._line_number_area.setGeometry(QRect(cr.left(), cr.top(), self.line_number_area_width(), cr.height()))

    def line_number_area_paint_event(self, event) -> None:
        colors = steins_gate_theme.get_colors()
        painter = QPainter(self._line_number_area)
        painter.fillRect(event.rect(), QColor(colors.panel_bg))

        block = self.firstVisibleBlock()
        block_number = block.blockNumber()
        top = int(self.blockBoundingGeometry(block).translated(self.contentOffset()).top())
        bottom = top + int(self.blockBoundingRect(block).height())

        while block.isValid() and top <= event.rect().bottom():
            if block.isVisible() and bottom >= event.rect().top():
                number = str(block_number + 1)
                block_height = int(self.blockBoundingRect(block).height())
                painter.setPen(QColor(colors.comments))
                painter.drawText(
                    0,
                    top,
                    self._line_number_area.width() - 4,
                    block_height,
                    Qt.AlignRight | Qt.AlignVCenter,
                    number,
                )

            block = block.next()
            top = bottom
            bottom = top + int(self.blockBoundingRect(block).height())
            block_number += 1

    def highlight_current_line(self) -> None:
        self._apply_extra_selections()

    def set_search_highlights(self, text: str) -> None:
        self._search_selections = []
        query = text.strip()
        if not query:
            self._apply_extra_selections()
            return

        colors = steins_gate_theme.get_colors()
        cursor = self.document().find(query)
        while not cursor.isNull():
            selection = QTextEdit.ExtraSelection()
            selection.cursor = cursor
            selection.format.setBackground(QColor(colors.hover))
            selection.format.setForeground(QColor(colors.foreground))
            self._search_selections.append(selection)
            start_position = cursor.selectionEnd()
            cursor = self.document().find(query, start_position)

        self._apply_extra_selections()

    def _apply_extra_selections(self) -> None:
        colors = steins_gate_theme.get_colors()
        extra_selections = []
        if not self.isReadOnly():
            selection = QTextEdit.ExtraSelection()
            selection.format.setBackground(QColor(colors.selection))
            selection.format.setProperty(QTextFormat.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            extra_selections.append(selection)
        extra_selections.extend(self._search_selections)
        extra_selections.extend(self._error_selections)
        self.setExtraSelections(extra_selections)

    def refresh_syntax_theme(self) -> None:
        self._syntax_highlighter.refresh_theme()

    def set_selection_lexical_callback(self, callback) -> None:
        self._selection_lexical_callback = callback

    def contextMenuEvent(self, event) -> None:  # type: ignore[override]
        menu = self.createStandardContextMenu()
        menu.addSeparator()
        lex_action = menu.addAction("Analisis lexico (seleccion)")
        selection_text = self.textCursor().selectedText()
        has_selection = bool(selection_text.strip())
        lex_action.setEnabled(has_selection and self._selection_lexical_callback is not None)

        if self._selection_lexical_callback is not None:
            lex_action.triggered.connect(
                lambda _checked=False, txt=selection_text: self._selection_lexical_callback(txt)
            )

        menu.exec_(event.globalPos())

    def clear_error_highlights(self) -> None:
        self._error_selections = []
        self._apply_extra_selections()

    def highlight_error_range(self, line: int, column_start: int, column_end: int | None = None, apply_immediate: bool = True) -> None:
        block = self.document().findBlockByNumber(max(0, line - 1))
        if not block.isValid():
            return

        line_start = block.position()
        start_col_zero = max(0, column_start - 1)
        # column_end is treated as 1-based inclusive, then converted to zero-based exclusive.
        end_col_exclusive = max(start_col_zero + 1, column_end if column_end is not None else start_col_zero + 1)

        start_pos = line_start + start_col_zero
        end_pos = min(line_start + len(block.text()), line_start + end_col_exclusive)
        if end_pos <= start_pos:
            end_pos = min(line_start + len(block.text()), start_pos + 1)

        selection = QTextEdit.ExtraSelection()
        cursor = QTextCursor(self.document())
        cursor.setPosition(start_pos)
        cursor.setPosition(end_pos, QTextCursor.KeepAnchor)
        selection.cursor = cursor

        error_colors = steins_gate_theme.get_error_colors()
        error_underline = QColor(error_colors.underline)
        error_background = QColor(error_colors.background)
        error_background.setAlpha(140)
        selection.format.setUnderlineStyle(QTextCharFormat.WaveUnderline)
        selection.format.setUnderlineColor(error_underline)
        selection.format.setBackground(error_background)
        selection.format.setForeground(QColor(error_colors.text))

        self._error_selections.append(selection)
        
        if apply_immediate:
            self._apply_extra_selections()
            self.setTextCursor(cursor)
            self.centerCursor()
