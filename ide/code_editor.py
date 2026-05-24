from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QColor, QPainter, QTextCharFormat, QTextCursor, QTextFormat
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

from ide.skuld_syntax_highlighter import SkuldSyntaxHighlighter
from ide.theme import steins_gate_theme


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
