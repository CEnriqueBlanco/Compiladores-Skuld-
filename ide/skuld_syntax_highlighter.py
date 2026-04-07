from __future__ import annotations

import re
from typing import List, Tuple

from PyQt5.QtGui import QColor, QTextCharFormat, QSyntaxHighlighter

from analizadores.analisis_lexico.skuld_lexer import KEYWORDS, WORD_LOGIC_TO_OPERATOR
from ide.theme import steins_gate_theme


class SkuldSyntaxHighlighter(QSyntaxHighlighter):
    def __init__(self, document) -> None:
        super().__init__(document)
        self._rules: List[Tuple[re.Pattern[str], QTextCharFormat]] = []
        self._line_comment_re = re.compile(r"<>[^\n]*")
        self._block_start_re = re.compile(r"<!")
        self._block_end_re = re.compile(r"!>")
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

        search_index = 0
        if self.previousBlockState() == 1:
            end_match = self._block_end_re.search(text)
            if end_match is None:
                self.setCurrentBlockState(1)
                self.setFormat(0, len(text), self._block_comment_format)
                return

            self.setFormat(0, end_match.end(), self._block_comment_format)
            search_index = end_match.end()

        while True:
            start_match = self._block_start_re.search(text, search_index)
            if start_match is None:
                break

            end_match = self._block_end_re.search(text, start_match.end())
            if end_match is None:
                self.setCurrentBlockState(1)
                self.setFormat(start_match.start(), len(text) - start_match.start(), self._block_comment_format)
                break

            self.setFormat(start_match.start(), end_match.end() - start_match.start(), self._block_comment_format)
            search_index = end_match.end()

    @staticmethod
    def _fmt(color_hex: str) -> QTextCharFormat:
        fmt = QTextCharFormat()
        fmt.setForeground(QColor(color_hex))
        return fmt
