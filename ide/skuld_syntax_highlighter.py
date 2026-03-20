from __future__ import annotations

import re
from typing import List, Tuple

from PyQt5.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter

from skuld_lexer import KEYWORDS, WORD_LOGIC_TO_OPERATOR
from ide.theme import steins_gate_theme


class SkuldSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)
        self._rules: List[Tuple[re.Pattern[str], QTextCharFormat]] = []
        self._line_comment_re = re.compile(r"//[^\n]*|<>[^\n]*|<[^>\n]*>")
        self._block_start_re = re.compile(r"/\*")
        self._block_end_re = re.compile(r"\*/")
        self._angle_start_re = re.compile(r"^\s*<(?!=|>)")
        self._angle_end_re = re.compile(r">")
        self._build_rules()

    def _build_rules(self) -> None:
        colors = steins_gate_theme.get_colors()

        keyword_fmt = self._fmt(colors.keywords)
        string_fmt = self._fmt(colors.strings)
        comment_fmt = self._fmt(colors.comments)
        number_fmt = self._fmt(colors.numbers)
        operator_fmt = self._fmt(colors.operators)

        keywords = sorted(KEYWORDS.keys(), key=len, reverse=True)
        logic_words = sorted(WORD_LOGIC_TO_OPERATOR.keys(), key=len, reverse=True)

        self._rules = []

        for kw in keywords:
            self._rules.append((re.compile(rf"\b{kw}\b"), keyword_fmt))

        for opw in logic_words:
            self._rules.append((re.compile(rf"\b{opw}\b"), operator_fmt))

        self._rules.extend(
            [
                (re.compile(r'"([^"\\]|\\["\\nrt])*"'), string_fmt),
                (re.compile(r"([0-9]+\.[0-9]+)([eE][+-]?[0-9]+)?"), number_fmt),
                (re.compile(r"\b(0|[1-9][0-9]*)\b"), number_fmt),
                (re.compile(r"==|!=|<=|>=|\+\+|--|\+=|-=|\*=|/=|%=|&&|\|\|"), operator_fmt),
                (re.compile(r"[=+*/%<>!(){}\[\];,.:-]"), operator_fmt),
                (self._line_comment_re, comment_fmt),
            ]
        )

        self._block_comment_format = comment_fmt

    def refresh_theme(self) -> None:
        self._build_rules()
        self.rehighlight()

    def highlightBlock(self, text: str) -> None:  # type: ignore[override]
        for pattern, fmt in self._rules:
            for match in pattern.finditer(text):
                start, end = match.span()
                self.setFormat(start, end - start, fmt)

        self.setCurrentBlockState(0)

        if self.previousBlockState() == 2:
            self._apply_multiline_comment(text, 0, self._angle_end_re, 2)
            if self.currentBlockState() == 2:
                return
        elif self._try_start_angle_comment(text):
            return

        start_index = 0
        if self.previousBlockState() != 1:
            start_match = self._block_start_re.search(text)
            start_index = start_match.start() if start_match else -1
        else:
            start_index = 0

        while start_index >= 0:
            end_match = self._block_end_re.search(text, start_index)
            if end_match is None:
                self.setCurrentBlockState(1)
                comment_length = len(text) - start_index
            else:
                comment_length = end_match.end() - start_index

            self.setFormat(start_index, comment_length, self._block_comment_format)

            if end_match is None:
                break

            next_match = self._block_start_re.search(text, start_index + comment_length)
            start_index = next_match.start() if next_match else -1

    def _try_start_angle_comment(self, text: str) -> bool:
        start_match = self._angle_start_re.search(text)
        if start_match is None:
            return False

        start_index = start_match.start() + text[start_match.start() : start_match.end()].rfind("<")
        self._apply_multiline_comment(text, start_index, self._angle_end_re, 2)
        return self.currentBlockState() == 2 or start_index >= 0

    def _apply_multiline_comment(self, text: str, start_index: int, end_re: re.Pattern[str], state_id: int) -> None:
        end_match = end_re.search(text, start_index + 1)
        if end_match is None:
            self.setCurrentBlockState(state_id)
            comment_length = len(text) - start_index
        else:
            comment_length = end_match.end() - start_index

        self.setFormat(start_index, comment_length, self._block_comment_format)

    @staticmethod
    def _fmt(color_hex: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))
        return fmt
