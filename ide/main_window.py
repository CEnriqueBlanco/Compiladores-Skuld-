from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QStyle,
    QToolBar,
)

from ide.analysis_panel import AnalysisPanel
from ide.code_editor import CodeEditor
from ide.console_panel import ConsolePanel
from ide.file_explorer import FileExplorer


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Reading Steiner IDE v1.0")
        self.resize(1200, 800)

        self._status = QStatusBar(self)
        self._editor: CodeEditor | None = None

        self._build_menu()
        self._build_toolbar()
        self._build_status_bar()
        self._build_layout()

    def _build_menu(self) -> None:
        menu_file = self.menuBar().addMenu("Archivo")
        menu_edit = self.menuBar().addMenu("Editar")
        menu_build = self.menuBar().addMenu("Compilar")
        menu_help = self.menuBar().addMenu("Ayuda")

        for label in ["Nuevo", "Abrir", "Guardar", "Guardar Como", "Salir"]:
            menu_file.addAction(QAction(label, self))

        for label in ["Deshacer", "Rehacer", "Copiar", "Pegar", "Buscar"]:
            menu_edit.addAction(QAction(label, self))

        for label in [
            "Análisis Léxico",
            "Análisis Sintáctico",
            "Análisis Semántico",
            "Código Intermedio",
            "Ejecución",
            "Limpiar",
        ]:
            menu_build.addAction(QAction(label, self))

        for label in ["Documentación", "Acerca de"]:
            menu_help.addAction(QAction(label, self))

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Herramientas", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        toolbar_actions = [
            ("Nuevo", QStyle.SP_FileIcon),
            ("Abrir", QStyle.SP_DirOpenIcon),
            ("Guardar", QStyle.SP_DialogSaveButton),
            ("Léxico", QStyle.SP_FileDialogInfoView),
            ("Sintáctico", QStyle.SP_FileDialogContentsView),
            ("Semántico", QStyle.SP_MessageBoxInformation),
            ("Intermedio", QStyle.SP_ComputerIcon),
            ("Ejecución", QStyle.SP_MediaPlay),
        ]

        for label, standard_icon in toolbar_actions:
            action = QAction(self.style().standardIcon(standard_icon), label, self)
            toolbar.addAction(action)

    def _build_status_bar(self) -> None:
        self._status.showMessage("Lab Member 004 · El Psy Kongroo")
        self.setStatusBar(self._status)

    def _build_layout(self) -> None:
        self._editor = CodeEditor()
        self._editor.setFont(QFont("Consolas", 11))
        self._editor.setPlainText(self._load_example_code())
        self._editor.cursorPositionChanged.connect(self._update_cursor_status)

        file_explorer = FileExplorer()
        analysis_panel = AnalysisPanel()

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(file_explorer)
        top_splitter.addWidget(self._editor)
        top_splitter.addWidget(analysis_panel)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 3)
        top_splitter.setStretchFactor(2, 1)

        console_panel = ConsolePanel()

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(console_panel)
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 1)

        self.setCentralWidget(main_splitter)

    def _load_example_code(self) -> str:
        example_path = Path(__file__).resolve().parent.parent / "examples" / "hello_world.stn"
        if example_path.exists():
            return example_path.read_text(encoding="utf-8")
        return "// Hola mundo Skuld\n\ngate {\n    dmail(\"El Psy Kongroo\");\n}\n"

    def _update_cursor_status(self) -> None:
        if not self._editor:
            return
        cursor = self._editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        self._status.showMessage(f"Lab Member 004 · Línea {line}, Col {column}")
