import os
import sys

from PyQt5.QtCore import QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from ide.main_window import MainWindow
from ide.splash_screen import SplashScreen
from ide.theme.steins_gate_theme import build_stylesheet


def _resource_path(*parts: str) -> str:
    if getattr(sys, "frozen", False):
        base_path = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    return os.path.join(base_path, *parts)


def main() -> int:
    app = QApplication(sys.argv)
    app.setApplicationName("Reading Steiner IDE")
    app.setStyleSheet(build_stylesheet())

    taskbar_icon_path = _resource_path("resources", "icons", "start.png")
    if os.path.exists(taskbar_icon_path):
        app.setWindowIcon(QIcon(taskbar_icon_path))

    splash = SplashScreen()
    main_window = MainWindow()

    window_icon_path = _resource_path("resources", "icons", "icon.ico")
    if os.path.exists(window_icon_path):
        main_window.setWindowIcon(QIcon(window_icon_path))

    splash.show()
    QTimer.singleShot(1200, lambda: (splash.close(), main_window.showMaximized()))

    return app.exec_()


if __name__ == "__main__":
    raise SystemExit(main())
