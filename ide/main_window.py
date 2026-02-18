from __future__ import annotations

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import (
    QAction,
    QFileDialog,
    QMessageBox,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QStyle,
    QTabWidget,
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
        self._editor_tabs: QTabWidget | None = None
        self._analysis_panel: AnalysisPanel | None = None
        self._console_panel: ConsolePanel | None = None
        self._file_explorer: FileExplorer | None = None
        self._untitled_counter = 1

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
        action_open_folder = QAction("Abrir Carpeta", self)
        action_close = QAction("Cerrar", self)
        action_save = QAction("Guardar", self)
        action_save_as = QAction("Guardar Como", self)
        action_exit = QAction("Salir", self)

        action_new.triggered.connect(self._new_file)
        action_open.triggered.connect(self._open_file)
        action_open_folder.triggered.connect(self._open_folder)
        action_close.triggered.connect(self._close_file)
        action_save.triggered.connect(self._save_file)
        action_save_as.triggered.connect(self._save_file_as)
        action_exit.triggered.connect(self.close)

        menu_file.addAction(action_new)
        menu_file.addAction(action_open)
        menu_file.addAction(action_open_folder)
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
        self._editor_tabs = QTabWidget()
        self._editor_tabs.setFocusPolicy(Qt.StrongFocus)
        self._editor_tabs.setMinimumWidth(420)
        self._editor_tabs.setTabsClosable(True)
        self._editor_tabs.tabCloseRequested.connect(self._close_tab)
        self._editor_tabs.currentChanged.connect(self._on_tab_changed)

        self._file_explorer = FileExplorer()
        self._file_explorer.file_open_requested.connect(self._open_file_from_explorer)
        self._analysis_panel = AnalysisPanel()

        top_splitter = QSplitter(Qt.Horizontal)
        top_splitter.setChildrenCollapsible(False)
        top_splitter.addWidget(self._file_explorer)
        top_splitter.addWidget(self._editor_tabs)
        top_splitter.addWidget(self._analysis_panel)
        top_splitter.setStretchFactor(0, 1)
        top_splitter.setStretchFactor(1, 3)
        top_splitter.setStretchFactor(2, 1)
        top_splitter.setSizes([250, 700, 250])

        self._console_panel = ConsolePanel()

        main_splitter = QSplitter(Qt.Vertical)
        main_splitter.addWidget(top_splitter)
        main_splitter.addWidget(self._console_panel)
        main_splitter.setStretchFactor(0, 3)
        main_splitter.setStretchFactor(1, 1)
        main_splitter.setSizes([620, 180])

        self.setCentralWidget(main_splitter)
        self._new_file(with_example=True)

    def _load_example_code(self) -> str:
        example_path = Path(__file__).resolve().parent.parent / "examples" / "hello_world.stn"
        if example_path.exists():
            return example_path.read_text(encoding="utf-8")
        return "// Hola mundo Skuld\n\ngate {\n    dmail(\"El Psy Kongroo\");\n}\n"

    def _update_cursor_status(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return
        cursor = editor.textCursor()
        line = cursor.blockNumber() + 1
        column = cursor.columnNumber() + 1
        current_file = self._get_active_file_path()
        file_label = current_file.name if current_file else self._current_tab_title()
        self._status.showMessage(f"Lab Member 004 · {file_label} · Línea {line}, Col {column}")

    def _new_file(self, with_example: bool = False) -> None:
        if self._editor_tabs is None:
            return

        editor = CodeEditor()
        editor.setReadOnly(False)
        editor.setFocusPolicy(Qt.StrongFocus)
        editor.setFont(QFont("Consolas", 11))
        if with_example:
            editor.setPlainText(self._load_example_code())
        editor.cursorPositionChanged.connect(self._update_cursor_status)
        editor.setProperty("file_path", "")

        tab_title = f"Sin título {self._untitled_counter}"
        self._untitled_counter += 1
        tab_index = self._editor_tabs.addTab(editor, tab_title)
        self._editor_tabs.setCurrentIndex(tab_index)

        if self._console_panel is not None:
            self._console_panel.append_console("Nuevo archivo creado.")
        editor.setFocus()
        self._update_cursor_status()

    def _open_file(self) -> None:
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Abrir archivo",
            "",
            "Archivos Skuld (*.stn);;Todos los archivos (*.*)",
        )
        if not file_path:
            return
        self._open_file_path(Path(file_path))

    def _open_folder(self) -> None:
        folder_path = QFileDialog.getExistingDirectory(self, "Seleccionar carpeta")
        if not folder_path:
            return
        if self._file_explorer is not None:
            self._file_explorer.add_root_path(folder_path)
        if self._console_panel is not None:
            self._console_panel.append_console(f"Carpeta agregada: {Path(folder_path).name}")

    def _save_file(self) -> None:
        editor = self._get_active_editor()
        if not editor:
            return
        current_file = self._get_active_file_path()
        if not current_file:
            self._save_file_as()
            return

        current_file.write_text(editor.toPlainText(), encoding="utf-8")
        if self._console_panel is not None:
            self._console_panel.append_console(f"Archivo guardado: {current_file.name}")
        if self._file_explorer is not None:
            self._file_explorer.refresh()

    def _save_file_as(self) -> None:
        editor = self._get_active_editor()
        if not editor:
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
        path.write_text(editor.toPlainText(), encoding="utf-8")
        editor.setProperty("file_path", str(path))

        if self._editor_tabs is not None:
            current_index = self._editor_tabs.currentIndex()
            if current_index >= 0:
                self._editor_tabs.setTabText(current_index, path.name)
                self._editor_tabs.setTabToolTip(current_index, str(path))

        if self._console_panel is not None:
            self._console_panel.append_console(f"Archivo guardado: {path.name}")
        if self._file_explorer is not None:
            self._file_explorer.refresh()
        self._update_cursor_status()

    def _close_file(self) -> None:
        if self._editor_tabs is None:
            return

        current_index = self._editor_tabs.currentIndex()
        if current_index >= 0:
            self._close_tab(current_index)

        if self._console_panel is not None:
            self._console_panel.append_console("Archivo cerrado.")
        self._update_cursor_status()

    def _run_phase(self, phase: str) -> None:
        editor = self._get_active_editor()
        if not editor:
            return

        current_file = self._get_active_file_path()
        if not current_file:
            self._save_file_as()
            current_file = self._get_active_file_path()
            if not current_file:
                return

        self._save_file()
        result = run_compiler(phase, str(current_file))

        if result.returncode != 0:
            if self._console_panel is not None:
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
            if self._console_panel is not None:
                self._console_panel.append_execution(output_text)

        if self._console_panel is not None:
            self._console_panel.append_console(f"Fase ejecutada: {phase}")

    def _open_file_from_explorer(self, file_path: str) -> None:
        if self._console_panel is not None:
            self._console_panel.append_console(f"Solicitud abrir desde explorador: {Path(file_path).name}")
        self._open_file_path(Path(file_path))

    def _open_file_path(self, path: Path) -> None:
        if self._editor_tabs is None:
            return

        if not path.exists() or not path.is_file():
            QMessageBox.warning(
                self,
                "No se puede abrir",
                f"El archivo no existe o no es valido:\n{path}",
            )
            return

        resolved = path.resolve()
        for index in range(self._editor_tabs.count()):
            editor = self._editor_tabs.widget(index)
            if not isinstance(editor, CodeEditor):
                continue
            tab_file_raw = editor.property("file_path")
            if not tab_file_raw:
                continue
            tab_file = Path(str(tab_file_raw)).resolve()
            if tab_file == resolved:
                self._editor_tabs.setCurrentIndex(index)
                if self._console_panel is not None:
                    self._console_panel.append_console(f"Archivo abierto: {path.name}")
                active_editor = self._get_active_editor()
                if active_editor:
                    active_editor.setFocus()
                self._update_cursor_status()
                return

        editor = CodeEditor()
        editor.setReadOnly(False)
        editor.setFocusPolicy(Qt.StrongFocus)
        editor.setFont(QFont("Consolas", 11))
        try:
            editor.setPlainText(path.read_text(encoding="utf-8"))
        except UnicodeDecodeError:
            QMessageBox.warning(
                self,
                "No se puede abrir",
                f"El archivo no esta en UTF-8:\n{path}",
            )
            return
        except OSError as exc:
            QMessageBox.warning(
                self,
                "No se puede abrir",
                f"No fue posible abrir el archivo:\n{path}\n\n{exc}",
            )
            return
        editor.cursorPositionChanged.connect(self._update_cursor_status)
        editor.setProperty("file_path", str(path))

        tab_index = self._editor_tabs.addTab(editor, path.name)
        self._editor_tabs.setTabToolTip(tab_index, str(path))
        self._editor_tabs.setCurrentIndex(tab_index)
        if self._console_panel is not None:
            self._console_panel.append_console(f"Archivo abierto: {path.name}")
        editor.setFocus()
        self._update_cursor_status()

    def _close_tab(self, index: int) -> None:
        if self._editor_tabs is None:
            return
        widget = self._editor_tabs.widget(index)
        self._editor_tabs.removeTab(index)
        if widget:
            widget.deleteLater()
        if self._editor_tabs.count() == 0:
            self._new_file()

    def _on_tab_changed(self, _index: int) -> None:
        editor = self._get_active_editor()
        if editor:
            editor.setReadOnly(False)
            editor.setFocus()
        self._update_cursor_status()

    def _get_active_editor(self) -> CodeEditor | None:
        if self._editor_tabs is None:
            return None
        widget = self._editor_tabs.currentWidget()
        if isinstance(widget, CodeEditor):
            return widget
        return None

    def _get_active_file_path(self) -> Path | None:
        editor = self._get_active_editor()
        if not editor:
            return None
        file_path_raw = editor.property("file_path")
        if not file_path_raw:
            return None
        return Path(str(file_path_raw))

    def _current_tab_title(self) -> str:
        if self._editor_tabs is None:
            return "Sin archivo"
        current_index = self._editor_tabs.currentIndex()
        if current_index < 0:
            return "Sin archivo"
        return self._editor_tabs.tabText(current_index) or "Sin archivo"

    def _clear_outputs(self) -> None:
        if self._analysis_panel is not None:
            self._analysis_panel.set_tokens("")
            self._analysis_panel.set_syntax("")
            self._analysis_panel.set_semantic("")
            self._analysis_panel.set_intermediate("")
            self._analysis_panel.set_symbols("")
        if self._console_panel is not None:
            self._console_panel.clear_all()
