from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QStyle,
    QToolBar,
)

from ide.analysis_panel import AnalysisPanel
from ide.code_editor import CodeEditor
from ide.compiler_runner import run_compiler
from ide.console_panel import ConsolePanel
from ide.file_explorer import FileExplorer


class MainWindow(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Reading Steiner IDE v1.0")
        self.resize(1200, 800)

        self._status = QStatusBar(self)
        self._editor: CodeEditor | None = None
        self._analysis_panel: AnalysisPanel | None = None
        self._console_panel: ConsolePanel | None = None
        self._current_file: Path | None = None

        self._build_menu()
        self._build_toolbar()
        self._build_status_bar()
        self._build_layout()

    def _build_menu(self) -> None:
        menu_file = self.menuBar().addMenu("Archivo")
        menu_edit = self.menuBar().addMenu("Editar")
        menu_build = self.menuBar().addMenu("Compilar")
        menu_help = self.menuBar().addMenu("Ayuda")

        action_new = QAction("Nuevo", self)
        action_open = QAction("Abrir", self)
        action_close = QAction("Cerrar", self)
        action_save = QAction("Guardar", self)
        action_save_as = QAction("Guardar Como", self)
        action_exit = QAction("Salir", self)

        action_new.triggered.connect(self._new_file)
        action_open.triggered.connect(self._open_file)
        action_close.triggered.connect(self._close_file)
        action_save.triggered.connect(self._save_file)
        action_save_as.triggered.connect(self._save_file_as)
        action_exit.triggered.connect(self.close)

        menu_file.addAction(action_new)
        menu_file.addAction(action_open)
        menu_file.addAction(action_close)
        menu_file.addSeparator()
        menu_file.addAction(action_save)
        menu_file.addAction(action_save_as)
        menu_file.addSeparator()
        menu_file.addAction(action_exit)

        for label in ["Deshacer", "Rehacer", "Copiar", "Pegar", "Buscar"]:
            menu_edit.addAction(QAction(label, self))

        action_lex = QAction("Análisis Léxico", self)
        action_syn = QAction("Análisis Sintáctico", self)
        action_sem = QAction("Análisis Semántico", self)
        action_inter = QAction("Código Intermedio", self)
        action_exec = QAction("Ejecución", self)
        action_clear = QAction("Limpiar", self)

        action_lex.triggered.connect(lambda: self._run_phase("lexico"))
        action_syn.triggered.connect(lambda: self._run_phase("sintactico"))
        action_sem.triggered.connect(lambda: self._run_phase("semantico"))
        action_inter.triggered.connect(lambda: self._run_phase("intermedio"))
        action_exec.triggered.connect(lambda: self._run_phase("ejecucion"))
        action_clear.triggered.connect(self._clear_outputs)

        menu_build.addAction(action_lex)
        menu_build.addAction(action_syn)
        menu_build.addAction(action_sem)
        menu_build.addAction(action_inter)
        menu_build.addAction(action_exec)
        menu_build.addSeparator()
        menu_build.addAction(action_clear)

        for label in ["Documentación", "Acerca de"]:
            menu_help.addAction(QAction(label, self))

    def _build_toolbar(self) -> None:
        toolbar = QToolBar("Herramientas", self)
        toolbar.setMovable(False)
        self.addToolBar(Qt.TopToolBarArea, toolbar)

        action_new = QAction(self.style().standardIcon(QStyle.SP_FileIcon), "Nuevo", self)
        action_open = QAction(self.style().standardIcon(QStyle.SP_DirOpenIcon), "Abrir", self)
        action_save = QAction(self.style().standardIcon(QStyle.SP_DialogSaveButton), "Guardar", self)
        action_lex = QAction(self.style().standardIcon(QStyle.SP_FileDialogInfoView), "Léxico", self)
        action_syn = QAction(self.style().standardIcon(QStyle.SP_FileDialogContentsView), "Sintáctico", self)
        action_sem = QAction(self.style().standardIcon(QStyle.SP_MessageBoxInformation), "Semántico", self)
        action_inter = QAction(self.style().standardIcon(QStyle.SP_ComputerIcon), "Intermedio", self)
        action_exec = QAction(self.style().standardIcon(QStyle.SP_MediaPlay), "Ejecución", self)

        action_new.triggered.connect(self._new_file)
        action_open.triggered.connect(self._open_file)
        action_save.triggered.connect(self._save_file)
        action_lex.triggered.connect(lambda: self._run_phase("lexico"))
        action_syn.triggered.connect(lambda: self._run_phase("sintactico"))
        action_sem.triggered.connect(lambda: self._run_phase("semantico"))
        action_inter.triggered.connect(lambda: self._run_phase("intermedio"))
        action_exec.triggered.connect(lambda: self._run_phase("ejecucion"))

        toolbar.addAction(action_new)
        toolbar.addAction(action_open)
        toolbar.addAction(action_save)
        toolbar.addSeparator()
        toolbar.addAction(action_lex)
        toolbar.addAction(action_syn)
        toolbar.addAction(action_sem)
        toolbar.addAction(action_inter)
        toolbar.addAction(action_exec)

    def _build_status_bar(self) -> None:
        self._status.showMessage("Lab Member 004 · El Psy Kongroo")
        self.setStatusBar(self._status)

    def _build_layout(self) -> None:
        self._editor = CodeEditor()
        self._editor.setFont(QFont("Consolas", 11))
        self._editor.setPlainText(self._load_example_code())
        self._editor.cursorPositionChanged.connect(self._update_cursor_status)

        file_explorer = FileExplorer()
        self._analysis_panel = AnalysisPanel()

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.addWidget(file_explorer)
        top_splitter.addWidget(self._editor)
        top_splitter.addWidget(self._analysis_panel)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 3)
        top_splitter.setStretchFactor(2, 1)

        self._console_panel = ConsolePanel()

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self._console_panel)
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
        file_label = self._current_file.name if self._current_file else "Sin archivo"
        self._status.showMessage(f"Lab Member 004 · {file_label} · Línea {line}, Col {column}")

    def _new_file(self) -> None:
        if not self._editor:
            return
        self._editor.clear()
        self._current_file = None
        self._console_panel.append_console("Nuevo archivo creado.")
        self._update_cursor_status()

    def _open_file(self) -> None:
        if not self._editor:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo",
            "",
            "Archivos Skuld (*.stn);;Todos los archivos (*.*)",
        )
        if not file_path:
            return
        path = Path(file_path)
        self._editor.setPlainText(path.read_text(encoding="utf-8"))
        self._current_file = path
        self._console_panel.append_console(f"Archivo abierto: {path.name}")
        self._update_cursor_status()

    def _save_file(self) -> None:
        if not self._editor:
            return
        if not self._current_file:
            self._save_file_as()
            return
        self._current_file.write_text(self._editor.toPlainText(), encoding="utf-8")
        self._console_panel.append_console(f"Archivo guardado: {self._current_file.name}")

    def _save_file_as(self) -> None:
        if not self._editor:
            return
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar archivo",
            "",
            "Archivos Skuld (*.stn);;Todos los archivos (*.*)",
        )
        if not file_path:
            return
        path = Path(file_path)
        path.write_text(self._editor.toPlainText(), encoding="utf-8")
        self._current_file = path
        self._console_panel.append_console(f"Archivo guardado: {path.name}")
        self._update_cursor_status()

    def _close_file(self) -> None:
        if not self._editor:
            return
        self._editor.clear()
        self._current_file = None
        self._console_panel.append_console("Archivo cerrado.")
        self._update_cursor_status()

    def _run_phase(self, phase: str) -> None:
        if not self._editor:
            return
        if not self._current_file:
            self._save_file_as()
            if not self._current_file:
                return

        self._save_file()
        result = run_compiler(phase, str(self._current_file))

        if result.returncode != 0:
            self._console_panel.append_errors(result.stderr or "Error ejecutando el compilador.")
            return

        output_text = result.stdout or "(sin salida)"
        if phase == "lexico":
            self._analysis_panel.set_tokens(output_text)
        elif phase == "sintactico":
            self._analysis_panel.set_syntax(output_text)
        elif phase == "semantico":
            self._analysis_panel.set_semantic(output_text)
        elif phase == "intermedio":
            self._analysis_panel.set_intermediate(output_text)
        elif phase == "ejecucion":
            self._console_panel.append_execution(output_text)

        self._console_panel.append_console(f"Fase ejecutada: {phase}")

    def _clear_outputs(self) -> None:
        if self._analysis_panel:
            self._analysis_panel.set_tokens("")
            self._analysis_panel.set_syntax("")
            self._analysis_panel.set_semantic("")
            self._analysis_panel.set_intermediate("")
            self._analysis_panel.set_symbols("")
        if self._console_panel:
            self._console_panel.clear_all()
