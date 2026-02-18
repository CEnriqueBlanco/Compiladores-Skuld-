import os
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QWidget

from ide.theme.steins_gate_theme import COLORS


class SplashScreen(QWidget):
    def __init__(self) -> None:
        super().__init__(None, Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setFixedSize(640, 400)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet("background: transparent;")

        splash_path = os.path.join(os.path.dirname(__file__), '..', 'resources', 'icons', 'start.png')
        pixmap = QPixmap(splash_path)
        splash_label = QLabel(self)
        if not pixmap.isNull():
            splash_label.setPixmap(pixmap.scaled(self.width(), self.height(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
        splash_label.setAlignment(Qt.AlignCenter)
        splash_label.setGeometry(0, 0, self.width(), self.height())
