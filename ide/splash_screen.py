from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from ide.theme.steins_gate_theme import COLORS


class SplashScreen(QWidget):
    def __init__(self) -> None:
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(520, 300)
        self.setStyleSheet(
            f"background-color: {COLORS.background}; color: {COLORS.foreground};"
            f"border: 2px solid {COLORS.accent};"
        )

        layout = QVBoxLayout(self)
        title = QLabel("Reading Steiner")
        title.setAlignment(Qt.AlignCenter)
        title.setFont(QFont("Consolas", 28, QFont.Bold))

        subtitle = QLabel("El Psy Kongroo")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setFont(QFont("Consolas", 14))

        footer = QLabel("Lab Member 004")
        footer.setAlignment(Qt.AlignCenter)
        footer.setFont(QFont("Consolas", 11))

        layout.addStretch(1)
        layout.addWidget(title)
        layout.addWidget(subtitle)
        layout.addStretch(1)
        layout.addWidget(footer)
