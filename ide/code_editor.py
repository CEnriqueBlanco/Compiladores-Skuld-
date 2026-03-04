from PyQt5.QtCore import QRect, QSize, Qt
from PyQt5.QtGui import QColor, QPainter, QTextCursor, QTextFormat
from PyQt5.QtWidgets import QPlainTextEdit, QTextEdit, QWidget

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
        self.setExtraSelections(extra_selections)
