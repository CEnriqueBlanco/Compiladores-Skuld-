import os
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from ide.main_window import MainWindow
from ide.splash_screen import SplashScreen
from ide.theme.steins_gate_theme import build_stylesheet


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Reading Steiner IDE")
    app.setStyleSheet(build_stylesheet())

    icon_path = os.path.join(os.path.dirname(__file__), "..", "resources", "icons", "logo.ico")
    icon_path = os.path.abspath(icon_path)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    splash = SplashScreen()
    main_window = MainWindow()

    splash.show()
    QTimer.singleShot(1200, lambda: (splash.close(), main_window.show()))

    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
